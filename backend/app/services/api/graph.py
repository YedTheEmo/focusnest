from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List

from ..database import get_db
from ..models import GraphData, LinkResponse
from ..services.graph_engine import GraphEngine

router = APIRouter(prefix="/graph", tags=["graph"])

@router.get("/data", response_model=GraphData)
async def get_graph_data(db: Session = Depends(get_db)):
    engine = GraphEngine(db)
    graph_data = engine.get_graph_data()
    return GraphData(**graph_data)

@router.get("/connections/{note_id}")
async def get_note_connections(note_id: int, db: Session = Depends(get_db)):
    engine = GraphEngine(db)
    connections = engine.get_connected_notes(note_id)
    return {"note_id": note_id, "connections": connections}

@router.get("/orphans")
async def get_orphan_notes(db: Session = Depends(get_db)):
    engine = GraphEngine(db)
    orphans = engine.get_orphan_notes()
    return {"orphan_notes": orphans}

@router.get("/central")
async def get_central_notes(limit: int = 10, db: Session = Depends(get_db)):
    engine = GraphEngine(db)
    central = engine.get_central_nodes(limit)
    return {"central_notes": [{"id": node_id, "centrality": score} for node_id, score in central]}

@router.get("/suggest/{note_id}")
async def suggest_connections(note_id: int, limit: int = 5, db: Session = Depends(get_db)):
    engine = GraphEngine(db)
    suggestions = engine.suggest_connections(note_id, limit)
    return {"note_id": note_id, "suggestions": suggestions}
