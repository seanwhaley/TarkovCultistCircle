import pytest
from src.services.item_service import ItemService
from src.services.exceptions import ValidationError, ItemNotFoundError

class TestItemService:
    @pytest.fixture
    def service(self):
        return ItemService()

    def test_validate_price(self, service):
        assert service.validate_price("100.50") == 100.50
        assert service.validate_price("1") == 1.0
        
        with pytest.raises(ValidationError):
            service.validate_price("invalid")
        with pytest.raises(ValidationError):
            service.validate_price("-1")
        with pytest.raises(ValidationError):
            service.validate_price("0")

    def test_validate_duration(self, service):
        assert service.validate_duration("24") == 24
        assert service.validate_duration("1") == 1
        
        with pytest.raises(ValidationError):
            service.validate_duration("invalid")
        with pytest.raises(ValidationError):
            service.validate_duration("-1")
        with pytest.raises(ValidationError):
            service.validate_duration("0")

    def test_override_price(self, service, db, sample_items):
        # Setup test data
        with db.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            session.run(
                """
                CREATE (i:Item {
                    uid: $uid,
                    name: $name,
                    base_price: $base_price
                })
                """,
                uid=sample_items[0]["uid"],
                name=sample_items[0]["name"],
                base_price=sample_items[0]["base_price"]
            )

        # Test valid price override
        service.override_price(sample_items[0]["uid"], "1500")
        
        with db.get_session() as session:
            result = session.run(
                "MATCH (i:Item {uid: $uid}) RETURN i.base_price",
                uid=sample_items[0]["uid"]
            )
            assert float(result.single()["i.base_price"]) == 1500.0

        # Test invalid item ID
        with pytest.raises(ItemNotFoundError):
            service.override_price("nonexistent", "1000")

    def test_blacklist_item(self, service, db, sample_items):
        # Setup test data
        with db.get_session() as session:
            session.run("MATCH (n) DETACH DELETE n")
            session.run(
                """
                CREATE (i:Item {
                    uid: $uid,
                    name: $name,
                    base_price: $base_price,
                    blacklisted: false
                })
                """,
                uid=sample_items[0]["uid"],
                name=sample_items[0]["name"],
                base_price=sample_items[0]["base_price"]
            )

        # Test blacklisting
        service.blacklist_item(sample_items[0]["uid"], "24")
        
        with db.get_session() as session:
            result = session.run(
                "MATCH (i:Item {uid: $uid}) RETURN i.blacklisted, i.blacklist_duration",
                uid=sample_items[0]["uid"]
            )
            record = result.single()
            assert record["i.blacklisted"] == True
            assert record["i.blacklist_duration"] == 24
