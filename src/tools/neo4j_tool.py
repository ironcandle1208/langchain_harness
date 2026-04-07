"""Neo4j query execution tool for LangChain agent."""

from __future__ import annotations

from typing import Any, Optional

from langchain_core.tools import tool
from neo4j import GraphDatabase

from src.config import NEO4J_DATABASE, NEO4J_PASSWORD, NEO4J_URI, NEO4J_USERNAME


class Neo4jClient:
    """Thin wrapper around the Neo4j driver."""

    def __init__(
        self,
        uri: str = NEO4J_URI,
        username: str = NEO4J_USERNAME,
        password: str = NEO4J_PASSWORD,
        database: str = NEO4J_DATABASE,
    ) -> None:
        self._driver = GraphDatabase.driver(uri, auth=(username, password))
        self._database = database

    def close(self) -> None:
        self._driver.close()

    def run_query(self, query: str, params: Optional[dict[str, Any]] = None) -> list[dict[str, Any]]:
        """Execute a Cypher query and return the results as a list of dicts."""
        with self._driver.session(database=self._database) as session:
            result = session.run(query, parameters=params or {})
            return [record.data() for record in result]

    def get_schema(self) -> str:
        """Return a human-readable summary of the graph schema."""
        node_labels = self.run_query("CALL db.labels() YIELD label RETURN label")
        rel_types = self.run_query("CALL db.relationshipTypes() YIELD relationshipType RETURN relationshipType")
        properties = self.run_query(
            "CALL db.schema.nodeTypeProperties() YIELD nodeType, propertyName, propertyTypes "
            "RETURN nodeType, propertyName, propertyTypes"
        )

        lines: list[str] = []
        lines.append("=== Node Labels ===")
        for row in node_labels:
            lines.append(f"  :{row['label']}")

        lines.append("\n=== Relationship Types ===")
        for row in rel_types:
            lines.append(f"  :{row['relationshipType']}")

        lines.append("\n=== Node Properties ===")
        for row in properties:
            lines.append(f"  {row['nodeType']}.{row['propertyName']} : {row['propertyTypes']}")

        return "\n".join(lines)


# ---------------------------------------------------------------------------
# Module-level singleton – created lazily so import doesn't require a running
# Neo4j instance.
# ---------------------------------------------------------------------------
_client: Optional[Neo4jClient] = None


def _get_client() -> Neo4jClient:
    global _client
    if _client is None:
        _client = Neo4jClient()
    return _client


def set_client(client: Neo4jClient) -> None:
    """Allow callers to inject a pre-configured client."""
    global _client
    _client = client


# ---------------------------------------------------------------------------
# LangChain Tools
# ---------------------------------------------------------------------------

@tool
def neo4j_query(query: str) -> str:
    """Execute a Cypher query against the Neo4j database and return the results.

    Args:
        query: A valid Cypher query string to execute against the Neo4j database.

    Returns:
        Query results formatted as a string. Each record is printed on its own line.
    """
    try:
        records = _get_client().run_query(query)
        if not records:
            return "Query executed successfully. No records returned."
        lines = [str(record) for record in records]
        return f"Returned {len(records)} record(s):\n" + "\n".join(lines)
    except Exception as e:
        return f"Error executing query: {e}"


@tool
def neo4j_schema() -> str:
    """Retrieve the schema of the Neo4j database.

    Returns node labels, relationship types, and property information.
    Use this tool first to understand the graph structure before writing queries.
    """
    try:
        return _get_client().get_schema()
    except Exception as e:
        return f"Error retrieving schema: {e}"
