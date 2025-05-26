import networkx as nx
from typing import List, Dict, Tuple
from sqlalchemy.orm import Session
from ..database import Note, Link

class GraphEngine:
    def __init__(self, db: Session):
        self.db = db
        self.graph = nx.Graph()
        self._build_graph()
    
    def _build_graph(self):
        """Build NetworkX graph from database"""
        # Add nodes
        notes = self.db.query(Note).all()
        for note in notes:
            self.graph.add_node(note.id, title=note.title, content=note.content)
        
        # Add edges
        links = self.db.query(Link).all()
        for link in links:
            self.graph.add_edge(link.from_note_id, link.to_note_id, strength=link.strength)
    
    def get_connected_notes(self, note_id: int) -> List[int]:
        """Get all notes connected to given note"""
        if note_id in self.graph:
            return list(self.graph.neighbors(note_id))
        return []
    
    def get_orphan_notes(self) -> List[int]:
        """Find notes with no connections"""
        return [node for node in self.graph.nodes() if self.graph.degree(node) == 0]
    
    def get_central_nodes(self, limit: int = 10) -> List[Tuple[int, float]]:
        """Get most connected notes"""
        centrality = nx.degree_centrality(self.graph)
        sorted_nodes = sorted(centrality.items(), key=lambda x: x[1], reverse=True)
        return sorted_nodes[:limit]
    
    def suggest_connections(self, note_id: int, limit: int = 5) -> List[int]:
        """Suggest notes that might be related"""
        if note_id not in self.graph:
            return []
        
        # Get neighbors of neighbors (2-hop connections)
        suggestions = []
        neighbors = set(self.graph.neighbors(note_id))
        
        for neighbor in neighbors:
            second_hop = set(self.graph.neighbors(neighbor))
            suggestions.extend(second_hop - neighbors - {note_id})
        
        # Remove duplicates and limit results
        unique_suggestions = list(set(suggestions))
        return unique_suggestions[:limit]
    
    def get_graph_data(self) -> Dict:
        """Export graph data for visualization"""
        nodes = []
        for node_id in self.graph.nodes():
            node_data = self.graph.nodes[node_id]
            nodes.append({
                "id": node_id,
                "title": node_data.get("title", f"Note {node_id}"),
                "connections": self.graph.degree(node_id)
            })
        
        links = []
        for edge in self.graph.edges(data=True):
            links.append({
                "source": edge[0],
                "target": edge[1],
                "strength": edge[2].get("strength", 1)
            })
        
        return {"nodes": nodes, "links": links}
