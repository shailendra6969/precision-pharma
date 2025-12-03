import streamlit as st
import os
from src.kg.knowledge_graph import KnowledgeGraphManager

class GraphService:
    """Service for Knowledge Graph interactions."""
    
    @staticmethod
    @st.cache_resource
    def get_client():
        """Initialize KG client from environment variables."""
        uri = os.getenv("NEO4J_URI", "bolt://localhost:7687")
        user = os.getenv("NEO4J_USER", "neo4j")
        password = os.getenv("NEO4J_PASSWORD", "password")
        
        try:
            return KnowledgeGraphManager(uri, user, password)
        except Exception:
            return None

    @staticmethod
    def is_connected(client) -> bool:
        """Check if client is connected."""
        return client is not None
