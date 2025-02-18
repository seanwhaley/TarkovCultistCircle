from src.db import Neo4jDB

class ExtensionsManager:
    _instance: "ExtensionsManager | None" = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExtensionsManager, cls).__new__(cls)
            cls._instance.db = Neo4jDB()
        return cls._instance

    @classmethod
    def get_db(cls):
        return cls().db

extensions = ExtensionsManager()
