MATCH (source:File)-[r:DEPENDS_ON]->(target:File)
RETURN
    source.path AS source,
    target.path AS target;
MATCH (dependent:File)-[:DEPENDS_ON]->(target:File {
    path: $file_path
})
RETURN dependent.path AS dependent_file;
MATCH (source:File)-[:DEPENDS_ON]->(target:File)
RETURN
    source.path AS file,
    count(target) AS dependency_count
ORDER BY dependency_count DESC;
MATCH path =
    (a:File)-[:DEPENDS_ON*2..]->(a)
RETURN path;