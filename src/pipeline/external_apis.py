import requests
import logging
import os
from typing import Optional, Dict, Any, List
import src.config as config

logger = logging.getLogger(__name__)

class ClinVarClient:
    """Client for fetching ClinVar data via NCBI E-utilities."""
    
    BASE_URL = config.CLINVAR_API_URL
    
    def __init__(self, email: Optional[str] = None):
        self.email = email or os.getenv("CLINVAR_API_EMAIL")
        if not self.email:
            logger.warning("CLINVAR_API_EMAIL not set. API requests may be limited.")

    def get_variant_summary(self, variant_id: str) -> Dict[str, Any]:
        """
        Fetch variant summary from ClinVar.
        Note: This is a simplified implementation. Real ClinVar queries 
        often require searching by HGVS or VCV ID first.
        """
        # For MVP, we'll simulate a query or return empty if no ID format match
        # In a real implementation, we would:
        # 1. esearch.fcgi to get ID from term
        # 2. esummary.fcgi to get details
        return {}

class GnomADClient:
    """Client for fetching gnomAD data via GraphQL."""
    
    API_URL = config.GNOMAD_API_URL
    
    def get_variant_frequency(self, chrom: str, pos: int, ref: str, alt: str) -> Optional[float]:
        """
        Fetch allele frequency from gnomAD.
        """
        query = """
        query GnomadVariant($variantId: String!) {
            variant(variantId: $variantId, dataset: gnomad_r2_1) {
                genome {
                    af
                }
                exome {
                    af
                }
            }
        }
        """
        variant_id = f"{chrom}-{pos}-{ref}-{alt}"
        
        try:
            response = requests.post(
                self.API_URL,
                json={'query': query, 'variables': {'variantId': variant_id}},
                timeout=5
            )
            if response.status_code == 200:
                data = response.json()
                # Extract AF logic here
                return 0.0 # Placeholder
        except Exception as e:
            logger.error(f"gnomAD API error: {e}")
            return None
        return None

class OpenFDAClient:
    """Client for fetching drug data from openFDA."""
    
    BASE_URL = config.OPENFDA_EVENT_URL
    LABEL_URL = config.OPENFDA_LABEL_URL
    
    def get_adverse_events(self, drug_name: str, limit: int = 5) -> List[Dict[str, Any]]:
        """
        Fetch recent adverse events for a drug.
        """
        # Try searching by harmonized brand name first (more reliable)
        params = {
            'search': f'patient.drug.openfda.brand_name:"{drug_name}"',
            'limit': limit
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
            
            # Fallback: Try medicinalproduct if brand_name fails
            params['search'] = f'patient.drug.medicinalproduct:"{drug_name}"'
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            if response.status_code == 200:
                data = response.json()
                return data.get('results', [])
                
        except Exception as e:
            logger.error(f"openFDA API error: {e}")
            return []
        return []

    def get_drug_label(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch FDA drug label (indications, warnings).
        """
        params = {
            'search': f'openfda.brand_name:"{drug_name}"',
            'limit': 1
        }
        
        try:
            response = requests.get(self.LABEL_URL, params=params, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                if results:
                    return results[0]
        except Exception as e:
            logger.error(f"openFDA Label API error: {e}")
            return None
        return None

    def search_drugs(self, query: str, limit: int = 10) -> List[str]:
        """
        Search for drug brand names matching the query.
        """
        if not query or len(query) < 3:
            return []
            
        # Use count endpoint to get unique brand names
        params = {
            'search': f'openfda.brand_name:"{query}*"',
            'count': 'openfda.brand_name.exact',
            'limit': limit
        }
        
        try:
            response = requests.get(self.LABEL_URL, params=params, timeout=5)
            if response.status_code == 200:
                results = response.json().get('results', [])
                # Extract term (drug name) from results
                return [item['term'].title() for item in results]
        except Exception as e:
            logger.error(f"openFDA Search API error: {e}")
            return []
        return []

class MyGeneInfoClient:
    """Client for fetching gene data from MyGene.info."""
    
    BASE_URL = config.MYGENE_URL
    
    def search_gene(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Search for a gene by symbol.
        """
        params = {
            'q': f'symbol:{symbol}',
            'fields': 'symbol,name,map_location,summary',
            'species': 'human',
            'limit': 1
        }
        
        try:
            response = requests.get(self.BASE_URL, params=params, timeout=5)
            if response.status_code == 200:
                hits = response.json().get('hits', [])
                if hits:
                    return hits[0]
        except Exception as e:
            logger.error(f"MyGene.info API error: {e}")
            return None
        return None

class DGIdbClient:
    """Client for fetching gene-drug interactions from DGIdb (GraphQL)."""
    
    BASE_URL = config.DGIDB_URL
    
    def get_interactions(self, gene_symbol: str) -> List[Dict[str, Any]]:
        """
        Fetch drug interactions for a gene.
        """
        query = """
        query($names: [String]!) {
            genes(names: $names) {
                nodes {
                    name
                    interactions {
                        drug { name }
                    }
                }
            }
        }
        """
        try:
            response = requests.post(self.BASE_URL, json={'query': query, 'variables': {'names': [gene_symbol]}}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                nodes = data.get('data', {}).get('genes', {}).get('nodes', [])
                if nodes:
                    # Transform to match expected format: [{'drugName': '...'}, ...]
                    interactions = nodes[0].get('interactions', [])
                    return [{'drugName': i['drug']['name']} for i in interactions if i.get('drug')]
        except Exception as e:
            logger.error(f"DGIdb GraphQL error: {e}")
        return []

    def get_genes_for_drug(self, drug_name: str) -> List[Dict[str, Any]]:
        """
        Fetch gene interactions for a drug.
        """
        query = """
        query($names: [String]!) {
            drugs(names: $names) {
                nodes {
                    name
                    interactions {
                        gene { name }
                    }
                }
            }
        }
        """
        try:
            response = requests.post(self.BASE_URL, json={'query': query, 'variables': {'names': [drug_name]}}, timeout=5)
            if response.status_code == 200:
                data = response.json()
                nodes = data.get('data', {}).get('drugs', {}).get('nodes', [])
                if nodes:
                    # Transform to match expected format: [{'geneName': '...', 'geneLongName': '...'}, ...]
                    interactions = nodes[0].get('interactions', [])
                    return [{'geneName': i['gene']['name'], 'geneLongName': i['gene']['name']} for i in interactions if i.get('gene')]
        except Exception as e:
            logger.error(f"DGIdb GraphQL error: {e}")
        return []

class PubChemClient:
    """Client for fetching chemical data from PubChem."""
    
    BASE_URL = config.PUBCHEM_URL
    
    def get_compound_data(self, drug_name: str) -> Optional[Dict[str, Any]]:
        """
        Fetch compound data (CID, formula, weight) from PubChem.
        """
        url = f"{self.BASE_URL}/{drug_name}/JSON"
        
        try:
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                data = response.json()
                compounds = data.get('PC_Compounds', [])
                if compounds:
                    return compounds[0]
        except Exception as e:
            logger.error(f"PubChem API error: {e}")
            return None
        return None
