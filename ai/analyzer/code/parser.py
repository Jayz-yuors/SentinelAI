import ast
from pathlib import Path


def analyze_python_file(file_path: Path):

    try:

        source = file_path.read_text(
            encoding="utf-8"
        )

        tree = ast.parse(source)

        functions = []
        classes = []
        imports = []

        for node in ast.walk(tree):

            if isinstance(node, ast.FunctionDef):
                functions.append(node.name)

            elif isinstance(node, ast.AsyncFunctionDef):
                functions.append(node.name)

            elif isinstance(node, ast.ClassDef):
                classes.append(node.name)

            elif isinstance(node, ast.Import):

                for alias in node.names:
                    imports.append(alias.name)

            elif isinstance(node, ast.ImportFrom):

                if node.module:
                    imports.append(node.module)

        return {
            "functions": functions,
            "classes": classes,
            "imports": imports
        }

    except Exception as error:

        return {
            "functions": [],
            "classes": [],
            "imports": [],
            "error": str(error)
        }