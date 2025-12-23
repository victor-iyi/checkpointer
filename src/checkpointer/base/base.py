"""Base checkpoint saver implementation.

Provides the `BaseSaver` abstract class that implements common checkpoint
serialization, deserialization, and SQL query generation logic.
"""

# mypy: disable-error-code="empty-body"
import json
import random
from collections.abc import Sequence
from functools import cached_property
from typing import Any, ClassVar, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import (
    WRITES_IDX_MAP,
    BaseCheckpointSaver,
    ChannelVersions,
    Checkpoint,
    CheckpointMetadata,
    get_checkpoint_id,
)
from langgraph.checkpoint.serde.jsonplus import JsonPlusSerializer

from checkpointer._internal._sql_helpers import get_sql_file
from checkpointer._internal._types import MetadataInput, _Version


class BaseSaver(BaseCheckpointSaver):  # pylint: disable=abstract-method
    """Base class for checkpoint savers.

    SQL queries are lazily loaded on first access to avoid import-time file I/O errors
    if SQL files are missing. Subclasses can override the SQL properties to provide
    database-specific query implementations.
    """

    jsonplus_serializer: ClassVar[JsonPlusSerializer] = JsonPlusSerializer()

    @cached_property
    def select_sql(self) -> str:
        """SQL query for selecting checkpoints."""
        return get_sql_file('selects/checkpoints.sql')

    @cached_property
    def migrations(self) -> list[str]:
        """List of SQL migration scripts in execution order."""
        return [
            get_sql_file('migrations/migration.sql'),  # Migration 1: Checkpoint Migrations table.
            get_sql_file('migrations/checkpoints.sql'),  # Migration 2: Checkpoints table.
            get_sql_file('migrations/checkpoint_blobs.sql'),  # Migration 3: Checkpoint Blobs table.
            get_sql_file('migrations/checkpoint_writes.sql'),  # Migration 4: Checkpoint Writes table.
        ]

    @cached_property
    def upsert_checkpoints_sql(self) -> str:
        """SQL query for upserting checkpoints."""
        return get_sql_file('upserts/checkpoints.sql')

    @cached_property
    def upsert_checkpoint_blobs_sql(self) -> str:
        """SQL query for upserting checkpoint blobs."""
        return get_sql_file('upserts/checkpoint_blobs.sql')

    @cached_property
    def upsert_checkpoint_writes_sql(self) -> str:
        """SQL query for upserting checkpoint writes."""
        return get_sql_file('upserts/checkpoint_writes.sql')

    @cached_property
    def insert_checkpoint_writes_sql(self) -> str:
        """SQL query for inserting checkpoint writes."""
        return get_sql_file('inserts/checkpoint_writes.sql')

    def get_next_version(self, current: _Version | None, channel: Any = None) -> _Version:  # noqa: PLR6301
        """Generate the next version ID for a channel.

        Default is to use integer versions, incrementing by `1`. If you override, you can use `str`/`int`/`float`
        versions, as long as they are monotonically increasing.

        Args:
            current(_Version | None): The current version identifier (`int`, `float`, or `str`), or `None` if no version exists.
            channel(Any): Unused. Kept for compatibility with the `BaseCheckpointSaver` interface.
                Defaults to `None`.

        Returns:
            _Version: The next version identifier, which must be monotonically increasing.

        """
        del channel  # Unused, required for interface compatibility.
        match current:
            case None:
                current_v = 0
            case int():
                current_v = current
            case str() if '.' in current:
                current_v = int(current.split('.')[0])
            case str() if current.isdigit():
                current_v = int(current)
            case float():
                current_v = int(current)
            case _:
                raise ValueError(f'Unknown version: {current}')

        next_v = current_v + 1
        next_h = random.randint(0, 0xFFFFFFFFFFFFFFFF)  # equivalent to sys.maxsize * 2 + 1
        return f'{next_v:032}.{next_h:016}'

    def _load_checkpoint(
        self,
        checkpoint: dict[str, Any],
        channel_values: list[tuple[str, str, str]],
        pending_sends: list[tuple[str, str]],
    ) -> Checkpoint:  # type: ignore[reportReturnType]
        """Load a checkpoint from a dictionary."""
        return Checkpoint(
            **checkpoint,  # type: ignore[typeddict-item]
            channel_values=self._load_blobs(channel_values),
            pending_sends=[self.serde.loads_typed((c, bytes.fromhex(b))) for c, b in pending_sends or []],  # type: ignore[reportCallIssue]
        )

    def _load_blobs(self, blob_values: list[tuple[str, str, str]]) -> dict[str, Any]:
        """Load blob values from a list of tuples."""
        if not blob_values:
            return {}
        return {k: self.serde.loads_typed((t, bytes.fromhex(v))) for k, t, v in blob_values if t != 'empty'}

    def _dump_blobs(
        self, thread_id: str, checkpoint_ns: str, values: dict[str, Any], versions: ChannelVersions
    ) -> list[tuple[str, str, str, str, str, bytes | None]]:
        """Dump blob values to a list of tuples."""
        if not versions:
            return []

        data = [
            (
                thread_id,
                checkpoint_ns,
                k,
                str(ver),
                *(self.serde.dumps_typed(values[k]) if k in values else ('empty', None)),
            )
            for k, ver in versions.items()
        ]
        return cast(list[tuple[str, str, str, str, str, bytes | None]], data)

    def _load_writes(self, writes: list[tuple[str, str, str, str]]) -> list[tuple[str, str, Any]]:
        """Load write values from a list of tuples."""
        return (
            [
                (
                    tid,
                    channel,
                    self.serde.loads_typed((t, bytes.fromhex(v))),
                )
                for tid, channel, t, v in writes
            ]
            if writes
            else []
        )

    def _dump_writes(  # pylint: disable=too-many-arguments, too-many-positional-arguments
        self, thread_id: str, checkpoint_ns: str, checkpoint_id: str, task_id: str, writes: Sequence[tuple[str, Any]]
    ) -> list[tuple[str, str, str, str, int, str, str, bytes]]:
        """Dump write values to a list of tuples."""
        return [
            (
                thread_id,
                checkpoint_ns,
                checkpoint_id,
                task_id,
                WRITES_IDX_MAP.get(channel, idx),
                channel,
                *self.serde.dumps_typed(value),
            )
            for idx, (channel, value) in enumerate(writes)
        ]

    def _load_metadata(self, metadata: dict[str, Any]) -> CheckpointMetadata:
        """Load metadata from a dictionary.

        Performs a round-trip serialization to ensure proper type coercion
        of metadata values (e.g., converting ISO date strings to datetime objects).
        """
        _data = self.jsonplus_serializer.dumps_typed(metadata)
        return self.jsonplus_serializer.loads_typed(_data)

    def _dump_metadata(self, metadata: CheckpointMetadata) -> str:
        """Dump metadata to a string."""
        serialized_metadata = self.jsonplus_serializer.dumps_typed(metadata)[1]
        # Remove null bytes from the serialized metadata
        return serialized_metadata.decode().replace('\\u0000', '')

    def _metadata_predicate(self, filter: MetadataInput) -> tuple[str, list[Any]]:  # pylint: disable=redefined-builtin
        """Return the SQL predicate for metadata filtering.

        Override this method in subclasses to provide database-specific JSON containment checks.

        The default implementation uses Snowflake's `OBJECT_CONTAINS` and `PARSE_JSON` functions.
        For other databases, override with the appropriate syntax:
            - PostgreSQL: `metadata @> %s::jsonb`
            - MySQL: `JSON_CONTAINS(metadata, %s)`
            - SQLite: Custom JSON extraction logic
            - Snowflake: `OBJECT_CONTAINS(metadata, PARSE_JSON(%s))`

        Args:
            filter(MetadataInput): The metadata filter dictionary to match against.

        Returns:
            tuple[str, list[Any]]: A tuple of (predicate_string, parameter_values).

        """
        if not filter:
            return '', []
        return 'OBJECT_CONTAINS(metadata, PARSE_JSON(%s))', [json.dumps(filter)]

    def _search_where(
        self,
        config: RunnableConfig | None,
        *,
        filter: MetadataInput,  # pylint: disable=redefined-builtin
        before: RunnableConfig | None = None,
    ) -> tuple[str, list[Any]]:
        """Return `WHERE` clause predicates for `alist()` given config, filter, cursor.

        This method returns a tuple of a SQL string and parameter values. The string is the
        parameterized `WHERE` clause predicate (including the `WHERE` keyword):
        `"WHERE column1 = %s AND column2 = %s"`.

        The list of values contains the values for each corresponding parameter placeholder.
        """
        wheres: list[str] = []
        param_values: list[Any] = []

        # Construct predicate for config filter.
        if config and 'configurable' in config:
            wheres.append('thread_id = %s ')
            param_values.append(config['configurable']['thread_id'])
            if checkpoint_ns := config['configurable'].get('checkpoint_ns'):
                wheres.append('checkpoint_ns = %s')
                param_values.append(checkpoint_ns)

            if checkpoint_id := get_checkpoint_id(config):
                wheres.append('checkpoint_id = %s')
                param_values.append(checkpoint_id)

        # Construct predicate for metadata filter.
        predicate_sql, predicate_values = self._metadata_predicate(filter)
        if predicate_sql:
            wheres.append(predicate_sql)
            param_values.extend(predicate_values)

        # Construct predicate for before filter.
        if before is not None:
            wheres.append('checkpoint_id < %s')
            param_values.append(get_checkpoint_id(before))

        return ' WHERE ' + ' AND '.join(wheres) if wheres else '', param_values
