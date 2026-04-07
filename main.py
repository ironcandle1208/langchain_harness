"""Entry point for the Neo4j LangChain Harness."""

import argparse
import sys

from src.harness import build_agent, run_agent_once, run_interactive


def main() -> None:
    parser = argparse.ArgumentParser(description="Neo4j LangChain Harness")
    parser.add_argument(
        "-q", "--query",
        type=str,
        default=None,
        help="Run a single query and exit (non-interactive mode).",
    )
    args = parser.parse_args()

    agent = build_agent()

    if args.query:
        answer = run_agent_once(agent, args.query)
        print(answer)
    else:
        run_interactive(agent)


if __name__ == "__main__":
    main()
