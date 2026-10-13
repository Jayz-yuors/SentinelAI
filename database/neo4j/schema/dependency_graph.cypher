CREATE CONSTRAINT dependency_file_unique
IF NOT EXISTS
FOR (f:File)
REQUIRE f.path IS UNIQUE;