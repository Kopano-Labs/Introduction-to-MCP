from sqlalchemy import create_engine, ForeignKey, String, Integer, Text, DateTime
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship, sessionmaker
from datetime import datetime
from pathlib import Path
import uuid
from .config import settings

# --- ABSOLUTE REGISTRY ALIGNMENT ---
# Modern SQLAlchemy 2.0 Registry-based Base
class Base(DeclarativeBase):
    pass

def generate_uuid():
    return str(uuid.uuid4())

class CouncilSession(Base):
    __tablename__ = "sessions"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    title: Mapped[str] = mapped_column(String, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    rounds: Mapped[list["NeuralRound"]] = relationship(
        "NeuralRound", back_populates="session", cascade="all, delete-orphan"
    )

class NeuralRound(Base):
    __tablename__ = "rounds"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    session_id: Mapped[str] = mapped_column(ForeignKey("sessions.id"))
    round_number: Mapped[int] = mapped_column(Integer, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    
    session: Mapped["CouncilSession"] = relationship("CouncilSession", back_populates="rounds")
    blocks: Mapped[list["CognitiveBlock"]] = relationship(
        "CognitiveBlock", back_populates="round", cascade="all, delete-orphan"
    )

class Mentor(Base):
    __tablename__ = "teachers"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    name: Mapped[str] = mapped_column(String, nullable=False, unique=True)
    role: Mapped[str | None] = mapped_column(String, nullable=True)
    
    blocks: Mapped[list["CognitiveBlock"]] = relationship("CognitiveBlock", back_populates="mentor")

class CognitiveBlock(Base):
    __tablename__ = "reasoning_blocks"
    
    id: Mapped[str] = mapped_column(String, primary_key=True, default=generate_uuid)
    round_id: Mapped[str] = mapped_column(ForeignKey("rounds.id"))
    mentor_id: Mapped[str] = mapped_column(ForeignKey("teachers.id"))
    content: Mapped[str] = mapped_column(Text, nullable=False)
    reasoning: Mapped[str | None] = mapped_column(Text, nullable=True)
    value_score: Mapped[int] = mapped_column(Integer, default=0)
    improvement_hint: Mapped[str | None] = mapped_column(Text, nullable=True)
    override_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_student: Mapped[int] = mapped_column(Integer, default=0)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    round: Mapped["NeuralRound"] = relationship("NeuralRound", back_populates="blocks")
    mentor: Mapped["Mentor"] = relationship("Mentor", back_populates="blocks")

# --- DATABASE ENGINE & SESSION ---
DB_PATH = settings.data_dir / "orch.db"
engine = create_engine(f"sqlite:///{DB_PATH}", echo=False)
SessionLocal = sessionmaker(bind=engine)

def init_db():
    Base.metadata.create_all(engine)

def get_or_create_mentor(db, name: str, role: str = None):
    """Ensure a mentor exists in the relational index."""
    from sqlalchemy import select
    stmt = select(Mentor).where(Mentor.name == name)
    mentor = db.execute(stmt).scalar_one_or_none()
    
    if not mentor:
        mentor = Mentor(id=generate_uuid(), name=name, role=role)
        db.add(mentor)
        db.commit()
        db.refresh(mentor)
    return mentor
