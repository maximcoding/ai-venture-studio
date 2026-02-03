"""PostgreSQL pool and LangGraph AsyncPostgresSaver for checkpoints."""

import logging
from typing import Any

from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg import AsyncConnection
from psycopg.rows import dict_row
from psycopg_pool import AsyncConnectionPool

logger = logging.getLogger(__name__)


async def setup_database(conninfo: str) -> AsyncConnectionPool:
    """Create pool and run checkpointer schema setup. Call once at boot."""
    setup_conn = await AsyncConnection.connect(
        conninfo,
        autocommit=True,
        row_factory=dict_row,
    )
    saver = AsyncPostgresSaver(setup_conn)
    await saver.setup()
    await setup_conn.close()

    pool = AsyncConnectionPool(
        conninfo=conninfo,
        max_size=10,
        timeout=30,
        kwargs={"row_factory": dict_row},
    )
    await pool.open()
    logger.info("postgres_pool_ready")
    return pool


def get_checkpointer(pool: AsyncConnectionPool) -> Any:
    """Return AsyncPostgresSaver for the given pool (for graph.compile(checkpointer=...))."""
    return AsyncPostgresSaver(pool)
