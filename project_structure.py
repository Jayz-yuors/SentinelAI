#!/usr/bin/env python3
"""Print/export a readable project folder tree. Read-only; does not change files."""
from __future__ import annotations
import argparse
import json
from pathlib import Path

EXCLUDED_DIRS = {
    ".git", ".idea", ".vscode", "__pycache__", ".pytest_cache",
    ".mypy_cache", ".ruff_cache", ".venv", "venv", "env",
    "node_modules", "dist", "build", "target", ".next",
    "coverage", "site-packages",
}
EXCLUDED_FILES = {".env", ".env.local", ".env.production", "id_rsa", "id_ed25519"}
EXCLUDED_SUFFIXES = {".pyc", ".pyo", ".log"}

def excluded(path: Path, include_all: bool) -> bool:
    if include_all:
        return False
    if path.is_dir() and path.name in EXCLUDED_DIRS:
        return True
    if path.is_file():
        return path.name in EXCLUDED_FILES or path.suffix.lower() in EXCLUDED_SUFFIXES
    return False

def build_tree(root: Path, include_all: bool = False, max_depth: int | None = None):
    def visit(folder: Path, depth: int):
        result = {"name": folder.name, "type": "directory", "children": []}
        try:
            children = sorted(folder.iterdir(), key=lambda p: (not p.is_dir(), p.name.lower()))
        except (PermissionError, OSError) as exc:
            result["error"] = str(exc)
            return result
        for child in children:
            if excluded(child, include_all):
                continue
            if child.is_dir():
                if max_depth is not None and depth >= max_depth:
                    result["children"].append({
                        "name": child.name, "type": "directory",
                        "children": [], "truncated": True
                    })
                else:
                    result["children"].append(visit(child, depth + 1))
            else:
                try:
                    size = child.stat().st_size
                except OSError:
                    size = None
                result["children"].append({
                    "name": child.name, "type": "file", "size_bytes": size
                })
        return result
    return visit(root, 0)

def render_tree(node, prefix=""):
    lines = [node["name"] + ("/" if node["type"] == "directory" else "")]
    children = node.get("children", [])
    for i, child in enumerate(children):
        last = i == len(children) - 1
        branch = "`-- " if last else "|-- "
        continuation = "    " if last else "|   "
        label = child["name"] + ("/" if child["type"] == "directory" else "")
        if child["type"] == "file" and child.get("size_bytes") is not None:
            label += f"  ({child['size_bytes']:,} bytes)"
        lines.append(prefix + branch + label)
        if child["type"] == "directory" and child.get("children"):
            nested = render_tree(
                {"name": "", "type": "directory", "children": child["children"]},
                prefix + continuation
            )
            lines.extend(nested[1:])
        if child.get("truncated"):
            lines.append(prefix + continuation + "`-- ... (depth limit)")
    return lines

def main():
    parser = argparse.ArgumentParser(description="Print/export a project folder tree.")
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parent),
                        help="Project root; defaults to the folder containing this script.")
    parser.add_argument("--output", "-o", help="Save output to a file; use .json for JSON.")
    parser.add_argument("--all", action="store_true",
                        help="Include .git, venv, node_modules, logs, and generated files.")
    parser.add_argument("--max-depth", type=int, default=None,
                        help="Limit recursion depth (root is depth 0).")
    args = parser.parse_args()
    root = Path(args.root).expanduser().resolve()
    if not root.exists() or not root.is_dir():
        parser.error(f"Project folder does not exist or is not a directory: {root}")
    if args.max_depth is not None and args.max_depth < 0:
        parser.error("--max-depth must be zero or greater")
    tree = build_tree(root, include_all=args.all, max_depth=args.max_depth)
    output = (json.dumps(tree, indent=2, ensure_ascii=False)
              if args.output and Path(args.output).suffix.lower() == ".json"
              else "\n".join(render_tree(tree)))
    if args.output:
        destination = Path(args.output).expanduser().resolve()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(output + "\n", encoding="utf-8")
        print(f"Tree saved to: {destination}")
    else:
        print(output)

if __name__ == "__main__":
    main()
