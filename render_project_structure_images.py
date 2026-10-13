#!/usr/bin/env python3
"""Render the live project tree as crisp, standalone SVG overview/detail pages."""
from __future__ import annotations

import html
from pathlib import Path

from project_structure import build_tree


ROOT = Path(__file__).resolve().parent
OUT = ROOT / "artifacts" / "project_structure_images"
EXCLUDED_TOP_LEVEL = {".git"}


def descendants(node: dict, depth: int = 1) -> list[tuple[str, str, int]]:
    rows: list[tuple[str, str, int]] = []
    for child in node.get("children", []):
        kind = child["type"]
        rows.append((child["name"], kind, depth))
        if kind == "directory":
            rows.extend(descendants(child, depth + 1))
    return rows


def svg_page(title: str, subtitle: str, rows: list[tuple[str, str, int]], path: Path) -> None:
    width = 1320
    row_h = 34
    top = 170
    height = max(310, top + len(rows) * row_h + 70)
    bits = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}">',
        '<defs><linearGradient id="bg" x2="1" y2="1"><stop stop-color="#07111f"/><stop offset="1" stop-color="#101c31"/></linearGradient></defs>',
        f'<rect width="{width}" height="{height}" rx="26" fill="url(#bg)"/>',
        '<text x="64" y="66" fill="#f1f5f9" font-family="Segoe UI,Arial,sans-serif" font-size="34" font-weight="700">SentinelAI · Project Structure</text>',
        f'<text x="64" y="111" fill="#8da3bd" font-family="Segoe UI,Arial,sans-serif" font-size="20">{html.escape(title)}  /  {html.escape(subtitle)}</text>',
        '<rect x="64" y="137" width="1192" height="1" fill="#26374d"/>',
    ]
    for i, (name, kind, depth) in enumerate(rows):
        y = top + i * row_h
        indent = min(depth - 1, 8) * 28
        color = "#59d3b4" if kind == "directory" else "#b8c7d9"
        marker = "▸" if kind == "directory" else "·"
        bits.append(f'<text x="{75 + indent}" y="{y}" fill="{color}" font-family="Segoe UI,Arial,sans-serif" font-size="19">{marker}</text>')
        bits.append(f'<text x="{104 + indent}" y="{y}" fill="{color}" font-family="Cascadia Code,Consolas,monospace" font-size="17">{html.escape(name)}{"/" if kind == "directory" else ""}</text>')
        bits.append(f'<text x="1215" y="{y}" text-anchor="end" fill="#61758d" font-family="Segoe UI,Arial,sans-serif" font-size="13">{kind}</text>')
    if not rows:
        bits.append('<text x="80" y="200" fill="#b8c7d9" font-family="Segoe UI,Arial,sans-serif" font-size="20">(empty)</text>')
    bits.append(f'<text x="64" y="{height - 28}" fill="#61758d" font-family="Segoe UI,Arial,sans-serif" font-size="13">Generated from the current workspace tree · excluded environment, cache, and Git internals</text>')
    bits.append('</svg>')
    path.write_text("\n".join(bits), encoding="utf-8")


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    tree = build_tree(ROOT)
    main_dirs = [n for n in tree["children"] if n["type"] == "directory" and n["name"] not in EXCLUDED_TOP_LEVEL]
    main_files = [n for n in tree["children"] if n["type"] == "file"]
    overview = [(n["name"], n["type"], 1) for n in main_dirs + main_files]
    svg_page("01 · Root overview", "main folders and root files", overview, OUT / "01_root_overview.svg")

    # One readable page per top-level folder, plus focused pages for the largest nested areas.
    for i, node in enumerate(main_dirs, 2):
        rows = descendants(node)
        svg_page(f"{i:02d} · {node['name']}/", f"{len(rows)} visible entries", rows, OUT / f"{i:02d}_{node['name'].strip('.').replace('.', '_')}.svg")
        if len(rows) > 55:
            for j, child in enumerate(node.get("children", []), 1):
                if child["type"] == "directory":
                    nested_rows = descendants(child)
                    svg_page(f"{i:02d}.{j:02d} · {node['name']}/{child['name']}/", f"{len(nested_rows)} visible entries", nested_rows, OUT / f"{i:02d}_{node['name'].strip('.').replace('.', '_')}_{j:02d}_{child['name']}.svg")
    print(f"Generated {len(list(OUT.glob('*.svg')))} SVG images in {OUT}")


if __name__ == "__main__":
    main()
