import requests
import os
import time
from typing import Dict, Any
from src.kg.service import GraphService

class SystemHealthCheck:
    """Utility to check health of system components."""
    
    @staticmethod
    def check_neo4j() -> Dict[str, Any]:
        """Check Neo4j connection."""
        uri = os.getenv("NEO4J_URI")
        user = os.getenv("NEO4J_USER")
        password = os.getenv("NEO4J_PASSWORD")
        
        start = time.time()
        try:
            service = GraphService(uri, user, password)
            stats = service.get_stats()
            latency = (time.time() - start) * 1000
            
            if stats.is_connected:
                return {"status": "online", "latency": f"{latency:.0f}ms", "details": f"{stats.node_count} nodes"}
            else:
                return {"status": "offline", "latency": "-", "details": "Connection failed"}
        except Exception as e:
            return {"status": "error", "latency": "-", "details": str(e)}

    @staticmethod
    def check_api(name: str, url: str, method: str = "GET", json_data: Dict = None) -> Dict[str, Any]:
        """Ping an external API."""
        start = time.time()
        try:
            if method == "POST":
                response = requests.post(url, json=json_data, timeout=5)
            else:
                response = requests.get(url, timeout=5)
                
            latency = (time.time() - start) * 1000
            
            if response.status_code < 500:
                return {"status": "online", "latency": f"{latency:.0f}ms", "details": f"Status {response.status_code}"}
            else:
                return {"status": "degraded", "latency": f"{latency:.0f}ms", "details": f"Status {response.status_code}"}
        except Exception as e:
            return {"status": "offline", "latency": "-", "details": "Unreachable"}

    @classmethod
    def run_all_checks(cls) -> Dict[str, Dict[str, Any]]:
        """Run all health checks."""
        from src import config
        return {
            "Neo4j Database": cls.check_neo4j(),
            "OpenFDA API": cls.check_api("OpenFDA", f"{config.OPENFDA_LABEL_URL}?limit=1"),
            "MyGene.info": cls.check_api("MyGene.info", f"{config.MYGENE_URL.replace('/query', '/metadata')}"),
            "DGIdb": cls.check_api("DGIdb", config.DGIDB_URL, method="POST", json_data={'query': '{ genes(names: ["TP53"]) { nodes { name } } }'}),
            "PubChem": cls.check_api("PubChem", f"{config.PUBCHEM_URL}/aspirin/JSON"),
        }
