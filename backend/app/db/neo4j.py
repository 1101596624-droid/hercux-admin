from neo4j import AsyncGraphDatabase
from app.core.config import settings


class Neo4jClient:
    """Neo4j database client for skill tree and dependencies"""

    def __init__(self):
        self.driver = None

    async def connect(self):
        """Initialize Neo4j connection"""
        self.driver = AsyncGraphDatabase.driver(
            settings.NEO4J_URI,
            auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
        )

    async def close(self):
        """Close Neo4j connection"""
        if self.driver:
            await self.driver.close()

    async def execute_query(self, query: str, parameters: dict = None):
        """Execute a Cypher query"""
        async with self.driver.session() as session:
            result = await session.run(query, parameters or {})
            return await result.data()


# Global Neo4j client instance
neo4j_client = Neo4jClient()


async def get_neo4j():
    """Dependency to get Neo4j client"""
    return neo4j_client
