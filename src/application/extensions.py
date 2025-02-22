from src.core.db import Neo4jConnection, get_db

class ExtensionsManager:
    _instance = None
    _initialized = False
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ExtensionsManager, cls).__new__(cls)
        return cls._instance

    def __init__(self):
        if not self._initialized:
            self.db = get_db()
            self._initialized = True
    
    @classmethod
    def get_db(cls) -> Neo4jConnection:
        return cls().db

extensions = ExtensionsManager()
