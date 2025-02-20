from src.services.item_service import ItemService

class ServiceFactory:
    @staticmethod
    def create_item_service():
        return ItemService()
