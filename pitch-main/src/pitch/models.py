from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, JSON, Float, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

Base = declarative_base()

class UserRole(enum.Enum):
    USER = "user"
    ADMIN = "admin"

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True)
    email = Column(String, unique=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    full_name = Column(String)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    last_login = Column(DateTime)
    
    # Relationships
    decks = relationship("Deck", back_populates="owner")
    analyses = relationship("Analysis", back_populates="user")
    knowledge_files = relationship("KnowledgeFile", back_populates="uploader")

class Deck(Base):
    __tablename__ = "decks"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_path = Column(String)
    file_size = Column(Integer)
    file_type = Column(String)
    version = Column(Integer, default=1)
    parent_version_id = Column(Integer, ForeignKey("decks.id"), nullable=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_public = Column(Boolean, default=False)
    metadata = Column(JSON)
    
    # Relationships
    owner = relationship("User", back_populates="decks")
    analyses = relationship("Analysis", back_populates="deck")
    parent_version = relationship("Deck", remote_side=[id])

class Analysis(Base):
    __tablename__ = "analyses"
    
    id = Column(Integer, primary_key=True)
    deck_id = Column(Integer, ForeignKey("decks.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    job_id = Column(String, unique=True)
    status = Column(String)
    result = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime)
    error_message = Column(String, nullable=True)
    
    # Relationships
    deck = relationship("Deck", back_populates="analyses")
    user = relationship("User", back_populates="analyses")

class KnowledgeFile(Base):
    __tablename__ = "knowledge_files"
    
    id = Column(Integer, primary_key=True)
    filename = Column(String)
    file_path = Column(String)
    file_type = Column(String)
    uploader_id = Column(Integer, ForeignKey("users.id"))
    is_public = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    metadata = Column(JSON)
    vector_id = Column(String, unique=True)  # Pinecone vector ID
    
    # Relationships
    uploader = relationship("User", back_populates="knowledge_files")

class UsageMetrics(Base):
    __tablename__ = "usage_metrics"
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    event_type = Column(String)  # upload, analysis, search, etc.
    event_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    user = relationship("User")

class SystemLog(Base):
    __tablename__ = "system_logs"
    
    id = Column(Integer, primary_key=True)
    level = Column(String)  # INFO, WARNING, ERROR, etc.
    message = Column(String)
    context = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow) 