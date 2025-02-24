"""Store the project analysis report in Neo4j."""
import json
import logging
from pathlib import Path
from src.database import db
from src.utils.prompt_storage import PromptResponseStorage

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def store_analysis_report():
    """Store the analysis report in Neo4j."""
    try:
        # Initialize storage
        storage = PromptResponseStorage(db)
        
        # Read the analysis report
        report_path = Path(__file__).parent.parent.parent / 'storage' / 'responses' / 'project_analysis_2024_02.json'
        with open(report_path, 'r') as f:
            report_data = json.load(f)
        
        # Validate and store the report
        if storage.validate_report_format(report_data):
            prompt_id = storage.store_analysis_report(report_data)
            logger.info(f"Successfully stored analysis report with ID: {prompt_id}")
            return prompt_id
        else:
            logger.error("Report validation failed")
            return None
            
    except Exception as e:
        logger.error(f"Failed to store analysis report: {str(e)}")
        raise

if __name__ == '__main__':
    store_analysis_report()