CREATE TABLE IF NOT EXISTS dependency_analysis (
    id BIGSERIAL PRIMARY KEY,
    repository_url TEXT NOT NULL,
    repository_name TEXT NOT NULL,
    branch TEXT NOT NULL,
    total_nodes INTEGER DEFAULT 0,
    total_edges INTEGER DEFAULT 0,
    overall_risk VARCHAR(20),
    risk_score INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);


CREATE TABLE IF NOT EXISTS dependency_nodes (
    id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL,
    node_name TEXT NOT NULL,
    node_type VARCHAR(50),
    dependency_count INTEGER DEFAULT 0,
    reverse_dependency_count INTEGER DEFAULT 0,

    CONSTRAINT fk_dependency_analysis
        FOREIGN KEY (analysis_id)
        REFERENCES dependency_analysis(id)
        ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS dependency_edges (
    id BIGSERIAL PRIMARY KEY,
    analysis_id BIGINT NOT NULL,
    source_node TEXT NOT NULL,
    target_node TEXT NOT NULL,

    CONSTRAINT fk_dependency_edge_analysis
        FOREIGN KEY (analysis_id)
        REFERENCES dependency_analysis(id)
        ON DELETE CASCADE
);