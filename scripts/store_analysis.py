"""Script to store analysis report in Neo4j."""
import os
import sys
import json
from pathlib import Path
import logging
from typing import Dict, Any
from neo4j import GraphDatabase
from uuid import uuid4
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jStorage:
    def __init__(self):
        self.uri = os.getenv('NEO4J_URI', 'bolt://neo4j:7687')  # Updated to use Docker service name
        self.user = os.getenv('NEO4J_USER', 'neo4j')
        self.password = os.getenv('NEO4J_PASSWORD', 'password')
        self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        
    def setup_schema(self):
        """Ensure required constraints and indexes exist."""
        with self.driver.session() as session:
            # Create constraints
            session.run("""
                CREATE CONSTRAINT prompt_response_id_unique IF NOT EXISTS 
                FOR (p:PromptResponse) REQUIRE p.prompt_id IS UNIQUE
            """)
            session.run("""
                CREATE CONSTRAINT prompt_response_required_props IF NOT EXISTS 
                FOR (p:PromptResponse) REQUIRE p.timestamp IS NOT NULL
            """)
            # Create indexes
            session.run("""
                CREATE INDEX prompt_response_timestamp IF NOT EXISTS 
                FOR (p:PromptResponse) ON (p.timestamp)
            """)
            session.run("""
                CREATE INDEX prompt_response_type IF NOT EXISTS 
                FOR (p:PromptResponse) ON (p.type)
            """)
            
    def store_analysis(self, data: Dict[str, Any]) -> str:
        """Store analysis report in Neo4j."""
        prompt_id = str(uuid4())
        
        with self.driver.session() as session:
            session.run("""
                CREATE (p:PromptResponse {
                    prompt_id: $prompt_id,
                    timestamp: datetime(),
                    type: 'analysis',
                    project_version: $project_version,
                    analysis_report: $data
                })
            """, {
                "prompt_id": prompt_id,
                "project_version": data.get("project_version", "unknown"),
                "data": data
            })
            
        return prompt_id
        
    def close(self):
        """Close the database connection."""
        self.driver.close()

def main():
    """Store the analysis report in Neo4j."""
    try:
        # Initialize storage
        storage = Neo4jStorage()
        storage.setup_schema()
        
        # Read analysis report
        project_root = Path(__file__).parent.parent
        report_path = project_root / 'storage' / 'responses' / 'project_analysis_2024_02.json'
        with open(report_path) as f:
            analysis_data = json.load(f)
        
        # Store in Neo4j
        prompt_id = storage.store_analysis(analysis_data)
        logger.info(f"Successfully stored analysis with ID: {prompt_id}")
        
        # Clean up
        storage.close()
        return 0
        
    except Exception as e:
        logger.error(f"Error storing analysis: {str(e)}")
        return 1

if __name__ == '__main__':
    sys.exit(main())