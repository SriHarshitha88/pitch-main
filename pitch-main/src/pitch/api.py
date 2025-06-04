from fastapi import FastAPI, File, UploadFile, WebSocket, BackgroundTasks, Form, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
import uuid
import os
from typing import Dict, Optional, List
import aiofiles
import asyncio
from datetime import datetime, timedelta
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext

from .crew import Pitch
from .status_manager import status_manager
from .tools.vector_store import VectorStore

app = FastAPI(title="Pitch Deck Analyzer")

# Mount static files first
app.mount("/static", StaticFiles(directory="src/pitch/static"), name="static")

# Add CORS middleware with specific origins
origins = [
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    "http://0.0.0.0:8000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


SECRET_KEY = "your-secret-key"  
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


fake_users_db = {
    "johndoe": {
        "username": "johndoe",
        "full_name": "John Doe",
        "email": "johndoe@example.com",
        "hashed_password": pwd_context.hash("secret"),
        "disabled": False,
    }
}

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_user(db, username: str):
    if username in db:
        user_dict = db[username]
        return user_dict

def authenticate_user(fake_db, username: str, password: str):
    user = get_user(fake_db, username)
    if not user:
        return False
    if not verify_password(password, user["hashed_password"]):
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

@app.get("/")
async def home():
    """Serve the home page"""
    return FileResponse("src/pitch/static/index.html")

@app.post("/analyze")
async def analyze(
    background_tasks: BackgroundTasks,
    startup_name: str = Form(...),
    files: list[UploadFile] = File(...)
):
    """Handle file uploads and start analysis"""
    try:
        # Generate unique job ID
        job_id = str(uuid.uuid4())
        
        # Save uploaded files and collect paths
        file_paths = []
        try:
            for file in files:
                file_path = await save_upload_file(file)
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"Failed to save file {file.filename}")
                file_paths.append(file_path)
                
                # Store in vector database
                async with aiofiles.open(file_path, 'r') as f:
                    content = await f.read()
                metadata = {
                    "filename": file.filename,
                    "startup_name": startup_name,
                    "upload_date": datetime.now().isoformat(),
                    "type": "deck"
                }
                await vector_store.store_pitch_deck(content, metadata)
                
        except Exception as upload_error:
            return JSONResponse({
                "status": "error",
                "message": f"Error uploading files: {str(upload_error)}"
            }, status_code=400)

        # Validate files
        if not file_paths:
            return JSONResponse({
                "status": "error",
                "message": "No files were uploaded"
            }, status_code=400)

        # Start analysis in background
        background_tasks.add_task(
            analyze_pitch_deck,
            job_id=job_id,
            file_paths=file_paths,
            startup_name=startup_name
        )
        
        # Return success response with WebSocket connection details
        return JSONResponse({
            "status": "started",
            "job_id": job_id,
            "message": "Analysis started successfully",
            "websocket_url": f"/ws/{job_id}"
        })
    except Exception as e:
        # Log the error and return error response
        print(f"Error in /analyze endpoint: {str(e)}")
        return JSONResponse({
            "status": "error",
            "message": f"Internal server error: {str(e)}"
        }, status_code=500)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

async def save_upload_file(upload_file: UploadFile) -> str:
    """Save uploaded file and return the path"""
    # Get absolute path
    abs_upload_dir = os.path.abspath(UPLOAD_DIR)
    file_path = os.path.join(abs_upload_dir, f"{uuid.uuid4()}_{upload_file.filename}")
    async with aiofiles.open(file_path, 'wb') as out_file:
        content = await upload_file.read()
        await out_file.write(content)
    return file_path

async def analyze_pitch_deck(job_id: str, file_paths: list[str], startup_name: str):
    """Background task to analyze the pitch deck and additional files"""
    try:
        # Initialize status
        await status_manager.broadcast_status(job_id, {
            "status": "started",
            "type": "task_started",
            "message": f"Starting analysis of {len(file_paths)} document(s)",
            "timestamp": datetime.now().isoformat()
        })

        # Validate and organize files
        valid_files = []
        invalid_files = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                invalid_files.append(f"File not found: {os.path.basename(file_path)}")
                continue
                
            ext = os.path.splitext(file_path.lower())[1]
            if ext not in ['.pdf', '.ppt', '.pptx']:
                invalid_files.append(f"Unsupported format for {os.path.basename(file_path)}")
                continue
                
            valid_files.append(file_path)

        if not valid_files:
            raise ValueError("No valid files to analyze.\n" + "\n".join(invalid_files))

        if invalid_files:
            await status_manager.broadcast_status(job_id, {
                "status": "warning",
                "type": "validation_warning",
                "message": "Some files were skipped:\n" + "\n".join(invalid_files),
                "timestamp": datetime.now().isoformat()
            })

        # Initialize crew
        pitch_crew = Pitch()
        
        print(f"\nStarting analysis with:")
        print(f"- Valid files ({len(valid_files)}):")
        for file in valid_files:
            print(f"  - {os.path.basename(file)}")
        print(f"- Startup name: {startup_name}")
        
        # Prepare inputs for the crew
        inputs = {
            'file_paths': ", ".join(valid_files),  # Convert list to comma-separated string for template
            'startup_name': startup_name,
            'current_year': str(datetime.now().year),
            'job_id': job_id,
            'total_files': len(valid_files)
        }

        try:
            # Run crew analysis
            result = pitch_crew.crew().kickoff(inputs=inputs)
            
            # Handle result
            result_text = str(result) if result else "Analysis completed but no results were generated."
            
            # Send completion status
            await status_manager.broadcast_status(job_id, {
                "status": "completed",
                "type": "completed",
                "message": "Analysis completed successfully",
                "result": result_text,
                "timestamp": datetime.now().isoformat()
            })

        except Exception as crew_error:
            error_message = f"Error during crew analysis: {str(crew_error)}"
            print(f"Crew error: {error_message}")
            await status_manager.broadcast_status(job_id, {
                "status": "error",
                "type": "error",
                "message": error_message,
                "timestamp": datetime.now().isoformat()
            })
            raise crew_error

    except Exception as e:
        error_message = f"Error in pitch deck analysis: {str(e)}"
        print(f"Analysis error: {error_message}")
        await status_manager.broadcast_status(job_id, {
            "status": "error",
            "type": "error",
            "message": error_message,
            "timestamp": datetime.now().isoformat()
        })
        raise e

    finally:
        # Clean up uploaded files
        try:
            for file_path in file_paths:
                if os.path.exists(file_path):
                    os.remove(file_path)
        except Exception as cleanup_error:
            print(f"Error cleaning up file(s): {cleanup_error}")

# Previous duplicate route handlers removed

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time updates"""
    await websocket.accept()
    await status_manager.connect(job_id, websocket)
    try:
        while True:
            data = await websocket.receive_text()
            if data == "ping":
                await websocket.send_text("pong")
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        status_manager.disconnect(websocket, job_id)

@app.post("/token")
async def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/users/me")
async def read_users_me(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    user = get_user(fake_users_db, username=username)
    if user is None:
        raise credentials_exception
    return user

@app.get("/dashboard")
async def get_dashboard(token: str = Depends(oauth2_scheme)):
    user = await read_users_me(token)
    dashboard_data = {
        "username": user["username"],
        "uploaded_decks": ["deck1.pdf", "deck2.pptx"],
        "analysis_history": ["Analysis 1", "Analysis 2"]
    }
    return dashboard_data

@app.put("/profile")
async def update_profile(token: str = Depends(oauth2_scheme), full_name: str = Form(...), email: str = Form(...)):
    user = await read_users_me(token)
    user["full_name"] = full_name
    user["email"] = email
    return {"message": "Profile updated successfully", "user": user}

@app.post("/knowledge/upload")
async def upload_knowledge_file(token: str = Depends(oauth2_scheme), file: UploadFile = File(...)):
    user = await read_users_me(token)
    
    # Save file
    file_path = await save_upload_file(file)
    
    # Read file content
    async with aiofiles.open(file_path, 'r') as f:
        content = await f.read()
    
    # Store in vector database
    metadata = {
        "filename": file.filename,
        "uploaded_by": user["username"],
        "upload_date": datetime.now().isoformat(),
        "type": "knowledge"
    }
    doc_id = await vector_store.store_knowledge_file(content, metadata)
    
    return {
        "message": "Knowledge file uploaded successfully",
        "file": {
            "id": doc_id,
            **metadata
        }
    }

@app.get("/knowledge/search")
async def search_knowledge(
    token: str = Depends(oauth2_scheme),
    query: str = None,
    filter_criteria: Dict = None
):
    user = await read_users_me(token)
    results = await vector_store.semantic_search(query, filter_criteria)
    return results

@app.get("/knowledge/files")
async def list_knowledge_files(token: str = Depends(oauth2_scheme)):
    user = await read_users_me(token)
    knowledge_files = [
        {"filename": "file1.pdf", "uploaded_by": "johndoe", "upload_date": "2023-01-01T00:00:00"},
        {"filename": "file2.docx", "uploaded_by": "johndoe", "upload_date": "2023-01-02T00:00:00"}
    ]
    return knowledge_files


mock_analysis_results = {
    "executive_summary": {
        "clarity_of_presentation": 5,
        "investor_readiness": 4,
        "team_strength": 6,
        "market_timing": 7,
        "execution_capability": 5,
        "fundability": 4,
        "aggregate_score": 5.2,
        "key_strengths": [
            "Addresses a real, high-demand problem with a working product and early traction.",
            "Growing market with visible interest.",
            "Experienced list of angel investors and mentors backing the seed round."
        ],
        "critical_gaps": [
            "Limited revenue/profit data; lack of detailed unit economics and future projections.",
            "Many entrants in on-demand driver space; competitive edge over established players is not clearly articulated.",
            "Need stronger operational and go-to-market leadership to scale."
        ]
    },
    "competitive_benchmarking": [
        {"company": "DriveU", "funding": "₹60 Cr", "revenue": "₹24.5 Cr", "valuation": "₹260 Cr", "notes": "Well-funded, multi-city operator; profitable in FY24."},
        {"company": "Park+", "funding": "$54M", "revenue": "₹131 Cr", "valuation": "$355M", "notes": "Parking/EV platform turned mobility service."},
        {"company": "DriversKart", "funding": "~$0.45M", "revenue": "10,000 rides/month", "valuation": "Small", "notes": "Early mover; focused on chauffeur rentals."},
        {"company": "IndianDrivers", "funding": "Bootstrapped", "revenue": "₹9.2 Cr", "valuation": "—", "notes": "Niche Pune startup; reported profitable growth."},
        {"company": "Drivers4Me", "funding": "₹3 Cr", "revenue": "~2.5L app downloads", "valuation": "—", "notes": "Competing B2C/B2B hybrid model."}
    ],
    "risk_identification": [
        "Execution Risks: Scaling to new cities is challenging.",
        "Financial Risks: High cash burn and fundraising risk.",
        "Market Risks: Intense competition and market adoption risk."
    ]
}

@app.get("/analysis/mock")
async def get_mock_analysis(token: str = Depends(oauth2_scheme)):
    user = await read_users_me(token)
    return mock_analysis_results

mock_knowledge_base = [
    {"filename": "market_research.pdf", "content": "India's on-demand driver and car-management market is at an inflection point."},
    {"filename": "competitive_analysis.docx", "content": "DriveU is the market leader in on-demand drivers; covers 6+ metros."}
]

@app.get("/knowledge/mock")
async def get_mock_knowledge(token: str = Depends(oauth2_scheme)):
    user = await read_users_me(token)
    return mock_knowledge_base

@app.get("/decks/similar/{deck_id}")
async def find_similar_decks(
    deck_id: str,
    token: str = Depends(oauth2_scheme),
    top_k: int = 5
):
    user = await read_users_me(token)
    similar_decks = await vector_store.find_similar_decks(deck_id, top_k)
    return similar_decks

@app.get("/decks/compare")
async def compare_deck_versions(
    deck_id_1: str,
    deck_id_2: str,
    token: str = Depends(oauth2_scheme)
):
    user = await read_users_me(token)
    comparison = await vector_store.compare_versions(deck_id_1, deck_id_2)
    return comparison

# Server will be started by uvicorn
