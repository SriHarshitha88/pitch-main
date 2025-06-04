from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
import os
from . import models, database, websocket, config

app = FastAPI(title="Pitch Deck Analyzer API")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize database on startup
@app.on_event("startup")
async def startup_event():
    models.Base.metadata.create_all(bind=database.engine)

# Dependency
def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Deck endpoints
@app.post("/analyze")
async def analyze_deck(
    files: UploadFile = File(...),
    startup_name: str = Form(...),
    db: Session = Depends(get_db)
):
    try:
        # Validate file size
        content = await files.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {config.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )
        
        # Validate file type
        if files.content_type not in config.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and PowerPoint files are allowed."
            )
        
        # Save file
        file_path = os.path.join(config.UPLOAD_DIR, files.filename)
        
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Create deck record
        deck = models.Deck(
            filename=files.filename,
            file_path=file_path,
            deck_metadata={"startup_name": startup_name, "upload_date": str(datetime.utcnow())}
        )
        db.add(deck)
        db.commit()
        db.refresh(deck)
        
        # Create analysis record
        analysis = models.Analysis(
            deck_id=deck.id,
            status="pending"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)
        
        return {"job_id": analysis.id, "deck_id": deck.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/decks")
async def list_decks(db: Session = Depends(get_db)):
    decks = db.query(models.Deck).all()
    return decks

@app.get("/decks/{deck_id}")
async def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

@app.get("/decks/compare")
async def compare_decks(
    deck_id_1: str,
    deck_id_2: str,
    db: Session = Depends(get_db)
):
    # Get both decks
    deck1 = db.query(models.Deck).filter(models.Deck.id == deck_id_1).first()
    deck2 = db.query(models.Deck).filter(models.Deck.id == deck_id_2).first()
    
    if not deck1 or not deck2:
        raise HTTPException(status_code=404, detail="One or both decks not found")
    
    # Get analysis results
    result1 = db.query(models.AnalysisResult).join(models.Analysis).filter(
        models.Analysis.deck_id == deck_id_1
    ).first()
    result2 = db.query(models.AnalysisResult).join(models.Analysis).filter(
        models.Analysis.deck_id == deck_id_2
    ).first()
    
    if not result1 or not result2:
        raise HTTPException(status_code=400, detail="Both decks must be analyzed first")
    
    # Calculate differences
    score_differences = {
        "overall": result2.overall_score - result1.overall_score,
        "pitch_analysis": {
            k: result2.pitch_analysis[k] - result1.pitch_analysis[k]
            for k in result1.pitch_analysis
        },
        "market_research": {
            k: result2.market_research[k] - result1.market_research[k]
            for k in result1.market_research
        },
        "financial_analysis": {
            k: result2.financial_analysis[k] - result1.financial_analysis[k]
            for k in result1.financial_analysis
        }
    }
    
    # Generate improvements
    improvements = []
    for category, scores in score_differences.items():
        if isinstance(scores, dict):
            for metric, diff in scores.items():
                if diff > 0:
                    improvements.append(f"Improved {metric} by {diff:.1f}%")
    
    return {
        "score_differences": score_differences,
        "improvements": improvements
    }

# Analysis endpoints
@app.get("/analysis/{job_id}/status")
async def get_analysis_status(job_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.Analysis).filter(models.Analysis.id == job_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    return {
        "status": analysis.status,
        "created_at": analysis.created_at,
        "completed_at": analysis.completed_at
    }

@app.get("/analysis/{job_id}/result")
async def get_analysis_result(job_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.Analysis).filter(models.Analysis.id == job_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis not found")
    
    if analysis.status != "completed":
        raise HTTPException(status_code=400, detail="Analysis not completed")
    
    result = db.query(models.AnalysisResult).filter(
        models.AnalysisResult.analysis_id == job_id
    ).first()
    if not result:
        raise HTTPException(status_code=404, detail="Result not found")
    
    return result

# Knowledge base endpoints
@app.post("/knowledge/upload")
async def upload_knowledge_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    # Validate file size
    content = await file.read()
    if len(content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {config.MAX_FILE_SIZE // (1024 * 1024)}MB"
        )
    
    # Save file
    file_path = os.path.join(config.KNOWLEDGE_DIR, file.filename)
    
    with open(file_path, "wb") as buffer:
        buffer.write(content)
    
    # Create knowledge file record
    knowledge_file = models.KnowledgeFile(
        filename=file.filename,
        file_path=file_path,
        file_type=file.content_type
    )
    db.add(knowledge_file)
    db.commit()
    db.refresh(knowledge_file)
    
    return knowledge_file

@app.get("/knowledge/search")
async def search_knowledge(query: str, db: Session = Depends(get_db)):
    # TODO: Implement actual search functionality
    files = db.query(models.KnowledgeFile).all()
    return files

@app.get("/knowledge/files")
async def list_knowledge_files(db: Session = Depends(get_db)):
    files = db.query(models.KnowledgeFile).all()
    return files

# WebSocket endpoint
@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.websocket_endpoint(websocket, job_id) 