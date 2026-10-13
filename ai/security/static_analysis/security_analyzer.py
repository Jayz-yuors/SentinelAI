import ast
from pathlib import Path


# ============================================================
# DANGEROUS FUNCTIONS
# ============================================================

DANGEROUS_FUNCTIONS = {

    "eval": (
        "Use of eval() may execute arbitrary code"
    ),

    "exec": (
        "Use of exec() may execute arbitrary code"
    ),

    "compile": (
        "Dynamic compilation can introduce code execution risks"
    ),

    "input": (
        "Input should be validated before sensitive processing"
    ),
}


# ============================================================
# PYTHON FILE ANALYSIS
# ============================================================

def analyze_python_file(
    file_path: Path,
    repository_path: Path
):

    findings = []

    try:

        source = file_path.read_text(
            encoding="utf-8",
            errors="ignore"
        )

        tree = ast.parse(
            source
        )

    except (
        OSError,
        SyntaxError
    ):

        return findings

    relative_path = str(
        file_path.relative_to(
            repository_path
        )
    )

    for node in ast.walk(tree):

        if isinstance(
            node,
            ast.Call
        ):

            function_name = None

            if isinstance(
                node.func,
                ast.Name
            ):

                function_name = (
                    node.func.id
                )

            if function_name in DANGEROUS_FUNCTIONS:

                severity = (
                    "HIGH"
                    if function_name
                    in {
                        "eval",
                        "exec"
                    }
                    else "MEDIUM"
                )

                findings.append({

                    "type":
                        "STATIC_ANALYSIS",

                    "category":
                        "DANGEROUS_FUNCTION",

                    "file":
                        relative_path,

                    "line":
                        getattr(
                            node,
                            "lineno",
                            None
                        ),

                    "severity":
                        severity,

                    "message":
                        DANGEROUS_FUNCTIONS[
                            function_name
                        ],

                    "function":
                        function_name
                })

        # ----------------------------------------------------
        # Hard-coded command execution
        # ----------------------------------------------------

        if isinstance(
            node,
            ast.Call
        ):

            if (
                isinstance(
                    node.func,
                    ast.Attribute
                )
                and node.func.attr
                in {
                    "system",
                    "popen"
                }
            ):

                findings.append({

                    "type":
                        "STATIC_ANALYSIS",

                    "category":
                        "COMMAND_EXECUTION",

                    "file":
                        relative_path,

                    "line":
                        getattr(
                            node,
                            "lineno",
                            None
                        ),

                    "severity":
                        "HIGH",

                    "message":
                        "Potentially unsafe command execution"
                })

    return findings


# ============================================================
# REPOSITORY ANALYSIS
# ============================================================

def analyze_security(
    repository_path: Path
):

    findings = []

    for file_path in repository_path.rglob("*.py"):

        if ".git" in file_path.parts:
            continue

        findings.extend(
            analyze_python_file(
                file_path,
                repository_path
            )
        )

    return {

        "scanner":
            "static_security_analyzer",

        "totalFindings":
            len(findings),

        "findings":
            findings
    }