package com.sentinelai.backend.modules.analysis;

import org.springframework.jdbc.core.JdbcTemplate;
import org.springframework.stereotype.Service;

import java.util.LinkedHashMap;
import java.util.Map;

@Service
public class BackendAnalysisPersistenceService {

    private final JdbcTemplate jdbcTemplate;

    public BackendAnalysisPersistenceService(
            JdbcTemplate jdbcTemplate
    ) {
        this.jdbcTemplate = jdbcTemplate;
    }

    public boolean analysisExists(
            String analysisId
    ) {

        Integer count =
                jdbcTemplate.queryForObject(
                        """
                        SELECT COUNT(*)
                        FROM sentinelai_analysis
                        WHERE analysis_id = ?
                        """,
                        Integer.class,
                        analysisId
                );

        return count != null && count > 0;
    }

    public Map<String, Object> getAnalysisStatus(
            String analysisId
    ) {

        Map<String, Object> result =
                new LinkedHashMap<>();

        jdbcTemplate.query(
                """
                SELECT
                    analysis_id,
                    repository_url,
                    repository_name,
                    branch,
                    status,
                    created_at,
                    completed_at,
                    error_message
                FROM sentinelai_analysis
                WHERE analysis_id = ?
                """,
                statement -> statement.setString(
                        1,
                        analysisId
                ),
                rs -> {

                    result.put(
                            "analysisId",
                            rs.getString("analysis_id")
                    );

                    result.put(
                            "repositoryUrl",
                            rs.getString("repository_url")
                    );

                    result.put(
                            "repositoryName",
                            rs.getString("repository_name")
                    );

                    result.put(
                            "branch",
                            rs.getString("branch")
                    );

                    result.put(
                            "status",
                            rs.getString("status")
                    );

                    result.put(
                            "createdAt",
                            rs.getTimestamp("created_at")
                    );

                    result.put(
                            "completedAt",
                            rs.getTimestamp("completed_at")
                    );

                    result.put(
                            "errorMessage",
                            rs.getString("error_message")
                    );
                }
        );

        return result;
    }

    public boolean databaseAvailable() {

        try {

            Integer result =
                    jdbcTemplate.queryForObject(
                            "SELECT 1",
                            Integer.class
                    );

            return result != null
                    && result == 1;

        } catch (Exception exception) {

            return false;
        }
    }
}