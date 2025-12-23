# Custom Checkpointer for LangGraph

A flexible, database-agnostic checkpointing solution for LangChain's LangGraph
framework, enabling persistent state management across multiple [database dialects]
e.g. PostgreSQL, SQLite, and MySQL databases using [`sqlmodel`] and [`sqlalchemy`].

## Overview

This project provides a custom checkpointer implementation for LangGraph's [memory
persistence] feature, allowing you to save and restore workflow state at various
points during execution. It uses [`sqlmodel`] and [`sqlalchemy`] to work seamlessly
with multiple database backends.

### Key Features

- ✅ **Synchronous & Asynchronous Support**: Both `CheckpointSaver` and `AsyncCheckpointSaver`
implementations
- ✅ **Multi-Database Support**: Works with PostgreSQL, SQLite, MySQL, and any
[SQLAlchemy-compatible database][database dialects]
- ✅ **LangGraph Compatible**: Implements `BaseCheckpointSaver` interface from LangGraph
- ✅ **Session Memory**: Enables context retention across multiple interactions
- ✅ **Error Recovery**: Resume operations from the last successful checkpoint

## Inspiration

This project was inspired by two Medium blog posts demonstrating Snowflake as a
checkpointer for LangGraph workflows:

- [LangGraph Workflows: How to Use Snowflake as a Checkpointer for Persistent State Management][part-1-blog]
- [LangGraph Workflows Part 2: Asynchronous State Management with Snowflake Checkpointing][part-2-blog]

While the original implementation focused on Snowflake, this project generalizes
the approach to work with any SQL database.

## Quick Start

### Installation

```sh
uv add checkpointer --dev
```

> *If you don't have the [`uv`] package manager, please follow the [installation guide][uv-install]
> to set it up.*

### Basic Usage

#### Synchronous

```python
from sqlalchemy import create_engine
from checkpointer import CheckpointSaver
from langgraph import StateGraph

engine = create_engine('sqlite:///checkpoints.db')
checkpointer = CheckpointSaver(engine)
graph = StateGraph(...).compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}
result = graph.invoke(initial_state, config=config)
```

#### Asynchronous

```python
from sqlalchemy.ext.asyncio import create_async_engine
from checkpointer import AsyncCheckpointSaver

engine = create_async_engine('sqlite+aiosqlite:///checkpoints.db')
checkpointer = AsyncCheckpointSaver(engine)
graph = StateGraph(...).compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "thread-1"}}
result = await graph.ainvoke(initial_state, config=config)
```

## Examples

- **[Synchronous example][sync-example]**: Saving and restoring checkpoints in
a synchronous LangGraph workflow
- **[Asynchronous example][async-example]**: Checkpointing in an asynchronous
LangGraph workflow

## Documentation

- **[Architecture Guide][architecture.md]**: System architecture and components
- **[Database Schema][database-schema.md]**: Database schema documentation
- **[Usage Guide][usage-guide.md]**: Practical examples and patterns

## Database Compatibility

Works with any SQLAlchemy-compatible database:

- **PostgreSQL**: `postgresql://...` or `postgresql+asyncpg://...`
- **SQLite**: `sqlite:///...` or `sqlite+aiosqlite://...`
- **MySQL**: `mysql://...` or `mysql+aiomysql://...`

## License

MIT License - see [LICENSE] for details.

[`uv`]: https://docs.astral.sh/uv/
[uv-install]: https://docs.astral.sh/uv/getting-started/installation/
[LICENSE]: ./LICENSE
[architecture.md]: ./docs/architecture.md
[database-schema.md]: ./docs/database-schema.md
[usage-guide.md]: ./docs/usage-guide.md
[sync-example]: ./src/checkpointer/examples/sync_checkpointer.py
[async-example]: ./src/checkpointer/examples/async_checkpointer.py
[part-1-blog]: https://medium.com/@siva_yetukuri/how-to-leverage-snowflake-as-a-checkpointer-for-persistence-in-langgraph-workflows-2824ab3efe60
[part-2-blog]: https://medium.com/@siva_yetukuri/langgraph-workflows-part-2-asynchronous-state-management-with-snowflake-checkpointing-76648a1e35af
[`sqlmodel`]: https://sqlmodel.tiangolo.com
[`sqlalchemy`]: https://www.sqlalchemy.org
[database dialects]: https://docs.sqlalchemy.org/en/20/dialects/
[memory persistence]: https://docs.langchain.com/oss/python/langgraph/persistence
