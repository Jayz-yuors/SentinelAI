import ast
from pathlib import Path


def extract_python_dependencies(
    file_path: Path
):
    """
    Extract Python imports using the AST module.

    Detects:
        import package
        from package import something
    """

    try:

        source = file_path.read_text(
            encoding="utf-8"
        )

    except (OSError, UnicodeDecodeError):

        return []

    try:

        tree = ast.parse(source)

    except SyntaxError:

        return []

    dependencies = set()

    for node in ast.walk(tree):

        if isinstance(node, ast.Import):

            for alias in node.names:

                dependencies.add(
                    alias.name
                )

        elif isinstance(node, ast.ImportFrom):

            if node.level > 0:

                prefix = "." * node.level

                if node.module:

                    dependencies.add(
                        prefix + node.module
                    )

                else:

                    dependencies.add(
                        prefix
                    )

            elif node.module:

                dependencies.add(
                    node.module
                )

    return sorted(
        dependencies
    )