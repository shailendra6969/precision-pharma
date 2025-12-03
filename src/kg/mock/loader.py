from typing import List, Dict
from src.kg.models import Gene, Drug, Variant, GraphStats

class MockDataLoader:
    """Deterministic mock data provider for offline mode."""
    
    @staticmethod
    def get_genes() -> List[Gene]:
        return [
            Gene(id="CYP2C19", label="Gene", symbol="CYP2C19", name="Cytochrome P450 2C19", chromosome="10"),
            Gene(id="CYP2D6", label="Gene", symbol="CYP2D6", name="Cytochrome P450 2D6", chromosome="22"),
            Gene(id="VKORC1", label="Gene", symbol="VKORC1", name="Vitamin K epoxide reductase", chromosome="16"),
        ]
        
    @staticmethod
    def get_drugs() -> List[Drug]:
        return [
            Drug(id="Clopidogrel", label="Drug", name="Clopidogrel", drugbank_id="DB00758"),
            Drug(id="Warfarin", label="Drug", name="Warfarin", drugbank_id="DB00682"),
            Drug(id="Omeprazole", label="Drug", name="Omeprazole", drugbank_id="DB00338"),
        ]
        
    @staticmethod
    def get_variants() -> List[Variant]:
        return [
            Variant(id="rs12248560", label="Variant", variant_id="rs12248560", clinvar_significance="Pathogenic", cadd_score=25.0),
            Variant(id="rs9923231", label="Variant", variant_id="rs9923231", clinvar_significance="Likely Pathogenic", cadd_score=22.5),
        ]

    @staticmethod
    def get_stats() -> GraphStats:
        return GraphStats(
            node_count=150,
            edge_count=320,
            latency_ms=0.0,
            is_connected=False
        )
