"""Neo4j database schema setup and maintenance."""

from typing import Dict, Any, Optional, NoReturn, List, Type, TypeVar, Union
from types import TracebackType
from neo4j import GraphDatabase, Session, TransactionError
from neo4j.exceptions import ConstraintError, ClientError
from src.config.settings import Settings
from src.services.exceptions import ValidationError

SCHEMA_SETUP = """
// Clean existing schema
MATCH (n) DETACH DELETE n;

// Create constraints
CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE;
CREATE CONSTRAINT vendor_name_unique IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE;
CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE;
CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE;
CREATE CONSTRAINT trade_id_unique IF NOT EXISTS FOR (t:Trade) REQUIRE t.id IS UNIQUE;

CREATE CONSTRAINT item_required_props IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS NOT NULL;
CREATE CONSTRAINT item_name_exists IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS NOT NULL;
CREATE CONSTRAINT vendor_name_exists IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS NOT NULL;

// Create indexes
CREATE INDEX item_id IF NOT EXISTS FOR (i:Item) ON (i.id);
CREATE INDEX item_name IF NOT EXISTS FOR (i:Item) ON (i.name);
CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name);
CREATE INDEX category_id IF NOT EXISTS FOR (c:Category) ON (c.id);
CREATE INDEX task_id IF NOT EXISTS FOR (t:Task) ON (t.id);
CREATE INDEX station_name IF NOT EXISTS FOR (s:Station) ON (s.name);
CREATE INDEX trade_id IF NOT EXISTS FOR (t:Trade) ON (t.id);

CREATE INDEX item_price_idx IF NOT EXISTS FOR (i:Item) ON (i.basePrice, i.lastLowPrice);
CREATE INDEX trade_type_level IF NOT EXISTS FOR (t:Trade) ON (t.type, t.level);
"""

ITEM_CREATION = """
MERGE (i:Item {id: $id})
SET i += $properties

WITH i

// Create category relationship
FOREACH (cat IN $categories |
    MERGE (c:Category {id: cat.id})
    SET c += cat
    MERGE (i)-[:IN_CATEGORY]->(c)
)

// Create vendor relationships for buying
FOREACH (trade IN $buyFor |
    MERGE (v:Vendor {name: trade.vendor.name})
    SET v.normalizedName = trade.vendor.normalizedName
    CREATE (t:Trade {
        id: apoc.create.uuid(),
        type: 'buy',
        source: trade.source,
        price: trade.price,
        currency: trade.currency,
        priceRUB: trade.priceRUB
    })
    CREATE (i)-[:CAN_BUY_FROM]->(t)-[:FROM_VENDOR]->(v)
    FOREACH (req IN trade.requirements |
        CREATE (r:Requirement {type: req.type, value: req.value})
        CREATE (t)-[:REQUIRES]->(r)
    )
)

// Create vendor relationships for selling
FOREACH (trade IN $sellFor |
    MERGE (v:Vendor {name: trade.vendor.name})
    SET v.normalizedName = trade.vendor.normalizedName
    CREATE (t:Trade {
        id: apoc.create.uuid(),
        type: 'sell',
        source: trade.source,
        price: trade.price,
        currency: trade.currency,
        priceRUB: trade.priceRUB
    })
    CREATE (i)-[:CAN_SELL_TO]->(t)-[:TO_VENDOR]->(v)
)

// Create barter relationships
FOREACH (barter IN $bartersFor |
    MERGE (v:Vendor {name: barter.trader.name})
    CREATE (t:Trade {
        id: barter.id,
        type: 'barter',
        level: barter.level
    })
    CREATE (i)<-[:GIVES]-(t)-[:AVAILABLE_AT]->(v)
    FOREACH (task IN [barter.taskUnlock] |
        WHEN task IS NOT NULL
        MERGE (ut:Task {id: task.id})
        SET ut.name = task.name
        CREATE (t)-[:UNLOCKED_BY]->(ut)
    )
)

// Create craft relationships
FOREACH (craft IN $craftsFor |
    MERGE (s:Station {name: craft.station.name})
    CREATE (t:Trade {
        id: craft.id,
        type: 'craft',
        level: craft.level
    })
    CREATE (i)<-[:PRODUCES]-(t)-[:AT_STATION]->(s)
    FOREACH (task IN [craft.taskUnlock] |
        WHEN task IS NOT NULL
        MERGE (ut:Task {id: task.id})
        SET ut.name = task.name
        CREATE (t)-[:UNLOCKED_BY]->(ut)
    )
)

// Create task usage relationships
FOREACH (task IN $usedInTasks |
    MERGE (t:Task {id: task.id})
    SET t.name = task.name
    MERGE (v:Vendor {name: task.trader.name})
    CREATE (i)-[:USED_IN]->(t)-[:GIVEN_BY]->(v)
)

// Create contained items relationships
FOREACH (contained IN $containsItems |
    MERGE (ci:Item {id: contained.item.id})
    SET ci.name = contained.item.name
    CREATE (i)-[:CONTAINS {count: contained.count}]->(ci)
)

// Create armor properties if they exist
FOREACH (armor IN [i.properties.armor] |
    WHEN armor IS NOT NULL
    CREATE (a:Armor {
        class: armor.class,
        zones: armor.zones,
        durability: armor.durability
    })
    CREATE (i)-[:HAS_ARMOR]->(a)
    MERGE (m:Material {name: armor.material.name})
    SET m.destructibility = armor.material.destructibility
    CREATE (a)-[:MADE_OF]->(m)
)

// Create weapon properties if they exist
FOREACH (weapon IN [i.properties.weaponStats] |
    WHEN weapon IS NOT NULL
    CREATE (w:WeaponStats {
        caliber: weapon.caliber,
        firerate: weapon.firerate,
        ergonomics: weapon.ergonomics,
        recoilVertical: weapon.recoilVertical,
        recoilHorizontal: weapon.recoilHorizontal
    })
    CREATE (i)-[:HAS_STATS]->(w)
)
"""

T = TypeVar('T')

class DatabaseSchema:
    def __init__(self) -> None:
        config = Settings()
        self.uri: str = config.neo4j_uri
        self.user: str = config.neo4j_user
        self.password: str = config.neo4j_password
        self._driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
        self._setup_retries: int = 3
        self._session: Optional[Session] = None

    def __enter__(self) -> 'DatabaseSchema':
        return self

    def __exit__(
        self,
        exc_type: Optional[Type[BaseException]],
        exc_val: Optional[BaseException],
        exc_tb: Optional[TracebackType]
    ) -> None:
        self.close()

    def close(self) -> None:
        """Close the database driver."""
        if self._session:
            self._session.close()
        if hasattr(self, '_driver'):
            self._driver.close()

    def setup_schema(self, force: bool = False) -> None:
        """Set up the database schema with retry logic."""
        retries = self._setup_retries
        last_error: Optional[Exception] = None

        while retries > 0:
            try:
                with self._driver.session() as session:
                    if force:
                        session.run("MATCH (n) DETACH DELETE n")
                    self._create_constraints(session)
                    self._create_indexes(session)
                    return
            except (ConstraintError, ClientError) as e:
                last_error = e
                retries -= 1
                if retries > 0:
                    print(f"Retrying schema setup. {retries} attempts remaining")
                continue
            except Exception as e:
                raise ValidationError(f"Failed to set up database schema: {str(e)}")

        if last_error:
            raise ValidationError(f"Failed to set up schema after {self._setup_retries} attempts: {str(last_error)}")

    def _create_constraints(self, session: Session) -> None:
        """Create database constraints in correct order."""
        constraints: List[str] = [
            # Unique identifier constraints
            "CREATE CONSTRAINT item_id_unique IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS UNIQUE",
            "CREATE CONSTRAINT vendor_name_unique IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS UNIQUE",
            "CREATE CONSTRAINT category_id_unique IF NOT EXISTS FOR (c:Category) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT task_id_unique IF NOT EXISTS FOR (t:Task) REQUIRE t.id IS UNIQUE",
            "CREATE CONSTRAINT trade_id_unique IF NOT EXISTS FOR (t:Trade) REQUIRE t.id IS UNIQUE",
            
            # Property existence constraints
            "CREATE CONSTRAINT item_required_props IF NOT EXISTS FOR (i:Item) REQUIRE i.id IS NOT NULL",
            "CREATE CONSTRAINT item_name_exists IF NOT EXISTS FOR (i:Item) REQUIRE i.name IS NOT NULL",
            "CREATE CONSTRAINT vendor_name_exists IF NOT EXISTS FOR (v:Vendor) REQUIRE v.name IS NOT NULL",
            
            # Relationship property constraints
            "CREATE CONSTRAINT trade_price_valid IF NOT EXISTS FOR (t:Trade) REQUIRE t.priceRUB IS NOT NULL",
            "CREATE CONSTRAINT contains_count_valid IF NOT EXISTS FOR ()-[r:CONTAINS]-() REQUIRE r.count IS NOT NULL"
        ]
        
        for constraint in constraints:
            try:
                session.run(constraint)
            except ClientError as e:
                if "An equivalent constraint already exists" not in str(e):
                    raise

    def _create_indexes(self, session: Session) -> None:
        """Create database indexes in correct order."""
        indexes: List[str] = [
            # Primary indexes
            "CREATE INDEX item_name IF NOT EXISTS FOR (i:Item) ON (i.name)",
            "CREATE INDEX vendor_name IF NOT EXISTS FOR (v:Vendor) ON (v.name)",
            "CREATE INDEX category_id IF NOT EXISTS FOR (c:Category) ON (c.id)",
            "CREATE INDEX task_id IF NOT EXISTS FOR (t:Task) ON (t.id)",
            "CREATE INDEX station_name IF NOT EXISTS FOR (s:Station) ON (s.name)",
            "CREATE INDEX trade_id IF NOT EXISTS FOR (t:Trade) ON (t.id)",
            
            # Composite indexes
            "CREATE INDEX item_price_idx IF NOT EXISTS FOR (i:Item) ON (i.basePrice, i.lastLowPrice)",
            "CREATE INDEX trade_type_level IF NOT EXISTS FOR (t:Trade) ON (t.type, t.level)",
            
            # Full-text indexes for search
            "CREATE FULLTEXT INDEX item_search IF NOT EXISTS FOR (i:Item) ON EACH [i.name, i.shortName]",
            
            # Array indexes
            "CREATE INDEX item_types IF NOT EXISTS FOR (i:Item) ON (i.types)"
        ]
        
        for index in indexes:
            try:
                session.run(index)
            except ClientError as e:
                if "There already exists an index" not in str(e):
                    raise

    def verify_schema(self) -> List[str]:
        """Verify schema setup and return any issues found."""
        issues: List[str] = []
        try:
            with self._driver.session() as session:
                # Check constraints
                result = session.run("SHOW CONSTRAINTS")
                constraints = {record["name"] for record in result}
                expected_constraints = {"item_id_unique", "vendor_name_unique", "category_id_unique"}
                missing_constraints = expected_constraints - constraints
                if missing_constraints:
                    issues.append(f"Missing constraints: {', '.join(missing_constraints)}")

                # Check indexes
                result = session.run("SHOW INDEXES")
                indexes = {record["name"] for record in result}
                expected_indexes = {"item_name", "vendor_name", "category_id"}
                missing_indexes = expected_indexes - indexes
                if missing_indexes:
                    issues.append(f"Missing indexes: {', '.join(missing_indexes)}")

                # Verify node existence
                result = session.run("MATCH (n) RETURN distinct labels(n) as labels")
                node_types = {label for record in result for label in record["labels"]}
                expected_types = {"Item", "Vendor", "Category", "Task", "Trade"}
                missing_types = expected_types - node_types
                if missing_types:
                    issues.append(f"Missing node types: {', '.join(missing_types)}")

        except Exception as e:
            issues.append(f"Schema verification failed: {str(e)}")

        return issues

    def create_or_update_item(self, item_data: Dict[str, Any]) -> None:
        """Create or update an item with all its relationships."""
        with self._driver.session() as session:
            session.run(
                ITEM_CREATION,
                id=item_data['id'],
                properties={
                    'name': item_data['name'],
                    'shortName': item_data.get('shortName'),
                    'basePrice': item_data['basePrice'],
                    'updated': item_data['updated'],
                    'width': item_data.get('width'),
                    'height': item_data.get('height'),
                    'weight': item_data.get('weight'),
                    'iconLink': item_data.get('iconLink'),
                    'imageLink': item_data.get('imageLink'),
                    'wikiLink': item_data.get('wikiLink'),
                    'changeLast24h': item_data.get('changeLast24h'),
                    'changeLast48h': item_data.get('changeLast48h'),
                    'low24h': item_data.get('low24h'),
                    'high24h': item_data.get('high24h'),
                    'lastLowPrice': item_data.get('lastLowPrice'),
                    'avg24hPrice': item_data.get('avg24hPrice'),
                    'types': item_data.get('types', [])
                },
                categories=[item_data.get('category')] if item_data.get('category') else [],
                buyFor=item_data.get('buyFor', []),
                sellFor=item_data.get('sellFor', []),
                bartersFor=item_data.get('bartersFor', []),
                craftsFor=item_data.get('craftsFor', []),
                usedInTasks=item_data.get('usedInTasks', []),
                containsItems=item_data.get('containsItems', [])
            )

    def cleanup(self) -> None:
        """Clean up the database (for testing purposes)."""
        try:
            with self._driver.session() as session:
                session.run("MATCH (n) DETACH DELETE n")
        except Exception as e:
            raise ValidationError(f"Failed to clean up database: {str(e)}")