-- Checkpoint blobs table.
CREATE OR REPLACE TABLE {{DB_NAME}}.{{SCHEMA_NAME}}.LANGGRAPH_CHECKPOINT_BLOBS (
  thread_id STRING NOT NULL,
  checkpoint_ns STRING NOT NULL DEFAULT '',
  channel STRING NOT NULL,
  version STRING NOT NULL,
  type STRING NOT NULL,
  blob BINARY,
  PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);
