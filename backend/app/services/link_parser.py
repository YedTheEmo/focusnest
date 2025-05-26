import re
from typing import List, Set
from sqlalchemy.orm import Session
from ..database import Note

class LinkParser:
    LINK_PATTERN = r'\[\[([^\]]+)\]\]'
    
    @staticmethod
    def extract_links(content: str) -> Set[str]:
        """Extract all [[Note Title]] links from content"""
        matches = re.findall(LinkParser.LINK_PATTERN, content)
        return set(matches)
    
    @staticmethod
    def resolve_links(content: str, db: Session) -> List[int]:
        """Resolve link titles to note IDs"""
        link_titles = LinkParser.extract_links(content)
        resolved_ids = []
        
        for title in link_titles:
            note = db.query(Note).filter(Note.title == title.strip()).first()
            if note:
                resolved_ids.append(note.id)
        
        return resolved_ids
    
    @staticmethod
    def render_links(content: str, db: Session) -> str:
        """Convert [[Title]] to clickable links"""
        def replace_link(match):
            title = match.group(1).strip()
            note = db.query(Note).filter(Note.title == title).first()
            if note:
                return f'<a href="#" class="note-link" data-note-id="{note.id}">{title}</a>'
            else:
                return f'<span class="broken-link">{title} (not found)</span>'
        
        return re.sub(LinkParser.LINK_PATTERN, replace_link, content)
