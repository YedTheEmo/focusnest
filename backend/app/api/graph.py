from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, List
from sqlalchemy.orm import Session
import networkx as nx

from ..database import get_db
from ..database import Note as NoteModel, Link as LinkModel, Tag as TagModel

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/", summary="Get full knowledge graph")
def get_graph(db: Session = Depends(get_db)) -> Dict:
    G = nx.Graph()
    for n in db.query(NoteModel).all():
        G.add_node(n.id, title=n.title)
    for l in db.query(LinkModel).all():
        G.add_edge(l.from_note_id, l.to_note_id, strength=l.strength)
    nodes = [{"id": nid, "title": data["title"], "connections": G.degree(nid)} for nid, data in G.nodes(data=True)]
    links = [{"source": u, "target": v, "strength": data["strength"]} for u, v, data in G.edges(data=True)]
    return {"nodes": nodes, "links": links}
