"""Utility functions for the base saver."""

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Connection, Engine
from sqlalchemy.pool import Pool


@contextmanager
def get_connection(conn: Connection | Engine | Pool) -> Iterator[Connection]:
    """Context manager to yield a SQLAlchemy Connection.

    Args:
        conn (Connection | Engine | Pool): A SQLAlchemy Connection, Engine, or Pool.

    Yields:
        Connection: A SQLAlchemy Connection instance.

    Examples:
        >>> # Example usage
        >>> from sqlalchemy import create_engine, text
        >>> engine = create_engine('sqlite:///:memory:')
        >>> with get_connection(engine) as connection:
        ...     result = connection.execute(text('SELECT 1'))
        ...     print(result.scalar())
        1

        >>> # Using a Connection directly
        >>> with engine.connect() as conn:
            ...     with get_connection(conn) as connection:
            ...         result = connection.execute(text('SELECT 1'))
            ...         print(result.scalar())
        1

    Raises:
        TypeError: If the provided conn is not a Connection, Engine, or Pool.

    """
    match conn:
        case Connection():
            # If it's already a Connection, yield it directly
            yield conn
        case Engine():
            # If it's an Engine, connect and yield the Connection
            with conn.connect() as connection:
                yield connection
        case Pool():
            # If it's a Pool, connect and yield the Connection
            # with conn.acquire() as connection:
            #     yield connection
            raise NotImplementedError('Pool connection is not supported. Use Engine instead.')
        case _:
            raise TypeError(f'Invalid connection type: {type(conn)}')
