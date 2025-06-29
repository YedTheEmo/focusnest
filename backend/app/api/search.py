from fastapi import APIRouter, Depends, Query
from typing import List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func, or_

from ..database import get_db
from ..services.resurfacing import IdeaResurfacing
from ..database import Note as NoteModel

router = APIRouter(prefix="/search", tags=["search"])

@router.get("/", summary="Search notes by title or content")
def search_notes(q: str = Query(..., min_length=2), db: Session = Depends(get_db)) -> Dict[str, List[Dict]]:
    pattern = f"%{q.lower()}%"
    notes = (
        db.query(NoteModel)
          .filter(
              or_(func.lower(NoteModel.title).like(pattern), func.lower(NoteModel.content).like(pattern))
          )
          .order_by(NoteModel.updated_at.desc())
          .all()
    )
    return {"notes": [{"id": n.id, "title": n.title, "content": n.content} for n in notes]}

@router.get("/resurface/daily", summary="Get daily resurfacing note suggestions")
def daily_resurface(count: int = 5, db: Session = Depends(get_db)):
    resurfacer = IdeaResurfacing(db)
    notes = resurfacer.get_daily_suggestions(count)
    return {"notes": [
        {"id": n.id, "title": n.title, "content": n.content, "updated_at": n.updated_at.isoformat()} for n in notes
    ]}

@router.get("/resurface/random", summary="Get a random resurfacing note")
def random_resurface(db: Session = Depends(get_db)):
    resurfacer = IdeaResurfacing(db)
    note = resurfacer.get_random_discovery()
    if note:
        return {"note": {"id": note.id, "title": note.title, "content": note.content, "updated_at": note.updated_at.isoformat()}}
    else:
        return {"note": None}
