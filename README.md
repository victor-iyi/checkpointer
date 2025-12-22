# Custom Checkpointer for LangGraph

A flexible, database-agnostic checkpointing solution for LangChain's LangGraph framework, enabling persistent state management across PostgreSQL, SQLite, and MySQL databases using `sqlmodel` and `sqlalchemy`.

## Overview

This project provides a custom checkpointer implementation for LangGraph's memory persistence feature, allowing you to save and restore workflow state at various points during execution. It uses `sqlmodel` and `sqlalchemy` to work seamlessly with multiple database backends.

### Key Features

- ✅ **Synchronous & Asynchronous Support**: Both `CheckpointSaver` and `AsyncCheckpointSaver` implementations
- ✅ **Multi-Database Support**: Works with PostgreSQL, SQLite, MySQL, and any SQLAlchemy-compatible database
- ✅ **LangGraph Compatible**: Implements `BaseCheckpointSaver` interface from LangGraph
- ✅ **Session Memory**: Enables context retention across multiple interactions
- ✅ **Error Recovery**: Resume operations from the last successful checkpoint

## Inspiration

This project was inspired by two Medium blog posts demonstrating Snowflake as a checkpointer for LangGraph workflows:

- [Part 1: How to Leverage Snowflake as a Checkpointer](https://medium.com/@siva_yetukuri/how-to-leverage-snowflake-as-a-checkpointer-for-persistence-in-langgraph-workflows-2824ab3efe60)
- [Part 2: Asynchronous State Management](https://medium.com/@siva_yetukuri/langgraph-workflows-part-2-asynchronous-state-management-with-snowflake-checkpointing-76648a1e35af)

While the original implementation focused on Snowflake, this project generalizes the approach to work with any SQL database.

## Quick Start

### Installation

```sh
uv add checkpointer
```

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

## Documentation

- **[Architecture Guide](./docs/architecture.md)**: System architecture and components
- **[Database Schema](./docs/database-schema.md)**: Database schema documentation
- **[API Reference](./docs/api-reference.md)**: API documentation
- **[Usage Guide](./docs/usage-guide.md)**: Practical examples and patterns

## Requirements

- Python >= 3.14
- langchain >= 1.2.0
- langgraph >= 1.0.5
- sqlmodel >= 0.0.27

## Database Compatibility

Works with any SQLAlchemy-compatible database:
- **PostgreSQL**: `postgresql://...` or `postgresql+asyncpg://...`
- **SQLite**: `sqlite:///...` or `sqlite+aiosqlite://...`
- **MySQL**: `mysql://...` or `mysql+aiomysql://...`

## License

MIT License - see [LICENSE](LICENSE) for details.
