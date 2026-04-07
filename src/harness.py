"""LangChain harness – builds and runs an agent with Neo4j tools."""

from __future__ import annotations

from langchain_core.messages import HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI

from src.config import LLM_MODEL, LLM_TEMPERATURE, OPENAI_API_KEY
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


def build_agent():
    """Create and return a LangChain agent executor."""
    from langgraph.prebuilt import create_react_agent

    llm = ChatOpenAI(
        model=LLM_MODEL,
        temperature=LLM_TEMPERATURE,
        api_key=OPENAI_API_KEY,
    )

    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder(variable_name="messages"),
    ])

    agent = create_react_agent(
        model=llm,
        tools=TOOLS,
        prompt=prompt,
    )
    return agent


def run_agent_once(agent, user_input: str) -> str:
    """Send a single user message and return the final assistant response."""
    result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
    # The last message from the agent is the final answer.
    return result["messages"][-1].content


def run_interactive(agent) -> None:
    """Run a REPL-style interactive loop."""
    from langchain_core.messages import AIMessage

    messages: list = []
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

        messages.append(HumanMessage(content=user_input))
        result = agent.invoke({"messages": messages})
        ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
        if ai_messages:
            answer = ai_messages[-1].content
            print(f"\nAssistant: {answer}")
        messages = result["messages"]
