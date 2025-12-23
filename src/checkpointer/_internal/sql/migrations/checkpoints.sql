-- Migration 2: Checkpoints table.
CREATE OR REPLACE TABLE {{DB_NAME}}.{{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINTS (
  thread_id STRING NOT NULL,
  checkpoint_ns STRING NOT NULL DEFAULT '',
  checkpoint_id STRING NOT NULL,
  parent_checkpoint_id STRING,
  type STRIG,
  checkpoint VARIANT NOT NULL,
  metadata VARIANT NOT NULL DEFAULT '{}',
  PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);
