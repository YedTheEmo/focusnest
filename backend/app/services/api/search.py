from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from sqlalchemy import or_
from typing import List

from ..database import get_db, Note
from ..models import SearchResult, NoteResponse
from ..services.resurfacing import IdeaResurfacing

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", response_model=SearchResult)
async def search_notes(
    q: str = Query(..., description="Search query"),
    limit: int = Query(20, description="Maximum results"),
    db: Session = Depends(get_db)
):
    # Simple full-text search
    query = db.query(Note).filter(
        or_(
            Note.title.contains(q),
            Note.content.contains(q)
        )
    ).limit(limit)
    
    notes = query.all()
    total = query.count()
    
    return SearchResult(notes=notes, total=total)

@router.get("/resurface/daily")
async def get_daily_suggestions(count: int = Query(5), db: Session = Depends(get_db)):
    resurfacing = IdeaResurfacing(db)
    suggestions = resurfacing.get_daily_suggestions(count)
    return {"suggestions": [NoteResponse.from_orm(note) for note in suggestions]}

@router.get("/resurface/random")
async def get_random_note(db: Session = Depends(get_db)):
    resurfacing = IdeaResurfacing(db)
    note = resurfacing.get_random_discovery()
    if note:
        return {"note": NoteResponse.from_orm(note)}
    return {"note": None}

@router.get("/resurface/context/{note_id}")
async def get_context_suggestions(note_id: int, count: int = Query(3), db: Session = Depends(get_db)):
    resurfacing = IdeaResurfacing(db)
    suggestions = resurfacing.get_context_suggestions(note_id, count)
    return {"suggestions": [NoteResponse.from_orm(note) for note in suggestions]}

@router.get("/resurface/orphans")
async def get_orphan_suggestions(count: int = Query(3), db: Session = Depends(get_db)):
    resurfacing = IdeaResurfacing(db)
    suggestions = resurfacing.get_orphan_suggestions(count)
    return {"suggestions": [NoteResponse.from_orm(note) for note in suggestions]}
