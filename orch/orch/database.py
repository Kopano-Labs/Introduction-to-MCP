from sqlalchemy import create_engine, Column, String, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from pathlib import Path
import uuid
from .config import settings

Base = declarative_base()

def generate_uuid():
    return str(uuid.uuid4())

class Session(Base):
    __tablename__ = "sessions"
    id = Column(String, primary_key=True, default=generate_uuid)
    title = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    rounds = relationship("Round", back_populates="session", cascade="all, delete-orphan")

class Round(Base):
    __tablename__ = "rounds"
    id = Column(String, primary_key=True, default=generate_uuid)
    session_id = Column(String, ForeignKey("sessions.id"))
    round_number = Column(Integer, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="rounds")
    blocks = relationship("ReasoningBlock", back_populates="round", cascade="all, delete-orphan")

class Teacher(Base):
    __tablename__ = "teachers"
    id = Column(String, primary_key=True, default=generate_uuid)
    name = Column(String, nullable=False, unique=True)
    role = Column(String, nullable=True)
    blocks = relationship("ReasoningBlock", back_populates="teacher")

class ReasoningBlock(Base):
    __tablename__ = "reasoning_blocks"
    id = Column(String, primary_key=True, default=generate_uuid)
    round_id = Column(String, ForeignKey("rounds.id"))
    teacher_id = Column(String, ForeignKey("teachers.id"))
    content = Column(Text, nullable=False)
    reasoning = Column(Text) # Preserving the CoT logic
    value_score = Column(Integer, default=0)
    improvement_hint = Column(Text, nullable=True)
    override_score = Column(Integer, nullable=True)
    is_student = Column(Integer, default=0) # Preserving student growth tagging
    created_at = Column(DateTime, default=datetime.utcnow)

    round = relationship("Round", back_populates="blocks")
    teacher = relationship("Teacher", back_populates="blocks")

# Database configuration
DB_PATH = settings.data_dir / "orch.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def get_or_create_teacher(db, name: str, role: str = None):
    """Ensure a teacher exists in the relational index."""
    teacher = db.query(Teacher).filter(Teacher.name == name).first()
    if not teacher:
        teacher = Teacher(id=generate_uuid(), name=name, role=role)
        db.add(teacher)
        db.commit()
        db.refresh(teacher)
    return teacher
