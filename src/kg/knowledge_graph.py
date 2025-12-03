"""
Neo4j Knowledge Graph for Pharmacogenomics
Manages gene-variant-drug-disease relationships and interactions.
"""

from neo4j import GraphDatabase
from typing import List, Dict, Any, Optional
import logging
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class Gene:
    """Represents a gene node in the KG."""
    symbol: str
    name: Optional[str] = None
    chromosome: Optional[str] = None
    is_drug_metabolizer: bool = False


@dataclass
class Variant:
    """Represents a variant node in the KG."""
    variant_id: str
    chrom: str
    pos: int
    ref: str
    alt: str
    clinvar_significance: Optional[str] = None
    cadd_score: Optional[float] = None


@dataclass
class Drug:
    """Represents a drug node in the KG."""
    name: str
    drugbank_id: Optional[str] = None
    atc_code: Optional[str] = None


@dataclass
class Disease:
    """Represents a disease/indication node in the KG."""
    name: str
    icd10_code: Optional[str] = None


class KnowledgeGraphManager:
    """Manage Neo4j knowledge graph for pharmacogenomics."""
    
    def __init__(self, uri: str, user: str, password: str):
        """
        Initialize KG manager with Neo4j credentials.
        
        Args:
            uri: Neo4j connection URI (e.g., "neo4j://localhost:7687")
            user: Neo4j username
            password: Neo4j password
        """
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        logger.info(f"Connected to Neo4j at {uri}")
    
    def close(self):
        """Close database connection."""
        self.driver.close()
        
    def verify_connection(self) -> bool:
        """Verify that the connection to Neo4j is active."""
        try:
            self.driver.verify_connectivity()
            return True
        except Exception as e:
            logger.error(f"Failed to verify Neo4j connection: {e}")
            return False
    
    def clear_database(self):
        """Clear all nodes and relationships (for testing)."""
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")
        logger.info("Cleared Neo4j database")
    
    # ===== Node Creation =====
    
    def create_gene(self, gene: Gene) -> Dict[str, Any]:
        """Create or update a Gene node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (g:Gene {symbol: $symbol})
                SET g.name = $name,
                    g.chromosome = $chromosome,
                    g.is_drug_metabolizer = $is_drug_metabolizer
                RETURN g
            """, {
                'symbol': gene.symbol,
                'name': gene.name,
                'chromosome': gene.chromosome,
                'is_drug_metabolizer': gene.is_drug_metabolizer,
            })
            return result.single()[0]
    
    def create_variant(self, variant: Variant) -> Dict[str, Any]:
        """Create or update a Variant node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (v:Variant {variant_id: $variant_id})
                SET v.chrom = $chrom,
                    v.pos = $pos,
                    v.ref = $ref,
                    v.alt = $alt,
                    v.clinvar_significance = $clinvar_significance,
                    v.cadd_score = $cadd_score
                RETURN v
            """, {
                'variant_id': variant.variant_id,
                'chrom': variant.chrom,
                'pos': variant.pos,
                'ref': variant.ref,
                'alt': variant.alt,
                'clinvar_significance': variant.clinvar_significance,
                'cadd_score': variant.cadd_score,
            })
            return result.single()[0]
    
    def create_drug(self, drug: Drug) -> Dict[str, Any]:
        """Create or update a Drug node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (d:Drug {name: $name})
                SET d.drugbank_id = $drugbank_id,
                    d.atc_code = $atc_code
                RETURN d
            """, {
                'name': drug.name,
                'drugbank_id': drug.drugbank_id,
                'atc_code': drug.atc_code,
            })
            return result.single()[0]
    
    def create_disease(self, disease: Disease) -> Dict[str, Any]:
        """Create or update a Disease node."""
        with self.driver.session() as session:
            result = session.run("""
                MERGE (d:Disease {name: $name})
                SET d.icd10_code = $icd10_code
                RETURN d
            """, {
                'name': disease.name,
                'icd10_code': disease.icd10_code,
            })
            return result.single()[0]
    
    # ===== Relationship Creation =====
    
    def link_variant_to_gene(self, variant_id: str, gene_symbol: str):
        """Create HAS_VARIANT relationship between Gene and Variant."""
        with self.driver.session() as session:
            session.run("""
                MATCH (g:Gene {symbol: $gene_symbol})
                MATCH (v:Variant {variant_id: $variant_id})
                MERGE (g)-[:HAS_VARIANT]->(v)
            """, {
                'gene_symbol': gene_symbol,
                'variant_id': variant_id,
            })
    
    def link_variant_to_drug(self, variant_id: str, drug_name: str, 
                            effect_type: str = 'affects',
                            evidence_count: int = 1,
                            pmids: List[str] = None):
        """
        Create AFFECTS relationship between Variant and Drug.
        
        Args:
            variant_id: Variant ID
            drug_name: Drug name
            effect_type: Type of effect (e.g., 'increases_metabolism', 'decreases_response')
            evidence_count: Number of supporting studies
            pmids: PubMed IDs for evidence
        """
        with self.driver.session() as session:
            session.run("""
                MATCH (v:Variant {variant_id: $variant_id})
                MATCH (d:Drug {name: $drug_name})
                MERGE (v)-[r:AFFECTS]->(d)
                SET r.effect_type = $effect_type,
                    r.evidence_count = $evidence_count,
                    r.pmids = $pmids
            """, {
                'variant_id': variant_id,
                'drug_name': drug_name,
                'effect_type': effect_type,
                'evidence_count': evidence_count,
                'pmids': pmids or [],
            })
    
    def link_drug_to_disease(self, drug_name: str, disease_name: str, indication: str = 'treats'):
        """Create TREATS relationship between Drug and Disease."""
        with self.driver.session() as session:
            session.run("""
                MATCH (d:Drug {name: $drug_name})
                MATCH (dis:Disease {name: $disease_name})
                MERGE (d)-[r:TREATS]->(dis)
                SET r.type = $indication
            """, {
                'drug_name': drug_name,
                'disease_name': disease_name,
                'indication': indication,
            })
    
    # ===== Query Methods =====
    
    def find_variants_for_gene(self, gene_symbol: str) -> List[Dict]:
        """Find all variants for a given gene."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Gene {symbol: $symbol})-[:HAS_VARIANT]->(v:Variant)
                RETURN v.variant_id as variant_id,
                       v.clinvar_significance as significance,
                       v.cadd_score as cadd_score
                ORDER BY v.cadd_score DESC
            """, {'symbol': gene_symbol})
            return [dict(record) for record in result]
    
    def find_drugs_for_variant(self, variant_id: str) -> List[Dict]:
        """Find all drugs affected by a variant."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (v:Variant {variant_id: $variant_id})-[r:AFFECTS]->(d:Drug)
                RETURN d.name as drug_name,
                       r.effect_type as effect_type,
                       r.evidence_count as evidence_count
                ORDER BY r.evidence_count DESC
            """, {'variant_id': variant_id})
            return [dict(record) for record in result]
    
    def find_gene_drug_interactions(self, gene_symbol: str, drug_name: str) -> List[Dict]:
        """Find interactions between a gene and drug."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Gene {symbol: $gene_symbol})-[:HAS_VARIANT]->(v:Variant)-[r:AFFECTS]->(d:Drug {name: $drug_name})
                RETURN v.variant_id as variant_id,
                       v.clinvar_significance as significance,
                       r.effect_type as effect_type,
                       r.evidence_count as evidence_count
                ORDER BY r.evidence_count DESC
            """, {
                'gene_symbol': gene_symbol,
                'drug_name': drug_name,
            })
            return [dict(record) for record in result]
    
    def find_drug_indications(self, drug_name: str) -> List[Dict]:
        """Find diseases/indications for a drug."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (d:Drug {name: $drug_name})-[r:TREATS]->(dis:Disease)
                RETURN dis.name as disease,
                       dis.icd10_code as icd10_code,
                       r.type as indication_type
            """, {'drug_name': drug_name})
            return [dict(record) for record in result]
    
    def find_pathways(self, gene_symbol: str) -> List[Dict]:
        """Find connected genes and drugs (2-hop neighborhood)."""
        with self.driver.session() as session:
            result = session.run("""
                MATCH (g:Gene {symbol: $symbol})-[:HAS_VARIANT]->(v:Variant)-[r:AFFECTS]->(d:Drug)
                RETURN DISTINCT d.name as drug,
                       COUNT(DISTINCT v) as num_variants,
                       COUNT(DISTINCT r) as num_interactions
                ORDER BY num_interactions DESC
                LIMIT 10
            """, {'symbol': gene_symbol})
            return [dict(record) for record in result]
    
    def get_statistics(self) -> Dict[str, int]:
        """Get overall KG statistics."""
        with self.driver.session() as session:
            stats = {}
            
            # Count nodes
            for label in ['Gene', 'Variant', 'Drug', 'Disease']:
                result = session.run(f"MATCH (n:{label}) RETURN count(n) as count")
                stats[f'{label.lower()}_count'] = result.single()['count']
            
            # Count relationships
            result = session.run("MATCH ()-[r:AFFECTS]->() RETURN count(r) as count")
            stats['variant_drug_links'] = result.single()['count']
            
            return stats


def ingest_mock_data(kg: KnowledgeGraphManager):
    """Ingest mock pharmacogenomics data for demonstration."""
    
    # Create genes
    genes = [
        Gene('CYP2C19', 'Cytochrome P450 2C19', '19', is_drug_metabolizer=True),
        Gene('CYP2C9', 'Cytochrome P450 2C9', '10', is_drug_metabolizer=True),
        Gene('CYP2D6', 'Cytochrome P450 2D6', '22', is_drug_metabolizer=True),
        Gene('VKORC1', 'Vitamin K epoxide reductase complex subunit 1', '16', is_drug_metabolizer=True),
    ]
    for gene in genes:
        kg.create_gene(gene)
    
    # Create variants
    variants = [
        Variant('chr10:94761930:G>A', '10', 94761930, 'G', 'A', 'likely_pathogenic', 25.3),
        Variant('chr22:42127942:C>T', '22', 42127942, 'C', 'T', 'benign', 5.2),
        Variant('chr19:49503616:G>C', '19', 49503616, 'G', 'C', 'likely_pathogenic', 22.1),
    ]
    for variant in variants:
        kg.create_variant(variant)
    
    # Create drugs
    drugs = [
        Drug('warfarin', 'DB00682'),
        Drug('omeprazole', 'DB00338'),
        Drug('clopidogrel', 'DB00758'),
    ]
    for drug in drugs:
        kg.create_drug(drug)
    
    # Create diseases
    diseases = [
        Disease('Atrial Fibrillation', 'I48'),
        Disease('Gastroesophageal Reflux Disease', 'K21'),
        Disease('Acute Coronary Syndrome', 'I24'),
    ]
    for disease in diseases:
        kg.create_disease(disease)
    
    # Link variants to genes
    kg.link_variant_to_gene('chr10:94761930:G>A', 'CYP2C9')
    kg.link_variant_to_gene('chr22:42127942:C>T', 'CYP2D6')
    kg.link_variant_to_gene('chr19:49503616:G>C', 'CYP2C19')
    
    # Link variants to drugs
    kg.link_variant_to_drug('chr10:94761930:G>A', 'warfarin', 
                           'decreases_metabolism', 5, ['12345678', '12345679'])
    kg.link_variant_to_drug('chr19:49503616:G>C', 'omeprazole',
                           'increases_metabolism', 3, ['12345680'])
    kg.link_variant_to_drug('chr22:42127942:C>T', 'clopidogrel',
                           'affects_response', 4, ['12345681', '12345682'])
    
    # Link drugs to diseases
    kg.link_drug_to_disease('warfarin', 'Atrial Fibrillation', 'treats')
    kg.link_drug_to_disease('omeprazole', 'Gastroesophageal Reflux Disease', 'treats')
    kg.link_drug_to_disease('clopidogrel', 'Acute Coronary Syndrome', 'treats')
    
    logger.info("Ingested mock pharmacogenomics data")
