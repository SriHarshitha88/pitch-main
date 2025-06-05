from fastapi import FastAPI, HTTPException, status, UploadFile, File, Form, WebSocket, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List, Optional
import json
from datetime import datetime
import os
from fastapi.responses import FileResponse
import tempfile
from . import models, database, websocket, config, schemas
from .services import analysis_service

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
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    files: UploadFile = File(...),
    startup_name: str = Form(...)
):
    try:
        content = await files.read()
        if len(content) > config.MAX_FILE_SIZE:
            raise HTTPException(
                status_code=400,
                detail=f"File size exceeds maximum limit of {config.MAX_FILE_SIZE // (1024 * 1024)}MB"
            )

        if files.content_type not in config.ALLOWED_FILE_TYPES:
            raise HTTPException(
                status_code=400,
                detail="Invalid file type. Only PDF and PowerPoint files are allowed."
            )

        os.makedirs(config.UPLOAD_DIR, exist_ok=True)
        file_path = os.path.join(config.UPLOAD_DIR, files.filename)

        with open(file_path, "wb") as buffer:
            buffer.write(content)

        deck = models.Deck(
            filename=files.filename,
            file_path=file_path,
            deck_metadata={"startup_name": startup_name}
        )
        db.add(deck)
        db.commit()
        db.refresh(deck)

        analysis = models.Analysis(
            deck_id=deck.id,
            status="pending"
        )
        db.add(analysis)
        db.commit()
        db.refresh(analysis)

        # background_tasks.add_task(analysis_service.perform_analysis, analysis.id, deck.file_path)
        # Temporarily run analysis directly for debugging
        analysis_service.perform_analysis(analysis.id, deck.file_path)

        return {"job_id": analysis.id, "deck_id": deck.id}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while processing your request: {str(e)}"
        )

@app.get("/decks", response_model=List[schemas.Deck])
async def list_decks(db: Session = Depends(get_db)):
    decks = db.query(models.Deck).all()
    return decks

@app.get("/decks/{deck_id}", response_model=schemas.Deck)
async def get_deck(deck_id: int, db: Session = Depends(get_db)):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")
    return deck

@app.post("/decks/{deck_id}/analyze", response_model=schemas.Analysis)
async def reanalyze_deck(
    deck_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db)
):
    deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
    if not deck:
        raise HTTPException(status_code=404, detail="Deck not found")

    analysis = models.Analysis(
        deck_id=deck.id,
        status="pending"
    )
    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    background_tasks.add_task(analysis_service.perform_analysis, analysis.id, deck.file_path)

    return analysis

@app.get("/decks/compare")
async def compare_decks(
    deck_id_1: str,
    deck_id_2: str,
    db: Session = Depends(get_db)
):
    deck1 = db.query(models.Deck).filter(models.Deck.id == deck_id_1).first()
    deck2 = db.query(models.Deck).filter(models.Deck.id == deck_id_2).first()

    if not deck1 or not deck2:
        raise HTTPException(status_code=404, detail="One or both decks not found")

    result1 = db.query(models.AnalysisResult).join(models.Analysis).filter(
        models.Analysis.deck_id == deck_id_1
    ).first()
    result2 = db.query(models.AnalysisResult).join(models.Analysis).filter(
        models.Analysis.deck_id == deck_id_2
    ).first()

    if not result1 or not result2:
        raise HTTPException(status_code=400, detail="Both decks must be analyzed first")

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

@app.delete("/decks/{deck_id}")
async def delete_deck(deck_id: int, db: Session = Depends(get_db)):
    try:
        deck = db.query(models.Deck).filter(models.Deck.id == deck_id).first()
        if not deck:
            raise HTTPException(status_code=404, detail="Deck not found")

        if os.path.exists(deck.file_path):
            os.remove(deck.file_path)

        db.query(models.Analysis).filter(models.Analysis.deck_id == deck_id).delete()

        db.delete(deck)
        db.commit()

        return {"message": "Deck deleted successfully"}
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"An error occurred while deleting the deck: {str(e)}"
        )

@app.get("/analysis/{job_id}/status", response_model=schemas.Analysis)
async def get_analysis_status(job_id: int, db: Session = Depends(get_db)):
    analysis = db.query(models.Analysis).filter(models.Analysis.id == job_id).first()
    if not analysis:
        raise HTTPException(status_code=404, detail="Analysis job not found")
    return analysis

@app.get("/analysis/{job_id}/result", response_model=schemas.AnalysisResult)
async def get_analysis_result(job_id: int, db: Session = Depends(get_db)):
    analysis_result = db.query(models.AnalysisResult).join(models.Analysis).filter(models.Analysis.id == job_id).first()
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")
    return analysis_result

@app.get("/analysis/{job_id}/report")
async def download_analysis_report(job_id: int, db: Session = Depends(get_db)):
    analysis_result = db.query(models.AnalysisResult).join(models.Analysis).filter(models.Analysis.id == job_id).first()
    if not analysis_result:
        raise HTTPException(status_code=404, detail="Analysis result not found")

    # Generate a simple text report
    report_content = f"Analysis Report for Job ID: {job_id}\n\n"
    report_content += f"Overall Score: {analysis_result.overall_score}\n\n"
    report_content += "Pitch Analysis:\n"
    if analysis_result.pitch_analysis:
        for key, value in analysis_result.pitch_analysis.items():
            report_content += f"  {key}: {value}\n"
    report_content += "\nMarket Research:\n"
    if analysis_result.market_research:
        for key, value in analysis_result.market_research.items():
            report_content += f"  {key}: {value}\n"
    report_content += "\nFinancial Analysis:\n"
    if analysis_result.financial_analysis:
        for key, value in analysis_result.financial_analysis.items():
            report_content += f"  {key}: {value}\n"
    report_content += "\nWebsite Analysis:\n"
    if analysis_result.website_analysis:
        for key, value in analysis_result.website_analysis.items():
            report_content += f"  {key}: {value}\n"
    report_content += "\nInvestment Strategy:\n"
    if analysis_result.investment_strategy:
        for key, value in analysis_result.investment_strategy.items():
            report_content += f"  {key}: {value}\n"
    report_content += "\nDue Diligence:\n"
    if analysis_result.due_diligence:
        for key, value in analysis_result.due_diligence.items():
            report_content += f"  {key}: {value}\n"

    # Save the report to a temporary file
    with tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.txt') as tmp_file:
        tmp_file.write(report_content)
        tmp_file_path = tmp_file.name

    # Return the file as a response
    return FileResponse(path=tmp_file_path, filename=f"analysis_report_job_{job_id}.txt", media_type='text/plain')

@app.post("/knowledge/upload")
async def upload_knowledge_file(
    file: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    content = await file.read()
    if len(content) > config.MAX_FILE_SIZE:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum limit of {config.MAX_FILE_SIZE // (1024 * 1024)}MB"
        )

    file_path = os.path.join(config.KNOWLEDGE_DIR, file.filename)

    with open(file_path, "wb") as buffer:
        buffer.write(content)

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
    files = db.query(models.KnowledgeFile).all()
    return files

@app.get("/knowledge/files")
async def list_knowledge_files(db: Session = Depends(get_db)):
    files = db.query(models.KnowledgeFile).all()
    return files

@app.get("/analytics/dashboard", response_model=schemas.AnalyticsDashboardMetrics)
async def get_analytics_dashboard_metrics(db: Session = Depends(get_db)):
    total_decks = db.query(models.Deck).count()
    analysis_pending_count = db.query(models.Analysis).filter(models.Analysis.status == "pending").count()
    analysis_processing_count = db.query(models.Analysis).filter(models.Analysis.status == "processing").count()
    analysis_completed_count = db.query(models.Analysis).filter(models.Analysis.status == "completed").count()
    analysis_failed_count = db.query(models.Analysis).filter(models.Analysis.status == "failed").count()

    return {
        "total_decks": total_decks,
        "analysis_pending_count": analysis_pending_count,
        "analysis_processing_count": analysis_processing_count,
        "analysis_completed_count": analysis_completed_count,
        "analysis_failed_count": analysis_failed_count,
    }

@app.get("/analytics/recent-activity", response_model=List[schemas.RecentAnalysis])
async def get_recent_activity(db: Session = Depends(get_db)):
    recent_analyses = db.query(models.Analysis)\
                          .join(models.Deck)\
                          .order_by(models.Analysis.created_at.desc())\
                          .limit(5)\
                          .all()

    recent_activity_data = []
    for analysis in recent_analyses:
        recent_activity_data.append({
            "analysis_id": analysis.id,
            "deck_id": analysis.deck_id,
            "startup_name": analysis.deck.deck_metadata.get("startup_name", "N/A"),
            "analysis_status": analysis.status,
            "completed_at": analysis.completed_at,
            "created_at": analysis.created_at
        })

    return [schemas.RecentAnalysis.model_validate(item) for item in recent_activity_data]

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    await websocket.websocket_endpoint(websocket, job_id)