"""Entry point: load config, setup Postgres, build graph, run Aiogram bot."""

import asyncio
import logging
import os

from dotenv import load_dotenv

from src.graph.workflow import build_workflow
from src.persistence.postgres import get_checkpointer, setup_database
from src.telegram_bot.bot import run_bot

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
)
logger = logging.getLogger(__name__)

load_dotenv()

PG_CONNECTION_STRING = os.getenv("PG_CONNECTION_STRING", "")
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")


async def main() -> None:
    """Boot: setup DB, compile graph, run Telegram bot."""
    if not TELEGRAM_BOT_TOKEN:
        logger.warning("TELEGRAM_BOT_TOKEN not set; bot will not receive updates.")
    if not PG_CONNECTION_STRING:
        raise ValueError("PG_CONNECTION_STRING is required (e.g. in .env)")

    pool = await setup_database(PG_CONNECTION_STRING)
    checkpointer = get_checkpointer(pool)
    graph = build_workflow(checkpointer)

    await run_bot(token=TELEGRAM_BOT_TOKEN, graph=graph, pool=pool)


if __name__ == "__main__":
    asyncio.run(main())
