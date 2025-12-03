import logging
import time
from typing import List, Optional, Dict, Any
from neo4j import GraphDatabase
from src.kg.models import Gene, Drug, Variant, GraphStats
from src.kg.mock.loader import MockDataLoader

logger = logging.getLogger(__name__)

class GraphService:
    """
    Service layer for Knowledge Graph interactions.
    Handles connection management, query execution, and mock fallback.
    """
    
    def __init__(self, uri: str, user: str, password: str):
        self.uri = uri
        self.user = user
        self.password = password
        self.driver = None
        self.is_connected = False
        self._connect()

    def _connect(self):
        """Establish connection to Neo4j."""
        try:
            self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
            self.driver.verify_connectivity()
            self.is_connected = True
            logger.info(f"Connected to Neo4j at {self.uri}")
        except Exception as e:
            logger.warning(f"Failed to connect to Neo4j: {e}. Switching to Mock Mode.")
            self.is_connected = False

    def close(self):
        """Close the driver."""
        if self.driver:
            self.driver.close()

    def get_stats(self) -> GraphStats:
        """Get graph statistics (node/edge counts)."""
        start_time = time.time()
        
        if not self.is_connected:
            return MockDataLoader.get_stats()
            
        try:
            with self.driver.session() as session:
                node_count = session.run("MATCH (n) RETURN count(n) as count").single()["count"]
                edge_count = session.run("MATCH ()-[r]->() RETURN count(r) as count").single()["count"]
                
            latency = (time.time() - start_time) * 1000
            return GraphStats(
                node_count=node_count,
                edge_count=edge_count,
                latency_ms=latency,
                is_connected=True
            )
        except Exception as e:
            logger.error(f"Error fetching stats: {e}")
            return MockDataLoader.get_stats()

    def search_gene(self, symbol: str) -> Optional[Gene]:
        """Search for a gene by symbol (Neo4j first, then External API)."""
        # 1. Try Neo4j
        if self.is_connected:
            try:
                with self.driver.session() as session:
                    result = session.run(
                        "MATCH (g:Gene) WHERE toLower(g.symbol) = toLower($symbol) RETURN g",
                        symbol=symbol
                    ).single()
                    
                    if result:
                        node = result["g"]
                        return Gene(
                            id=node.element_id,
                            label="Gene",
                            symbol=node.get("symbol"),
                            name=node.get("name"),
                            chromosome=node.get("chromosome")
                        )
            except Exception as e:
                logger.error(f"Error searching gene in Neo4j: {e}")

        # 2. Try External API (MyGene.info)
        try:
            from src.pipeline.external_apis import MyGeneInfoClient
            client = MyGeneInfoClient()
            data = client.search_gene(symbol)
            
            if data:
                return Gene(
                    id=f"external_{data.get('_id')}",
                    label="Gene",
                    symbol=data.get("symbol"),
                    name=data.get("name"),
                    chromosome=data.get("map_location")
                )
        except Exception as e:
            logger.error(f"Error searching external gene: {e}")
            
        # 3. Mock Fallback (if everything else fails and we are in mock mode)
        if not self.is_connected:
            for gene in MockDataLoader.get_genes():
                if gene.symbol.lower() == symbol.lower():
                    return gene
            
        return None

    def find_related_drugs(self, gene_symbol: str) -> List[Drug]:
        """Find drugs related to a gene (Neo4j first, then External API)."""
        drugs = []
        
        # 1. Try Neo4j
        if self.is_connected:
            try:
                with self.driver.session() as session:
                    result = session.run("""
                        MATCH (g:Gene {symbol: $symbol})-[:HAS_VARIANT]->(:Variant)-[:AFFECTS]->(d:Drug)
                        RETURN DISTINCT d
                    """, symbol=gene_symbol)
                    
                    for record in result:
                        node = record["d"]
                        drugs.append(Drug(
                            id=node.element_id,
                            label="Drug",
                            name=node.get("name"),
                            drugbank_id=node.get("drugbank_id")
                        ))
            except Exception as e:
                logger.error(f"Error finding related drugs in Neo4j: {e}")

        # 2. If no drugs found locally, try External API (DGIdb)
        if not drugs:
            try:
                from src.pipeline.external_apis import DGIdbClient
                client = DGIdbClient()
                interactions = client.get_interactions(gene_symbol)
                
                for interaction in interactions:
                    drug_name = interaction.get('drugName')
                    if drug_name:
                        drugs.append(Drug(
                            id=f"external_{drug_name}",
                            label="Drug",
                            name=drug_name.title(),
                            drugbank_id=None # DGIdb doesn't always provide this
                        ))
            except Exception as e:
                logger.error(f"Error finding external drugs: {e}")
            
        # 3. Mock Fallback
        if not drugs and not self.is_connected:
             return MockDataLoader.get_drugs()
            
        return drugs

    def get_drug_details(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """Fetch detailed drug info from PubChem."""
        try:
            from src.pipeline.external_apis import PubChemClient
            client = PubChemClient()
            data = client.get_compound_data(drug_name)
            
            if data:
                props = data.get('props', [])
                details = {
                    "cid": data.get('id', {}).get('id', {}).get('cid'),
                    "formula": next((p['value']['sval'] for p in props if p['urn']['label'] == 'Molecular Formula'), "N/A"),
                    "weight": next((p['value']['fval'] for p in props if p['urn']['label'] == 'Molecular Weight'), "N/A"),
                    "iupac_name": next((p['value']['sval'] for p in props if p['urn']['label'] == 'IUPAC Name' and p['urn'].get('name') == 'Preferred'), "N/A")
                }
                return details
        except Exception as e:
            logger.error(f"Error fetching drug details: {e}")
            
        return None

    def search_drug(self, name: str) -> Optional[Drug]:
        """Search for a drug by name (Neo4j first, then External API)."""
        # 1. Try Neo4j
        if self.is_connected:
            try:
                with self.driver.session() as session:
                    result = session.run(
                        "MATCH (d:Drug) WHERE toLower(d.name) = toLower($name) RETURN d",
                        name=name
                    ).single()
                    
                    if result:
                        node = result["d"]
                        return Drug(
                            id=node.element_id,
                            label="Drug",
                            name=node.get("name"),
                            drugbank_id=node.get("drugbank_id")
                        )
            except Exception as e:
                logger.error(f"Error searching drug in Neo4j: {e}")

        # 2. Try External API (OpenFDA/PubChem)
        try:
            from src.pipeline.external_apis import OpenFDAClient
            client = OpenFDAClient()
            # Verify existence via search
            results = client.search_drugs(name, limit=1)
            
            if results:
                found_name = results[0]
                
                # Try to get generic name for better context
                generic_name = None
                try:
                    label = client.get_drug_label(found_name)
                    if label and 'openfda' in label:
                        generic_names = label['openfda'].get('generic_name', [])
                        if generic_names:
                            generic_name = generic_names[0]
                except Exception:
                    pass

                drug = Drug(
                    id=f"external_{found_name}",
                    label="Drug",
                    name=found_name,
                    drugbank_id=None
                )
                if generic_name:
                    drug.properties['generic_name'] = generic_name
                    
                return drug
        except Exception as e:
            logger.error(f"Error searching external drug: {e}")
            
        return None

    def find_related_genes(self, drug_name: str) -> List[Gene]:
        """Find genes related to a drug (Neo4j first, then External API)."""
        genes = []
        
        # 1. Try Neo4j
        if self.is_connected:
            try:
                with self.driver.session() as session:
                    result = session.run("""
                        MATCH (d:Drug {name: $name})<-[:AFFECTS]-(:Variant)<-[:HAS_VARIANT]-(g:Gene)
                        RETURN DISTINCT g
                    """, name=drug_name)
                    
                    for record in result:
                        node = record["g"]
                        genes.append(Gene(
                            id=node.element_id,
                            label="Gene",
                            symbol=node.get("symbol"),
                            name=node.get("name"),
                            chromosome=node.get("chromosome")
                        ))
            except Exception as e:
                logger.error(f"Error finding related genes in Neo4j: {e}")

        # 2. If no genes found locally, try External API (DGIdb)
        if not genes:
            try:
                from src.pipeline.external_apis import DGIdbClient, OpenFDAClient
                client = DGIdbClient()
                interactions = client.get_genes_for_drug(drug_name)
                
                # FALLBACK: If no interactions, try to find generic name via OpenFDA
                if not interactions:
                    try:
                        fda_client = OpenFDAClient()
                        label = fda_client.get_drug_label(drug_name)
                        if label and 'openfda' in label:
                            generic_names = label['openfda'].get('generic_name', [])
                            if generic_names:
                                generic_name = generic_names[0]
                                logger.info(f"Trying generic name for {drug_name}: {generic_name}")
                                interactions = client.get_genes_for_drug(generic_name)
                    except Exception as e:
                        logger.warning(f"Failed to fetch generic name fallback: {e}")

                for interaction in interactions:
                    gene_symbol = interaction.get('geneName')
                    if gene_symbol:
                        genes.append(Gene(
                            id=f"external_{gene_symbol}",
                            label="Gene",
                            symbol=gene_symbol,
                            name=interaction.get('geneLongName'),
                            chromosome=None
                        ))
            except Exception as e:
                logger.error(f"Error finding external genes: {e}")
            
        return genes
