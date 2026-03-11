"""SQLAlchemy database models for TruthLens AI."""

from datetime import datetime
from sqlalchemy import Column, String, Integer, Float, DateTime, Text, JSON, ForeignKey, Enum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
import enum
import uuid

Base = declarative_base()


class User(Base):
    """User model."""
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, nullable=False, index=True)
    password_hash = Column(String, nullable=False)
    username = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    sessions = relationship("Session", back_populates="user", cascade="all, delete-orphan")


class Session(Base):
    """Analysis session model."""
    __tablename__ = "sessions"
    
    session_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, ForeignKey("users.user_id"), nullable=False, index=True)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    user = relationship("User", back_populates="sessions")
    queries = relationship("Query", back_populates="session", cascade="all, delete-orphan")


class Query(Base):
    """Individual query/analysis model."""
    __tablename__ = "queries"
    
    query_id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String, ForeignKey("sessions.session_id"), nullable=False, index=True)
    input_text = Column(Text, nullable=False)
    
    # Verdict scores
    verdict = Column(String, nullable=False)  # REAL, RUMOR, FAKE
    confidence = Column(Float, nullable=False)
    
    # Probability scores
    score_real = Column(Float, nullable=False)
    score_rumor = Column(Float, nullable=False)
    score_fake = Column(Float, nullable=False)
    
    # Risk metrics
    propagation_risk = Column(String, nullable=False)  # LOW, MEDIUM, HIGH
    propagation_score = Column(Float, nullable=False)
    evidence_score = Column(Float, nullable=False)
    
    # Model breakdown
    model_breakdown = Column(JSON, nullable=True)  # {nlp_score, evidence_credibility, propagation_risk}
    
    # Summary and signals
    summary = Column(Text, nullable=True)
    key_signals = Column(JSON, nullable=True)  # List of strings
    
    # Claims and evidence
    claims = Column(JSON, nullable=True)  # List of claim objects
    evidence_sources = Column(JSON, nullable=True)  # List of evidence objects
    
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="queries")
