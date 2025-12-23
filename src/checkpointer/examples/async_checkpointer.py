"""Asynchronous checkpointer example.

Demonstrates usage of the asynchronous `AsyncCheckpointSaver` class.
"""


async def amain() -> None:
    """Entry point for async-checkpointer package."""
    print('Hello from async-checkpointer!')


# pylint: disable=import-outside-toplevel
def main() -> None:
    """Synchronous entry point for async-checkpointer package."""
    import asyncio  # noqa: PLC0415

    asyncio.run(amain())


if __name__ == '__main__':
    main()
