-- Select checkpoint data.
SELECT
  thread_id,
  checkpoint,
  checkpoint_ns,
  checkpoint_id,
  parent_checkpoint_id,
  metadata,

  -- Subquery to get channel values
  (
    SELECT ARRAY_AGG(ARRAY_CONSTRUCT(bl.channel, bl.type, COALESCE(bl.blob, x'')))
    FROM {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS c,
      LATERAL FLATTEN(input => c.checkpoint:channel_versions) AS json_data,
      {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_BLOBS bl
    WHERE bl.thread_id = c.thread_id
    AND bl.checkpoint_ns = c.checkpoint_ns
    AND bl.channel = json_data.KEY
    AND bl.version = json_data.VALUE
  ) AS channel_values,

  -- Subquery to get pending writes
  (
    SELECT ARRAY_AGG(ARRAY_CONSTRUCT(cw.task_id, cw.channel, cw.type, COALESCE(cw.blob, x''))) WITHIN GROUP (ORDER BY cw.task_id, cw.idx)
    FROM {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_WRITES cw,
         {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS c
    WHERE cw.thread_id = c.thread_id
    AND cw.checkpoint_ns = c.checkpoint_ns
    AND cw.checkpoint_id = c.checkpoint_id
  ) AS pending_writes

  -- Subquery to get pending sends
  (
    SELECT ARRAY_AGG(ARRAY_CONSTRUCT(cw.type, COALESCE(cw.blob, x''))) WITHIN GROUP (ORDER BY cw.idx)
    FROM {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_WRITES cw,
         {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS c
    WHERE cw.thread_id = c.thread_id
    AND cw.checkpoint_ns = c.checkpoint_ns
    AND cw.checkpoint_id = c.checkpoint_id
    AND cw.channel = '{TASKS}'
  ) AS pending_sends

FROM {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS
