-- Insert checkpoint writes.
MERGE INTO {{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_WRITES AS target
USING (
  SELECT %(thread_id)s AS thread_id, %(checkpoint_ns)s AS checkpoint_ns, %(checkpoint_id)s AS checkpoint_id,
         %(task_id)s AS task_id, %(idx)s AS idx, %(channel)s AS channel, %(type)s AS type, %(blob)s AS blob
) AS source
ON target.thread_id = source.thread_id
  AND target.checkpoint_ns = source.checkpoint_ns
  AND target.checkpoint_id = source.checkpoint_id
  AND target.task_id = source.task_id
  AND target.idx = source.idx
WHEN NOT MATCHED THEN
  INSERT (thread_id, checkpoint_ns, checkpoint_id, task_id, idx, channel, type, blob)
  VALUES (source.thread_id, source.checkpoint_ns, source.checkpoint_id, source.task_id, source.idx, source.channel, source.type, source.blob);
