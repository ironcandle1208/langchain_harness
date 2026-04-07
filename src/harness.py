"""LangChain harness – builds and runs an agent with Neo4j tools."""

from __future__ import annotations

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

from src.config import LLM_MODEL, LLM_TEMPERATURE, OLLAMA_BASE_URL
from src.tools.neo4j_tool import neo4j_query, neo4j_schema

SYSTEM_PROMPT = """\
You are a helpful assistant that can query a Neo4j graph database.

Available tools:
- neo4j_schema: Retrieve the database schema (node labels, relationship types, properties).
- neo4j_query: Execute a Cypher query against the database.

Workflow:
1. If the user asks about the data, first call neo4j_schema to understand the graph structure.
2. Write and execute Cypher queries using neo4j_query.
3. Summarise the results in natural language for the user.

Always confirm destructive operations (CREATE, DELETE, MERGE, SET, REMOVE) with the user before executing them.\
"""

TOOLS = [neo4j_query, neo4j_schema]


def build_agent() -> AgentExecutor:
    """Create and return a LangChain agent executor."""
    llm = ChatOllama(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        base_url=OLLAMA_BASE_URL,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="chat_history", optional=True),
        ("human", "{input}"),
        MessagesPlaceholder(variable_name="agent_scratchpad"),
    ])

    agent = create_tool_calling_agent(llm, TOOLS, prompt)
    return AgentExecutor(agent=agent, tools=TOOLS, verbose=True)


def run_agent_once(agent: AgentExecutor, user_input: str) -> str:
    """Send a single user message and return the final assistant response."""
    result = agent.invoke({"input": user_input})
    return result["output"]


def run_interactive(agent: AgentExecutor) -> None:
    """Run a REPL-style interactive loop."""
    chat_history: list = []
    print("Neo4j LangChain Harness (type 'exit' to quit)")
    print("=" * 50)

    while True:
        try:
            user_input = input("\nYou: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        result = agent.invoke({"input": user_input, "chat_history": chat_history})
        print(f"\nAssistant: {result['output']}")
        chat_history.append(("human", user_input))
        chat_history.append(("ai", result["output"]))
