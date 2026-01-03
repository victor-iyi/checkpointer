"""Synchronous checkpoint saver implementation.

Provides the `CheckpointSaver` class for synchronous checkpoint persistence operations.
"""

import sys
import threading
from collections.abc import Iterator
from contextlib import contextmanager
from typing import cast

from langgraph.checkpoint.serde.base import SerializerProtocol
from psycopg.cursor import Cursor
from psycopg.rows import DictRow, dict_row
from sqlalchemy.engine import Engine

from checkpointer._internal import Conn, logger
from checkpointer.base.base import BaseSaver
from checkpointer.base.utils import get_connection


class CheckpointSaver(BaseSaver):  # pylint: disable=abstract-method
    """Synchronous checkpoint saver for LangGraph state persistence.

    This class provides synchronous methods for saving and retrieving
    checkpoints from a database backend.
    """

    lock: threading.Lock

    def __init__(self, conn: Conn, serde: SerializerProtocol | None = None) -> None:
        """Initialize the CheckpointSaver with a threading lock."""
        super().__init__(serde=serde)

        self.conn = conn
        self.lock = threading.Lock()

    @contextmanager
    def _cursor(self) -> Iterator[Cursor[DictRow]]:
        """Context manager to yield a database cursor with thread safety."""
        conn_context = get_connection(self.conn)
        conn = conn_context.__enter__()
        try:
            dbapi_conn = conn.connection
            with self.lock:
                cursor = cast(Cursor[DictRow], dbapi_conn.cursor(row_factory=dict_row))
                try:
                    yield cursor
                finally:
                    cursor.close()
        finally:
            exc_type, exc_val, exc_tb = sys.exc_info()
            conn_context.__exit__(exc_type, exc_val, exc_tb)

    @classmethod
    @contextmanager
    def from_engine(cls, engine: Engine) -> Iterator['CheckpointSaver']:
        """Context manager to create a CheckpointSaver from a SQLAlchemy Engine.

        Args:
            engine (Engine): A SQLAlchemy Engine instance.

        Yields:
            Iterator[CheckpointSaver]: An instance of CheckpointSaver.

        """
        logger.debug('Creating CheckpointSaver from Engine.')
        saver = cls(conn=engine)
        try:
            yield saver  # Yield the saver instance
        finally:
            logger.info('Cleaning up CheckpointSaver resources.')
            if isinstance(saver.conn, Engine):
                saver.conn.dispose()
            else:
                saver.conn.close()
