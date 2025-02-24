"""Tests for prompt storage functionality."""
import unittest
from unittest.mock import Mock
from src.utils.prompt_storage import PromptResponseStorage
from src.database.neo4j import Neo4jDB

class TestPromptStorage(unittest.TestCase):
    def setUp(self):
        self.mock_db = Mock(spec=Neo4jDB)
        self.storage = PromptResponseStorage(self.mock_db)

    def test_import_to_neo4j_success(self):
        """Test importing JSON data to Neo4j successfully."""
        test_data = {
            "type": "analysis",
            "data": {
                "analysis_report": {
                    "executive_summary": "Test summary",
                    "inferred_requirements": ["req1", "req2"],
                    "code_quality": {"test": "value"},
                    "tech_stack": {"test": "value"},
                    "recommendations": []
                }
            }
        }

        self.mock_db.store_prompt_response.return_value = "test_prompt_id"
        prompt_id = self.storage.import_to_neo4j(test_data)

        self.assertEqual(prompt_id, "test_prompt_id")
        self.mock_db.store_prompt_response.assert_called_once_with(
            response_type=test_data["type"],
            data=test_data["data"],
            parent_id=None
        )

    def test_get_prompt_by_id_exists(self):
        """Test retrieving an existing prompt from Neo4j."""
        test_prompt = {
            "prompt_id": "test_id",
            "type": "analysis",
            "data": {"test": "value"}
        }
        self.mock_db.query.return_value = [{"p": test_prompt}]

        result = self.storage.get_prompt_by_id("test_id")
        self.assertEqual(result, test_prompt)

    def test_get_prompt_by_id_not_found(self):
        """Test retrieving a non-existent prompt from Neo4j."""
        self.mock_db.query.return_value = []
        result = self.storage.get_prompt_by_id("nonexistent_id")
        self.assertIsNone(result)

    def test_validate_report_format_valid(self):
        """Test validating a correctly formatted analysis report."""
        valid_prompt = {
            "prompt_id": "test_id",
            "timestamp": "2024-03-20T12:00:00",
            "type": "analysis",
            "data": {
                "analysis_report": {
                    "executive_summary": "Test summary",
                    "inferred_requirements": ["req1"],
                    "code_quality": {},
                    "tech_stack": {},
                    "recommendations": []
                }
            }
        }
        self.assertTrue(self.storage.validate_report_format(valid_prompt))

    def test_validate_report_format_invalid(self):
        """Test validating an incorrectly formatted analysis report."""
        invalid_prompt = {
            "prompt_id": "test_id",
            "timestamp": "2024-03-20T12:00:00",
            "type": "analysis",
            "data": {
                "analysis_report": {
                    "executive_summary": "Test summary"
                    # Missing required sections
                }
            }
        }
        self.assertFalse(self.storage.validate_report_format(invalid_prompt))

    def test_validate_report_format_wrong_type(self):
        """Test validating a prompt with wrong type."""
        wrong_type_prompt = {
            "prompt_id": "test_id",
            "timestamp": "2024-03-20T12:00:00",
            "type": "action_plan",
            "data": {}
        }
        self.assertFalse(self.storage.validate_report_format(wrong_type_prompt))