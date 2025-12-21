-- Upsert checkpoints.
MERGE INTO {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS AS target
USING (
  SELECT %(thread_id)s AS thread_id, %(checkpoint_ns)s AS checkpoint_ns, %(checkpoint_id)s AS checkpoint_id, %(parent_checkpoint_id)s AS parent_checkpoint_id,
         PARSE_JSON(%(checkpoint)s) AS checkpoint, PARSE_JSON(%(metadata)s) AS metadata,
) AS source
ON target.thread_id = source.thread_id
   AND target.checkpoint_ns = source.checkpoint_ns
   AND target.checkpoint_id = source.checkpoint_id
WHEN MATCHED THEN
  UPDATE SET
    checkpoint = source.checkpoint,
    metadata = source.metadata
WHEN NOT MATCHED THEN
  INSERT (thread_id, checkpoint_ns, checkpoint_id, parent_checkpoint_id, checkpoint, metadata)
  VALUES (source.thread_id, source.checkpoint_ns, source.checkpoint_id, source.parent_checkpoint_id, source.checkpoint, source.metadata);
