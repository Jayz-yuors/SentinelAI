from html import escape
from pathlib import Path

def _summary(profile):
    if profile is None: return {}
    return {
        "score": getattr(profile,"overall_score",0),
        "level": getattr(profile,"overall_level","INFO"),
        "findings": getattr(profile,"finding_count",0),
        "affected_files": getattr(profile,"affected_files",0),
        "affected_dependencies": getattr(profile,"affected_dependencies",0),
        "severity_counts": getattr(profile,"severity_counts",{}),
    }

def render_html(analysis_id, repository, before, after, comparison, gate, changes) -> str:
    b,a=_summary(before),_summary(after)
    rows="".join(f"<tr><td>{escape(str(k))}</td><td>{escape(str(v))}</td></tr>" for k,v in a.get("severity_counts",{}).items())
    return f"""<!doctype html><html><head><meta charset="utf-8"><title>SentinelAI Report</title>
<style>body{{font-family:Arial;max-width:1100px;margin:40px auto}}table{{border-collapse:collapse;width:100%}}td,th{{border:1px solid #ccc;padding:8px}}pre{{background:#f5f5f5;padding:16px;overflow:auto}}</style></head>
<body><h1>SentinelAI Security Analysis</h1><p><b>Analysis:</b> {escape(analysis_id)}</p><p><b>Repository:</b> {escape(str(repository))}</p>
<h2>Risk</h2><table><tr><th></th><th>Before</th><th>After</th></tr>
<tr><td>Score</td><td>{b.get("score")}</td><td>{a.get("score")}</td></tr><tr><td>Level</td><td>{b.get("level")}</td><td>{a.get("level")}</td></tr><tr><td>Findings</td><td>{b.get("findings")}</td><td>{a.get("findings")}</td></tr></table>
<h2>Gate</h2><pre>{escape(str(gate))}</pre><h2>Comparison</h2><pre>{escape(str(comparison))}</pre>
<h2>Changed Files</h2><pre>{escape(str(changes))}</pre><h2>After Severity Counts</h2><table>{rows}</table></body></html>"""

def write_pdf(path: Path, title: str, content: str):
    from reportlab.lib.pagesizes import A4
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet
    doc=SimpleDocTemplate(str(path), pagesize=A4)
    styles=getSampleStyleSheet()
    story=[Paragraph(title,styles["Title"]),Spacer(1,12)]
    for line in content.splitlines():
        if line.strip():
            story.append(Paragraph(escape(line[:3000]),styles["BodyText"]))
            story.append(Spacer(1,6))
    doc.build(story)
