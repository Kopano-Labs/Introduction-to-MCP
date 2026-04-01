-- `orch` Data Lake Audit Logging Schema
-- Architect: www.linkedin.com/in/kholofelo-robyn-rababalela-7a26273b7
-- GitHub: https://github.com/RobynAwesome/

CREATE TABLE IF NOT EXISTS discussions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    start_time DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    discussion_id INTEGER,
    model TEXT NOT NULL,
    agent_id TEXT NOT NULL,
    message TEXT,
    prompt TEXT,
    log_type TEXT CHECK(log_type IN ('reasoning', 'execution', 'message')) NOT NULL,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(discussion_id) REFERENCES discussions(id)
);