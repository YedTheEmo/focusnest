from fastapi import APIRouter, HTTPException, Depends
from typing import List, Dict
from sqlalchemy.orm import Session

from ..database import get_db
from ..database import Note as NoteModel, Link as LinkModel, Tag as TagModel
from ..services.link_parser import LinkParser

router = APIRouter(prefix="/notes", tags=["notes"])

@router.get("/", summary="List notes with pagination")
def list_notes(limit: int = 100, offset: int = 0, db: Session = Depends(get_db)) -> List[Dict]:
    notes = (
        db.query(NoteModel)
          .order_by(NoteModel.updated_at.desc())
          .limit(limit)
          .offset(offset)
          .all()
    )
    return [{"id": n.id, "title": n.title, "content": n.content} for n in notes]

@router.get("/{note_id}", summary="Get a specific note by ID")
def get_note(note_id: int, db: Session = Depends(get_db)) -> Dict:
    note = db.get(NoteModel, note_id)
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return {"id": note.id, "title": note.title, "content": note.content}

@router.post("/", summary="Create a new note")
def create_note(body: Dict, db: Session = Depends(get_db)) -> Dict:
    n = NoteModel(title=body.get("title"), content=body.get("content", ""))
    db.add(n)
    db.commit()
    db.refresh(n)
    
    # Create links for any referenced notes
    link_titles = LinkParser.extract_links(body.get("content", ""))
    for title in link_titles:
        linked_note = db.query(NoteModel).filter(NoteModel.title == title.strip()).first()
        if linked_note:
            link = LinkModel(from_note_id=n.id, to_note_id=linked_note.id)
            db.add(link)
    db.commit()
    
    return {"id": n.id, "title": n.title, "content": n.content}

@router.put("/{note_id}", summary="Update an existing note")
def update_note(note_id: int, body: Dict, db: Session = Depends(get_db)) -> Dict:
    n = db.get(NoteModel, note_id)
    if not n:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Delete existing links
    db.query(LinkModel).filter(LinkModel.from_note_id == note_id).delete()
    
    n.title = body.get("title", n.title)
    n.content = body.get("content", n.content)
    db.commit()
    
    # Create new links
    link_titles = LinkParser.extract_links(body.get("content", ""))
    for title in link_titles:
        linked_note = db.query(NoteModel).filter(NoteModel.title == title.strip()).first()
        if linked_note:
            link = LinkModel(from_note_id=n.id, to_note_id=linked_note.id)
            db.add(link)
    db.commit()
    
    return {"id": n.id, "title": n.title, "content": n.content}

@router.delete("/{note_id}", summary="Delete a note")
def delete_note(note_id: int, db: Session = Depends(get_db)) -> Dict:
    n = db.get(NoteModel, note_id)
    if not n:
        raise HTTPException(status_code=404, detail="Note not found")
        # cascade delete related links and tags
    db.query(LinkModel).filter((LinkModel.from_note_id==note_id)|(LinkModel.to_note_id==note_id)).delete(synchronize_session=False)
    db.query(TagModel).filter(TagModel.note_id==note_id).delete(synchronize_session=False)
    db.delete(n)
    db.commit()
    return {"message": "Deleted"}
