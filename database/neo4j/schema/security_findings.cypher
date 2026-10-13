CREATE CONSTRAINT security_finding_id_unique
IF NOT EXISTS
FOR (f:SecurityFinding)
REQUIRE f.id IS UNIQUE;