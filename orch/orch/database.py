from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import declarative_base, sessionmaker, relationship
from datetime import datetime
from pathlib import Path
from .config import settings

Base = declarative_base()

class Session(Base):
    __tablename__ = "sessions"
    id = Column(Integer, primary_key=True)
    topic = Column(String(255), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    agents = Column(String(512))  # Comma-separated list of agent IDs
    
    messages = relationship("Message", back_populates="session")

class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    session_id = Column(Integer, ForeignKey("sessions.id"))
    round_num = Column(Integer)
    agent_id = Column(String(100))
    content = Column(Text)
    reasoning = Column(Text)  # Added to capture internal thought processes
    is_student = Column(Integer, default=0) # Flag for Student Growth Data
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    session = relationship("Session", back_populates="messages")

# Database init
DB_PATH = settings.data_dir / "orch.db"
engine = create_engine(f"sqlite:///{DB_PATH}")

def init_db():
    Base.metadata.create_all(engine)

SessionLocal = sessionmaker(bind=engine)

def save_discussion(topic: str, agent_ids: list[str], history: list[dict]):
    """Persist a full discussion session and its messages."""
    db = SessionLocal()
    try:
        # 1. Create session
        new_session = Session(
            topic=topic,
            agents=",".join(agent_ids)
        )
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        
        # 2. Add messages
        for msg in history:
            new_msg = Message(
                session_id=new_session.id,
                round_num=msg.get("round", 0),
                agent_id=msg.get("agent", "Unknown"),
                content=msg.get("text", ""),
                reasoning=msg.get("reasoning", ""),  # Now capturing the CoT
                is_student=1 if msg.get("agent") == "orch" else 0
            )
            db.add(new_msg)
        
        db.commit()
        return new_session.id
    finally:
        db.close()
