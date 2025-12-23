<!--
 Copyright (c) 2025 Victor I. Afolabi

 This software is released under the MIT License.
 https://opensource.org/licenses/MIT
-->

# Architecture Guide

> [!WARNING]
> *The architecture is under active development. This document may change as new
> features are added.*

This document provides a comprehensive overview of the Custom Checkpointer architecture,
design patterns, and component interactions.

## Table of Contents

1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Checkpoint Lifecycle](#checkpoint-lifecycle)
5. [Serialization Strategy](#serialization-strategy)
6. [Database Abstraction](#database-abstraction)

## System Overview

The Custom Checkpointer is designed as a flexible persistence layer for LangGraph
workflows. It implements the `BaseCheckpointSaver` interface from LangGraph, providing
both synchronous and asynchronous operations for saving and retrieving workflow state.

```mermaid
graph TB
    subgraph "LangGraph Application"
        LG[LangGraph Workflow]
        BS[BaseCheckpointSaver Interface]
    end

    subgraph "Custom Checkpointer"
        Base[BaseSaver]
        Sync[CheckpointSaver<br/>Synchronous]
        Async[AsyncCheckpointSaver<br/>Asynchronous]
    end

    subgraph "Database Layer"
        SA[SQLAlchemy Engine]
        SM[SQLModel Models]
    end

    subgraph "Database"
        PG[(PostgreSQL)]
        SQLite[(SQLite)]
        MySQL[(MySQL)]
    end

    LG -->|uses| BS
    BS -->|implemented by| Base
    Base -->|extended by| Sync
    Base -->|extended by| Async
    Sync -->|uses| SA
    Async -->|uses| SA
    SA -->|connects to| SM
    SM -->|queries| PG
    SM -->|queries| SQLite
    SM -->|queries| MySQL
```

## Component Architecture

The checkpointer consists of several key components working together:

### Base Classes

```mermaid
classDiagram
    class BaseCheckpointSaver {
        <<abstract>>
        +put(thread_id, checkpoint_ns, checkpoint_id, ...)
        +get_tuple(thread_id, checkpoint_ns, checkpoint_id)
        +list(config, filter, before)
        +put_writes(thread_id, checkpoint_ns, checkpoint_id, ...)
    }

    class BaseSaver {
        -SELECT_SQL: str
        -MIGRATIONS: list[str]
        -UPSERT_CHECKPOINTS_SQL: str
        -UPSERT_CHECKPOINT_BLOBS_SQL: str
        -UPSERT_CHECKPOINT_WRITES_SQL: str
        +get_next_version(current, channel)
        +_load_checkpoint(...)
        +_load_blobs(...)
        +_dump_blobs(...)
        +_load_writes(...)
        +_dump_writes(...)
        +_load_metadata(...)
        +_dump_metadata(...)
        +_search_where(...)
    }

    class CheckpointSaver {
        -engine: Engine
        -lock: threading.Lock
        +put(...)
        +get_tuple(...)
        +list(...)
        +put_writes(...)
    }

    class AsyncCheckpointSaver {
        -engine: AsyncEngine
        +aput(...)
        +aget_tuple(...)
        +alist(...)
        +aput_writes(...)
    }

    BaseCheckpointSaver <|-- BaseSaver
    BaseSaver <|-- CheckpointSaver
    BaseSaver <|-- AsyncCheckpointSaver
```

### Core Components

1. **BaseSaver**: Abstract base class providing common functionality
   - SQL query management
   - Serialization/deserialization helpers
   - Version management
   - Metadata handling

2. **CheckpointSaver**: Synchronous implementation
   - Uses SQLAlchemy synchronous engine
   - Thread-safe operations with locks
   - Blocking database operations

3. **AsyncCheckpointSaver**: Asynchronous implementation
   - Uses SQLAlchemy async engine
   - Non-blocking database operations
   - Coroutine-based API

## Data Flow

### Saving a Checkpoint

```mermaid
sequenceDiagram
    participant LG as LangGraph Workflow
    participant CS as CheckpointSaver
    participant Base as BaseSaver
    participant Serializer as JsonPlusSerializer
    participant DB as Database

    LG->>CS: put(thread_id, checkpoint_ns, checkpoint_id, ...)
    CS->>Base: _dump_blobs(values, versions)
    Base->>Serializer: dumps_typed(value)
    Serializer-->>Base: (type, bytes)
    Base-->>CS: blob_data
    CS->>Base: _dump_metadata(metadata)
    Base->>Serializer: dumps_typed(metadata)
    Serializer-->>Base: serialized_metadata
    Base-->>CS: metadata_str
    CS->>DB: UPSERT_CHECKPOINTS_SQL
    CS->>DB: UPSERT_CHECKPOINT_BLOBS_SQL
    DB-->>CS: Success
    CS-->>LG: Checkpoint saved
```

### Retrieving a Checkpoint

```mermaid
sequenceDiagram
    participant LG as LangGraph Workflow
    participant CS as CheckpointSaver
    participant Base as BaseSaver
    participant Serializer as JsonPlusSerializer
    participant DB as Database

    LG->>CS: get_tuple(thread_id, checkpoint_ns, checkpoint_id)
    CS->>DB: SELECT_SQL with parameters
    DB-->>CS: checkpoint_data, channel_values, pending_writes
    CS->>Base: _load_blobs(channel_values)
    Base->>Serializer: loads_typed((type, bytes))
    Serializer-->>Base: deserialized_value
    Base-->>CS: channel_values dict
    CS->>Base: _load_checkpoint(...)
    Base->>Base: _load_writes(pending_writes)
    Base-->>CS: Checkpoint object
    CS-->>LG: CheckpointTuple
```

## Checkpoint Lifecycle

A checkpoint goes through several stages during its lifecycle:

```mermaid
stateDiagram-v2
    [*] --> Created: Workflow Step Executes
    Created --> Serialized: Serialize State
    Serialized --> BlobsExtracted: Extract Channel Values
    BlobsExtracted --> MetadataPrepared: Prepare Metadata
    MetadataPrepared --> Saved: Database Write
    Saved --> Retrieved: get_tuple() Called
    Retrieved --> Deserialized: Deserialize State
    Deserialized --> Restored: Workflow Continues
    Restored --> Created: Next Step
    Restored --> [*]: Workflow Complete
```

### Checkpoint States

1. **Created**: Initial checkpoint object created by LangGraph
2. **Serialized**: State data converted to binary format
3. **BlobsExtracted**: Large channel values extracted as separate blobs
4. **MetadataPrepared**: Metadata serialized and prepared
5. **Saved**: Checkpoint persisted to database
6. **Retrieved**: Checkpoint fetched from database
7. **Deserialized**: Binary data converted back to Python objects
8. **Restored**: State restored in LangGraph workflow

## Serialization Strategy

The checkpointer uses a sophisticated serialization strategy to handle complex
state data:

```mermaid
graph LR
    subgraph "Checkpoint Data"
        CP[Checkpoint Object]
        CV[Channel Values]
        PS[Pending Sends]
        MD[Metadata]
    end

    subgraph "Serialization"
        JPS[JsonPlusSerializer]
        TV[Type + Value]
    end

    subgraph "Storage"
        CB[Checkpoint Table<br/>JSON/Binary]
        BT[Blobs Table<br/>Binary]
        WT[Writes Table<br/>Binary]
    end

    CP -->|serialize| JPS
    CV -->|extract & serialize| JPS
    PS -->|serialize| JPS
    MD -->|serialize| JPS

    JPS -->|produces| TV
    TV -->|store| CB
    TV -->|store| BT
    TV -->|store| WT
```

### Serialization Components

1. **JsonPlusSerializer**: LangGraph's serializer that handles:
   - Python primitives (int, str, float, bool)
   - Complex objects (dicts, lists, tuples)
   - Custom types with type annotations
   - Circular references

2. **Type + Value Pairing**: Each serialized value is paired with its type identifier
to enable proper deserialization

3. **Blob Separation**: Large channel values are stored separately in the `checkpoint_blobs`
table for efficiency

## Database Abstraction

The checkpointer uses SQLAlchemy and SQLModel for database abstraction:

```mermaid
graph TB
    subgraph "Application Layer"
        CS[CheckpointSaver]
    end

    subgraph "Abstraction Layer"
        SA[SQLAlchemy Engine]
        SM[SQLModel]
    end

    subgraph "Database Drivers"
        PG_D[PostgreSQL Driver<br/>psycopg2/asyncpg]
        SQLite_D[SQLite Driver<br/>pysqlite/aiosqlite]
        MySQL_D[MySQL Driver<br/>pymysql/aiomysql]
    end

    subgraph "Databases"
        PG[(PostgreSQL)]
        SQL[(SQLite)]
        MY[(MySQL)]
    end

    CS -->|uses| SA
    SA -->|uses| SM
    SM -->|connects via| PG_D
    SM -->|connects via| SQLite_D
    SM -->|connects via| MySQL_D
    PG_D -->|queries| PG
    SQLite_D -->|queries| SQL
    MySQL_D -->|queries| MY
```

### Database Schema Abstraction

The SQL queries use parameterized placeholders that are compatible across different
databases:

- **PostgreSQL**: Uses `%s` placeholders
- **SQLite**: Uses `?` or `%s` placeholders
- **MySQL**: Uses `%s` placeholders

SQLModel/SQLAlchemy handles the translation of these placeholders based on the
database dialect.

## Error Handling

The checkpointer handles various error scenarios:

- **Connection Errors**: Retry logic for transient failures
- **Constraint Violations**: Handle duplicate checkpoint IDs
- **Serialization Errors**: Graceful handling of unserializable data
- **Database-Specific Errors**: Dialect-aware error handling

## Performance Considerations

1. **Blob Storage**: Large channel values are stored separately to avoid bloating
the main checkpoint table
2. **Indexing**: Primary keys and indexes on frequently queried columns
3. **Connection Pooling**: Reuse database connections for better performance
4. **Batch Operations**: Efficient batch inserts/updates for writes
5. **Lazy Loading**: Channel values loaded only when needed
