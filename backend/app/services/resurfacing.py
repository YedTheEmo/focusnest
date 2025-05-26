import random
from datetime import datetime, timedelta
from typing import List
from sqlalchemy.orm import Session
from sqlalchemy import func
from ..database import Note, Link

class IdeaResurfacing:
    def __init__(self, db: Session):
        self.db = db
    
    def get_daily_suggestions(self, count: int = 5) -> List[Note]:
        """Get daily note suggestions using spaced repetition"""
        # Get notes not viewed recently
        week_ago = datetime.utcnow() - timedelta(days=7)
        
        candidates = self.db.query(Note).filter(
            Note.updated_at < week_ago
        ).all()
        
        if len(candidates) <= count:
            return candidates
        
        # Prioritize notes with more connections
        weighted_candidates = []
        for note in candidates:
            connection_count = len(note.outgoing_links) + len(note.incoming_links)
            weight = max(1, connection_count)  # Minimum weight of 1
            weighted_candidates.extend([note] * weight)
        
        return random.sample(weighted_candidates, min(count, len(weighted_candidates)))
    
    def get_random_discovery(self, exclude_recent: bool = True) -> Note:
        """Get a random note for serendipitous discovery"""
        query = self.db.query(Note)
        
        if exclude_recent:
            three_days_ago = datetime.utcnow() - timedelta(days=3)
            query = query.filter(Note.updated_at < three_days_ago)
        
        notes = query.all()
        return random.choice(notes) if notes else None
    
    def get_context_suggestions(self, current_note_id: int, count: int = 3) -> List[Note]:
        """Get suggestions based on current note context"""
        current_note = self.db.query(Note).filter(Note.id == current_note_id).first()
        if not current_note:
            return []
        
        # Get connected notes
        connected_ids = []
        for link in current_note.outgoing_links:
            connected_ids.append(link.to_note_id)
        for link in current_note.incoming_links:
            connected_ids.append(link.from_note_id)
        
        if not connected_ids:
            return self.get_daily_suggestions(count)
        
        suggestions = self.db.query(Note).filter(Note.id.in_(connected_ids)).limit(count).all()
        return suggestions
    
    def get_orphan_suggestions(self, count: int = 3) -> List[Note]:
        """Suggest orphaned notes that need connections"""
        # Find notes with no links
        orphan_notes = self.db.query(Note).outerjoin(Link, 
            (Note.id == Link.from_note_id) | (Note.id == Link.to_note_id)
        ).filter(Link.id.is_(None)).limit(count).all()
        
        return orphan_notes
