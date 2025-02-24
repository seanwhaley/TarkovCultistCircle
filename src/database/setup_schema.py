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
                # Core entity constraints
                "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.uid IS UNIQUE",
                "CREATE CONSTRAINT vendor_name_unique IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE",
                "CREATE CONSTRAINT material_name_unique IF NOT EXISTS FOR (m:Material) REQUIRE m.name IS UNIQUE",
                "CREATE CONSTRAINT trade_id_unique IF NOT EXISTS FOR (t:Trade) REQUIRE t.uid IS UNIQUE",
                
                # Property existence constraints
                "CREATE CONSTRAINT item_required_props IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS NOT NULL",
                "CREATE CONSTRAINT vendor_required_props IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS NOT NULL",
                "CREATE CONSTRAINT price_history_required_props IF NOT EXISTS FOR (p:PriceHistory) REQUIRE p.price_rub IS NOT NULL",
                "CREATE CONSTRAINT armor_required_props IF NOT EXISTS FOR (a:Armor) REQUIRE a.class_level IS NOT NULL",
                "CREATE CONSTRAINT weapon_stats_required_props IF NOT EXISTS FOR (w:WeaponStats) REQUIRE w.caliber IS NOT NULL"
            ]
            
            for constraint in constraints:
                try:
                    db.execute(constraint)
                except ClientError as e:
                    if "There already exists an index" not in str(e):
                        raise
            
            # Create indexes
            indexes = [
                # Basic lookup indexes
                "CREATE INDEX item_name IF NOT EXISTS FOR (i:Item) ON (i.name)",
                "CREATE INDEX item_normalized_name IF NOT EXISTS FOR (i:Item) ON (i.normalized_name)",
                "CREATE INDEX vendor_normalized_name IF NOT EXISTS FOR (v:Vendor) ON (v.normalized_name)",
                
                # Composite indexes for optimization
                "CREATE INDEX item_price_range IF NOT EXISTS FOR (i:Item) ON (i.base_price, i.last_low_price)",
                "CREATE INDEX trade_type_level IF NOT EXISTS FOR (t:Trade) ON (t.trade_type, t.level)",
                
                # Temporal indexes
                "CREATE INDEX price_history_timestamp IF NOT EXISTS FOR (p:PriceHistory) ON (p.recorded_at)",
                "CREATE INDEX trade_timestamp IF NOT EXISTS FOR (t:Trade) ON (t.created_at)",
                
                # Category and type indexes
                "CREATE INDEX item_category IF NOT EXISTS FOR (i:Item) ON (i.category)",
                "CREATE INDEX item_type IF NOT EXISTS FOR (i:Item) ON (i.type)",
                
                # Property-specific indexes
                "CREATE INDEX armor_class IF NOT EXISTS FOR (a:Armor) ON (a.class_level)",
                "CREATE INDEX weapon_caliber IF NOT EXISTS FOR (w:WeaponStats) ON (w.caliber)"
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
            expected_constraints = {
                "item_id_unique", "vendor_name_unique", "material_name_unique",
                "trade_id_unique", "item_required_props", "vendor_required_props",
                "price_history_required_props", "armor_required_props",
                "weapon_stats_required_props"
            }
            missing_constraints = expected_constraints - constraints
            if missing_constraints:
                issues.append(f"Missing constraints: {', '.join(missing_constraints)}")

            # Check indexes
            result = db.query("SHOW INDEXES")
            indexes = {record["name"] for record in result}
            expected_indexes = {
                "item_name", "item_normalized_name", "vendor_normalized_name",
                "item_price_range", "trade_type_level", "price_history_timestamp",
                "trade_timestamp", "item_category", "item_type", "armor_class",
                "weapon_caliber"
            }
            missing_indexes = expected_indexes - indexes
            if missing_indexes:
                issues.append(f"Missing indexes: {', '.join(missing_indexes)}")

            # Verify node types
            result = db.query("MATCH (n) RETURN distinct labels(n) as labels")
            node_types = {label for record in result for label in record["labels"]}
            expected_types = {
                "Item", "Vendor", "Material", "Trade", "PriceHistory",
                "Armor", "WeaponStats"
            }
            if missing_types:
                issues.append(f"Missing node types: {', '.join(missing_types)}")

        except Exception as e:
            issues.append(f"Schema verification failed: {str(e)}")

        return issues

    def optimize_indexes(self) -> None:
        """Optimize database indexes."""
        try:
            # Force index population
            db.execute("CALL db.index.fulltext.awaitEventuallyConsistency(300)")
            
            # Analyze index usage
            result = db.query("""
                CALL db.stats.retrieve('DETAILED INDEX STATS')
                YIELD stats
                RETURN stats
            """)
            
            # Log index statistics
            logger.info("Index optimization complete")
            logger.debug(f"Index statistics: {result}")
            
        except Exception as e:
            logger.error(f"Index optimization failed: {str(e)}")
            raise

schema_manager = DatabaseSchema()