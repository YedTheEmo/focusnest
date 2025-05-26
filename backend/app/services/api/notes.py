from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db, Note, Link
from ..models import NoteCreate, NoteUpdate, NoteResponse
from ..services.link_parser import LinkParser

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", response_model=List[NoteResponse])
async def get_all_notes(db: Session = Depends(get_db)):
    notes = db.query(Note).order_by(Note.updated_at.desc()).all()
    return notes

@router.get("/{note_id}", response_model=NoteResponse)
async def get_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

@router.post("/", response_model=NoteResponse)
async def create_note(note: NoteCreate, db: Session = Depends(get_db)):
    # Check if title already exists
    existing = db.query(Note).filter(Note.title == note.title).first()
    if existing:
        raise HTTPException(status_code=400, detail="Note with this title already exists")
    
    db_note = Note(title=note.title, content=note.content)
    db.add(db_note)
    db.commit()
    db.refresh(db_note)
    
    # Process links
    await _update_note_links(db_note.id, note.content, db)
    
    return db_note

@router.put("/{note_id}", response_model=NoteResponse)
async def update_note(note_id: int, note: NoteUpdate, db: Session = Depends(get_db)):
    db_note = db.query(Note).filter(Note.id == note_id).first()
    if not db_note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Check title uniqueness if changed
    if note.title != db_note.title:
        existing = db.query(Note).filter(Note.title == note.title).first()
        if existing:
            raise HTTPException(status_code=400, detail="Note with this title already exists")
    
    db_note.title = note.title
    db_note.content = note.content
    db.commit()
    db.refresh(db_note)
    
    # Update links
    await _update_note_links(note_id, note.content, db)
    
    return db_note

@router.delete("/{note_id}")
async def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete associated links
    db.query(Link).filter(
        (Link.from_note_id == note_id) | (Link.to_note_id == note_id)
    ).delete()
    
    db.delete(note)
    db.commit()
    return {"message": "Note deleted successfully"}

@router.get("/{note_id}/render")
async def render_note_content(note_id: int, db: Session = Depends(get_db)):
    note = db.query(Note).filter(Note.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    rendered_content = LinkParser.render_links(note.content, db)
    return {"content": rendered_content}

async def _update_note_links(note_id: int, content: str, db: Session):
    """Update links for a note based on its content"""
    # Remove existing outgoing links
    db.query(Link).filter(Link.from_note_id == note_id).delete()
    
    # Add new links
    linked_note_ids = LinkParser.resolve_links(content, db)
    for target_id in linked_note_ids:
        if target_id != note_id:  # Avoid self-links
            link = Link(from_note_id=note_id, to_note_id=target_id)
            db.add(link)
    
    db.commit()
