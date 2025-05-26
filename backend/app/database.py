from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session, relationship
from datetime import datetime
import os

# Database setup
DATABASE_URL = "sqlite:///./data/focusnest.db"
os.makedirs("./data", exist_ok=True)

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# Database Models
class Note(Base):
    __tablename__ = "notes"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    content = Column(Text, nullable=False, default="")
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    outgoing_links = relationship("Link", foreign_keys="Link.from_note_id", back_populates="from_note")
    incoming_links = relationship("Link", foreign_keys="Link.to_note_id", back_populates="to_note")
    tags = relationship("Tag", back_populates="note")

class Link(Base):
    __tablename__ = "links"
    
    id = Column(Integer, primary_key=True, index=True)
    from_note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    to_note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    strength = Column(Integer, default=1)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    from_note = relationship("Note", foreign_keys=[from_note_id], back_populates="outgoing_links")
    to_note = relationship("Note", foreign_keys=[to_note_id], back_populates="incoming_links")

class Tag(Base):
    __tablename__ = "tags"
    
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey("notes.id"), nullable=False)
    tag_name = Column(String, nullable=False)
    
    # Relationships
    note = relationship("Note", back_populates="tags")

def init_db():
    Base.metadata.create_all(bind=engine)

def get_db() -> Session:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
