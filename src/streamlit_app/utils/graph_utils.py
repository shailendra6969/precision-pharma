import streamlit as st
import os
from dotenv import load_dotenv
from src.kg.service import GraphService as KGService

load_dotenv()

class GraphService:
    """Service for Knowledge Graph interactions."""
    
    @staticmethod
    @st.cache_resource(show_spinner=False)
    def get_client():
        """Initialize KG client from environment variables."""
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            # Use the high-level service from src.kg.service
            service = KGService(uri, user, password)
            # Check connection (get_stats is a good proxy or we can add verify_connection to it)
            stats = service.get_stats()
            if stats.is_connected:
                return service
            return None
        except Exception as e:
            return None

    @staticmethod
    def is_connected(client) -> bool:
        """Check if client is connected."""
        return client is not None
