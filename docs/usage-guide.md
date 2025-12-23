# Usage Guide

> [!WARNING]
> *This repository is under active development. This document may change as new
> features are added.*

Practical examples for using the Custom Checkpointer.

## Installation

```sh
uv add checkpointer --dev
```

## Database Setup

### SQLite (Development)

```python
from sqlalchemy import create_engine
from checkpointer import CheckpointSaver

engine = create_engine('sqlite:///checkpoints.db')
checkpointer = CheckpointSaver(engine)
```

### PostgreSQL (Production)

```python
from sqlalchemy import create_engine
from checkpointer import CheckpointSaver

engine = create_engine('postgresql://user:password@localhost:5432/mydb')
checkpointer = CheckpointSaver(engine)
```

### MySQL

```python
from sqlalchemy import create_engine
from checkpointer import CheckpointSaver

engine = create_engine('mysql://user:password@localhost:3306/mydb')
checkpointer = CheckpointSaver(engine)
```

## Synchronous Usage

```python
from sqlalchemy import create_engine
from checkpointer import CheckpointSaver
from langgraph import StateGraph

# Setup
engine = create_engine('sqlite:///checkpoints.db')
checkpointer = CheckpointSaver(engine)

# Compile graph with checkpointer
graph = StateGraph(state_schema).compile(checkpointer=checkpointer)

# Run workflow
config = {"configurable": {"thread_id": "thread-1"}}
result = graph.invoke(initial_state, config=config)

# Resume from checkpoint (uses last checkpoint automatically)
result = graph.invoke({}, config=config)
```

## Asynchronous Usage

```python
from sqlalchemy.ext.asyncio import create_async_engine
from checkpointer import AsyncCheckpointSaver
from langgraph import StateGraph
import asyncio

# Setup
engine = create_async_engine('sqlite+aiosqlite:///checkpoints.db')
checkpointer = AsyncCheckpointSaver(engine)

# Compile graph
graph = StateGraph(state_schema).compile(checkpointer=checkpointer)

# Run workflow
async def main():
    config = {"configurable": {"thread_id": "thread-1"}}
    result = await graph.ainvoke(initial_state, config=config)
    return result

asyncio.run(main())
```

## Common Patterns

### Session Management

```python
class WorkflowManager:
    def __init__(self, database_url: str):
        engine = create_engine(database_url)
        self.checkpointer = CheckpointSaver(engine)
        self.graph = None

    def compile_graph(self, workflow: StateGraph):
        self.graph = workflow.compile(checkpointer=self.checkpointer)

    def run(self, thread_id: str, initial_state: dict):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(initial_state, config=config)

    def resume(self, thread_id: str, additional_input: dict = None):
        config = {"configurable": {"thread_id": thread_id}}
        return self.graph.invoke(additional_input or {}, config=config)
```

### Namespace Isolation

```python
# Development namespace
dev_config = {
    "configurable": {
        "thread_id": "user-123",
        "checkpoint_ns": "dev"
    }
}

# Production namespace
prod_config = {
    "configurable": {
        "thread_id": "user-123",
        "checkpoint_ns": "prod"
    }
}

# Same thread_id, different namespaces = isolated checkpoints
dev_result = graph.invoke(state, config=dev_config)
prod_result = graph.invoke(state, config=prod_config)
```

### Listing Checkpoints

```python
# List all checkpoints for a thread
config = {"configurable": {"thread_id": "thread-1"}}
checkpoints = list(checkpointer.list(config))

for checkpoint_tuple in checkpoints:
    print(f"Checkpoint ID: {checkpoint_tuple.metadata.get('checkpoint_id')}")
```

## Troubleshooting

### Database Connection Errors

- Verify database URL is correct
- Check database credentials
- Ensure database server is running

### Table Creation Issues

- Tables are created automatically on first use
- Check database permissions
- Verify database exists

### Checkpoint Not Found

- Verify `thread_id` and `checkpoint_ns` match
- Check `checkpoint_id` is correct
- Ensure checkpoint was saved successfully

## Connection Pooling (Production)

```python
engine = create_engine(
    'postgresql://user:pass@localhost/dbname',
    pool_size=20,
    max_overflow=10,
    pool_pre_ping=True,
    pool_recycle=3600,
)
checkpointer = CheckpointSaver(engine)
```
