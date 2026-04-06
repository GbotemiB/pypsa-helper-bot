"""CLI entrypoint for the PyPSA Helper Bot."""

import argparse
import sys


def main():
    """Main CLI entrypoint."""
    parser = argparse.ArgumentParser(
        prog="pypsa-bot",
        description="PyPSA Discord Helper Bot — AI-powered community support",
    )
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # --- `run` command ---
    subparsers.add_parser("run", help="Start the Discord bot")

    # --- `ingest` command ---
    ingest_parser = subparsers.add_parser(
        "ingest", help="Run the document ingestion pipeline"
    )
    ingest_parser.add_argument(
        "--incremental",
        action="store_true",
        help="Only ingest new/updated content (skip already-indexed URLs)",
    )
    ingest_parser.add_argument(
        "--repo",
        type=str,
        default=None,
        help="Only ingest a specific repository (e.g., 'pypsa', 'pypsa-eur')",
    )

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        sys.exit(1)

    if args.command == "run":
        _run_bot()
    elif args.command == "ingest":
        _run_ingest(incremental=args.incremental, repo=args.repo)


def _run_bot():
    """Start the Discord bot."""
    from pypsa_bot.config import config

    config.validate(require_discord=True, require_groq=True)

    from pypsa_bot.bot.client import start_bot

    start_bot(config)


def _run_ingest(incremental: bool = False, repo: str | None = None):
    """Run the ingestion pipeline."""
    from pypsa_bot.config import config

    config.validate(require_discord=False, require_groq=False)

    from pypsa_bot.ingestion.processor import run_ingestion

    run_ingestion(config, incremental=incremental, target_repo=repo)


if __name__ == "__main__":
    main()
