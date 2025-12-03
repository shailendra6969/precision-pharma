import pytest
from unittest.mock import MagicMock, patch
from src.kg.knowledge_graph import KnowledgeGraphManager, Gene, Variant

@pytest.fixture
def mock_driver():
    with patch('neo4j.GraphDatabase.driver') as mock:
        yield mock

def test_kg_manager_init(mock_driver):
    kg = KnowledgeGraphManager("bolt://localhost:7687", "user", "pass")
    assert kg.driver is not None

def test_create_gene(mock_driver):
    kg = KnowledgeGraphManager("bolt://localhost:7687", "user", "pass")
    
    # Mock session and result
    mock_session = MagicMock()
    kg.driver.session.return_value.__enter__.return_value = mock_session
    mock_result = MagicMock()
    mock_session.run.return_value = mock_result
    mock_result.single.return_value = [{'symbol': 'CYP2C19'}]
    
    gene = Gene(symbol='CYP2C19', is_drug_metabolizer=True)
    result = kg.create_gene(gene)
    
    assert result['symbol'] == 'CYP2C19'
    mock_session.run.assert_called_once()
