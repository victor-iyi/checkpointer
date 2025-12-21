-- Upsert checkpoint blobs.
MERGE INTO {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_BLOBS AS target
USING (
  SELECT %(thread_id)s AS thread_id, %(checkpoint_ns)s AS checkpoint_ns, %(channel)s AS channel,
         %(version)s AS version, %(type)s AS type, %(blob)s AS blob
) AS source
ON target.thread_id = source.thread_id
  AND target.checkpoint_ns = source.checkpoint_ns
  AND target.channel = source.channel
  AND target.version = source.version
WHEN NOT MATCHED THEN
  INSERT (thread_id, checkpoint_ns, channel, version, type, blob)
  VALUES (source.thread_id, source.checkpoint_ns, source.channel, source.version, source.type, source.blob);
