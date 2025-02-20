from neo4j import GraphDatabase  # Ensure this import is accurate
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

    def init_app(self, app):
        self.driver = GraphDatabase.driver(
            app.config['NEO4J_URI'],
            auth=(app.config['NEO4J_USER'], app.config['NEO4J_PASSWORD'])
        )

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

    def test_connection(self):
        with self.driver.session() as session:
            result = session.run("RETURN 1")
            return result.single()[0] == 1

    def run_query(self, query, parameters=None):
        with self.driver.session() as session:
            return session.run(query, parameters)
