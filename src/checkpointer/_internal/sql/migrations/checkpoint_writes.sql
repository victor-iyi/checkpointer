-- Migration 4: Checkpoint Writes table.
CREATE OR REPLACE TABLE {{DB_NAME}}.{{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_WRITES (
  thread_id STRING NOT NULL,
  checkpoint_ns STRING NOT NULL DEFAULT '',
  checkpoint_id STRING NOT NULL,
  task_id STRING NOT NULL,
  idx INTEGER NOT NULL,
  channel STRING NOT NULL,
  type STRING,
  blob BINARY NOT NULL,
  PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);
