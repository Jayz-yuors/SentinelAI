CREATE TABLE IF NOT EXISTS security_analysis (
    id BIGSERIAL PRIMARY KEY,
    repository_url TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    branch TEXT NOT NULL,
    threat_level VARCHAR(20),
    threat_score INTEGER DEFAULT 0,
    total_findings INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS security_findings (
    id SERIAL PRIMARY KEY,

    repository_name VARCHAR(255),

    repository_url TEXT,

    branch VARCHAR(255),

    finding_type VARCHAR(100),

    category VARCHAR(150),

    severity VARCHAR(50),

    file_path TEXT,

    line_number INTEGER,

    message TEXT,

    evidence TEXT,

    cve_id VARCHAR(100),

    package_name VARCHAR(255),

    package_version VARCHAR(100),

    fix_versions JSONB,

    threat_type VARCHAR(150),

    exploitable BOOLEAN DEFAULT FALSE,

    risk_score INTEGER DEFAULT 0,

    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE INDEX IF NOT EXISTS
idx_security_findings_severity
ON security_findings(severity);


CREATE INDEX IF NOT EXISTS
idx_security_findings_repository
ON security_findings(repository_name);


CREATE INDEX IF NOT EXISTS
idx_security_findings_cve
ON security_findings(cve_id);