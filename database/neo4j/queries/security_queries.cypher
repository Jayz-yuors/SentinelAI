// ============================================================
// CREATE SECURITY FINDING
// ============================================================

CREATE (
    f:SecurityFinding {
        id: $id,
        repository: $repository,
        type: $type,
        category: $category,
        severity: $severity,
        file: $file,
        line: $line,
        message: $message,
        exploitable: $exploitable,
        riskScore: $riskScore
    }
)


// ============================================================
// FIND HIGH-RISK SECURITY FINDINGS
// ============================================================

MATCH (f:SecurityFinding)
WHERE f.severity IN ["CRITICAL", "HIGH"]
RETURN f
ORDER BY f.riskScore DESC;


// ============================================================
// FIND CVE FINDINGS
// ============================================================

MATCH (f:SecurityFinding)
WHERE f.category = "VULNERABLE_DEPENDENCY"
RETURN f;


// ============================================================
// FIND EXPLOITABLE FINDINGS
// ============================================================

MATCH (f:SecurityFinding)
WHERE f.exploitable = true
RETURN f
ORDER BY f.riskScore DESC;