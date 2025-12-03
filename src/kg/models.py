from pydantic import BaseModel, Field
from typing import List, Optional, Any

class GraphNode(BaseModel):
    """Base model for graph nodes."""
    id: str
    label: str
    properties: dict = Field(default_factory=dict)

class Gene(GraphNode):
    """Gene entity."""
    symbol: str
    name: Optional[str] = None
    chromosome: Optional[str] = None
    
class Drug(GraphNode):
    """Drug entity."""
    name: str
    drugbank_id: Optional[str] = None
    
class Variant(GraphNode):
    """Variant entity."""
    variant_id: str
    clinvar_significance: Optional[str] = None
    cadd_score: Optional[float] = None

class GraphEdge(BaseModel):
    """Base model for graph edges."""
    source: str
    target: str
    type: str
    properties: dict = Field(default_factory=dict)

class GraphStats(BaseModel):
    """Statistics for the knowledge graph."""
    node_count: int
    edge_count: int
    latency_ms: float
    is_connected: bool
