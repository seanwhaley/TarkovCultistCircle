"""Storage utilities for AI prompt responses."""
import logging
from typing import Dict, Any, Optional, List
from datetime import datetime
from src.database.neo4j import Neo4jDB

logger = logging.getLogger(__name__)

class PromptResponseStorage:
    """Handles storage and validation of AI prompt responses."""

    def __init__(self, db: Neo4jDB):
        self.db = db

    def import_to_neo4j(self, json_data: Dict[str, Any]) -> str:
        """Import a JSON prompt response into Neo4j."""
        try:
            return self.db.store_prompt_response(
                response_type=json_data['type'],
                data=json_data['data'],
                parent_id=json_data.get('parent_analysis_id')
            )
        except Exception as e:
            logger.error(f"Error importing prompt response to Neo4j: {str(e)}")
            raise

    def get_prompt_by_id(self, prompt_id: str) -> Optional[Dict[str, Any]]:
        """Retrieve a specific prompt by ID from Neo4j."""
        try:
            result = self.db.query(
                """
                MATCH (p:PromptResponse {prompt_id: $prompt_id})
                RETURN p
                """,
                {"prompt_id": prompt_id}
            )
            return result[0]["p"] if result else None
        except Exception as e:
            logger.error(f"Error retrieving prompt from Neo4j: {str(e)}")
            return None

    def validate_report_format(self, prompt: Dict[str, Any]) -> bool:
        """Validate the format of an analysis report."""
        if prompt.get('type') != 'analysis':
            return False

        required_fields = {
            'prompt_id': str,
            'timestamp': str,
            'type': str,
            'data': dict
        }

        # Check required fields and types
        for field, field_type in required_fields.items():
            if field not in prompt or not isinstance(prompt[field], field_type):
                return False

        # Check analysis report structure
        report = prompt['data'].get('analysis_report', {})
        required_report_sections = [
            'executive_summary',
            'inferred_requirements',
            'code_quality',
            'tech_stack',
            'recommendations'
        ]

        for section in required_report_sections:
            if section not in report:
                return False

        return True