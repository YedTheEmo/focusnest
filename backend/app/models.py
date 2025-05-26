from pydantic import BaseModel
from datetime import datetime
from typing import List, Optional

class NoteBase(BaseModel):
    title: str
    content: str

class NoteCreate(NoteBase):
    pass

class NoteUpdate(NoteBase):
    pass

class NoteResponse(NoteBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

class LinkResponse(BaseModel):
    id: int
    from_note_id: int
    to_note_id: int
    strength: int
    from_note_title: str
    to_note_title: str
    
    class Config:
        from_attributes = True

class GraphNode(BaseModel):
    id: int
    title: str
    connections: int

class GraphLink(BaseModel):
    source: int
    target: int
    strength: int

class GraphData(BaseModel):
    nodes: List[GraphNode]
    links: List[GraphLink]

class SearchResult(BaseModel):
    notes: List[NoteResponse]
    total: int

    from pydantic import BaseModel
from typing import Optional

# … existing models …

class LinkCreate(BaseModel):
    to_note: int
    strength: Optional[int] = 1

class TagCreate(BaseModel):
    tag_name: str

class MetadataCreate(BaseModel):
    key: str
    value: str


