"""Neo4j database schema setup and maintenance."""
from typing import List
from neo4j.exceptions import ClientError
from src.database import db
import logging

logger = logging.getLogger(__name__)

class DatabaseSchema:
    """Manages Neo4j database schema setup and verification."""

    def setup_schema(self, force: bool = False) -> None:
        """Set up the database schema."""
        try:
            if force:
                db.execute("MATCH (n) DETACH DELETE n")
            
            # Create constraints
            constraints = [
                "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
                "CREATE CONSTRAINT vendor_name_unique IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE",
                "CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
                "CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT trade_id_unique IF NOT EXISTS FOR (t:Trade) REQUIRE t.id IS UNIQUE",
                "CREATE CONSTRAINT item_required_props IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS NOT NULL",
                "CREATE CONSTRAINT item_name_exists IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS NOT NULL"
            ]
            
            for constraint in constraints:
                try:
                    db.execute(constraint)
                except ClientError as e:
                    if "There already exists an index" not in str(e):
                        raise
            
            # Create indexes
            indexes = [
                "CREATE INDEX item_name IF NOT EXISTS FOR (i:Item) ON (i.name)",
                "CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name)",
                "CREATE INDEX category_id IF NOT EXISTS FOR (c:Category) ON (c.id)",
                "CREATE INDEX task_id IF NOT EXISTS FOR (t:Task) ON (t.id)",
                "CREATE INDEX station_name IF NOT EXISTS FOR (s:Station) ON (s.name)",
                "CREATE INDEX trade_id IF NOT EXISTS FOR (t:Trade) ON (t.id)",
                "CREATE INDEX item_price_idx IF NOT EXISTS FOR (i:Item) ON (i.basePrice, i.lastLowPrice)",
                "CREATE INDEX trade_type_level IF NOT EXISTS FOR (t:Trade) ON (t.type, t.level)"
            ]
            
            for index in indexes:
                try:
                    db.execute(index)
                except ClientError as e:
                    if "There already exists an index" not in str(e):
                        raise

        except Exception as e:
            logger.error(f"Failed to set up schema: {str(e)}")
            raise

    def verify_schema(self) -> List[str]:
        """Verify schema setup and return any issues found."""
        issues: List[str] = []
        try:
            # Check constraints
            result = db.query("SHOW CONSTRAINTS")
            constraints = {record["name"] for record in result}
            expected_constraints = {"item_id_unique", "vendor_name_unique", "category_id_unique"}
            missing_constraints = expected_constraints - constraints
            if missing_constraints:
                issues.append(f"Missing constraints: {', '.join(missing_constraints)}")

            # Check indexes
            result = db.query("SHOW INDEXES")
            indexes = {record["name"] for record in result}
            expected_indexes = {"item_name", "vendor_name", "category_id"}
            missing_indexes = expected_indexes - indexes
            if missing_indexes:
                issues.append(f"Missing indexes: {', '.join(missing_indexes)}")

            # Verify node types
            result = db.query("MATCH (n) RETURN distinct labels(n) as labels")
            node_types = {label for record in result for label in record["labels"]}
            expected_types = {"Item", "Vendor", "Category", "Task", "Trade"}
            missing_types = expected_types - node_types
            if missing_types:
                issues.append(f"Missing node types: {', '.join(missing_types)}")

        except Exception as e:
            issues.append(f"Schema verification failed: {str(e)}")

        return issues