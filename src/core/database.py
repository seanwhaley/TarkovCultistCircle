from neo4j import GraphDatabase
import logging
from contextlib import contextmanager
from typing import Optional, ClassVar

logger = logging.getLogger(__name__)

class Neo4jDB:
    _instance: ClassVar[Optional["Neo4jDB"]] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance.driver = None
            cls._instance.initialized = False
        return cls._instance

    def initialize(self, uri, user, password):
        if not self.initialized:
            try:
                self.driver = GraphDatabase.driver(uri, auth=(user, password))
                self.initialized = True
                logger.info("Neo4j database initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Neo4j: {str(e)}")
                raise

    @contextmanager
    def get_session(self):
        if not self.initialized:
            raise RuntimeError("Database not initialized")
        session = None
        try:
            session = self.driver.session()
            yield session
        finally:
            if session:
                session.close()

    def close(self):
        if self.driver:
            self.driver.close()
            self.initialized = False
            self.driver = None
