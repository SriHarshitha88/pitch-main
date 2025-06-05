from pydantic import BaseModel, ConfigDict, Field
from datetime import datetime
from typing import Optional, Any

class DeckBase(BaseModel):
    filename: str
    deck_metadata: Any

class DeckCreate(DeckBase):
    pass

class Deck(DeckBase):
    id: int
    # Map backend's upload_date to frontend's createdAt using Alias
    createdAt: datetime = Field(alias="upload_date")
    # Include status from the related Analysis
    status: Optional[str] = None

    model_config = ConfigDict(from_attributes=True)

class AnalysisBase(BaseModel):
    status: str

class AnalysisCreate(AnalysisBase):
    deck_id: int

class Analysis(AnalysisBase):
    id: int
    deck_id: int
    createdAt: datetime = Field(alias="created_at")
    completedAt: Optional[datetime] = Field(None, alias="completed_at")

    model_config = ConfigDict(from_attributes=True)

class AnalysisResultBase(BaseModel):
    overall_score: Optional[float] = None
    pitch_analysis: Optional[Any] = None
    market_research: Optional[Any] = None
    financial_analysis: Optional[Any] = None
    generated_report: Optional[str] = None

class AnalysisResultCreate(AnalysisResultBase):
    analysis_id: int

class AnalysisResult(AnalysisResultBase):
    id: int
    analysis_id: int
    createdAt: datetime = Field(alias="created_at")

    model_config = ConfigDict(from_attributes=True)

class KnowledgeFileBase(BaseModel):
    filename: str
    file_type: str

class KnowledgeFileCreate(KnowledgeFileBase):
    pass

class KnowledgeFile(KnowledgeFileBase):
    id: int
    upload_date: datetime = Field(alias="upload_date")

    model_config = ConfigDict(from_attributes=True)

# New schema for Analytics Dashboard metrics
class AnalyticsDashboardMetrics(BaseModel):
    total_decks: int
    analysis_pending_count: int
    analysis_processing_count: int
    analysis_completed_count: int
    analysis_failed_count: int

# New schema for Recent Analysis activity on Dashboard
class RecentAnalysis(BaseModel):
    analysis_id: int
    deck_id: int
    startupName: str = Field(alias="startup_name") # Map deck metadata startup_name
    analysis_status: str
    analyzedAt: Optional[datetime] = Field(None, alias="completed_at") # Use completed_at from analysis
    createdAt: datetime = Field(alias="created_at") # Analysis creation date

    model_config = ConfigDict(from_attributes=True) 