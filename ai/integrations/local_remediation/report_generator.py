from __future__ import annotations
import html
import json
from datetime import datetime
from pathlib import Path
from typing import Any

class SentinelAIReportGenerator:
    """Generate one consolidated HTML + PDF remediation report locally."""

    def __init__(self, output_root: str | Path = ".sentinelai/reports"):
        self.output_root = Path(output_root).resolve()

    @staticmethod
    def _obj(value: Any) -> Any:
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        if isinstance(value, dict):
            return {str(k): SentinelAIReportGenerator._obj(v) for k, v in value.items()}
        if isinstance(value, (list, tuple)):
            return [SentinelAIReportGenerator._obj(v) for v in value]
        if hasattr(value, "to_dict"):
            return SentinelAIReportGenerator._obj(value.to_dict())
        if hasattr(value, "__dict__"):
            return {k: SentinelAIReportGenerator._obj(v) for k, v in vars(value).items()}
        return str(value)

    def generate(self, evidence: dict[str, Any], run_id: str | None = None) -> dict[str, str]:
        run_id = run_id or datetime.now().strftime("%Y%m%d-%H%M%S")
        self.output_root.mkdir(parents=True, exist_ok=True)
        html_path = self.output_root / f"SENTINELAI_REMEDIATION_REPORT_{run_id}.html"
        pdf_path = self.output_root / f"SENTINELAI_REMEDIATION_REPORT_{run_id}.pdf"

        def esc(v):
            return html.escape("" if v is None else str(v))

        def block(title, value):
            data = json.dumps(self._obj(value), indent=2, ensure_ascii=False, default=str)
            return "<h3>" + esc(title) + "</h3><pre>" + esc(data) + "</pre>"

        def section(title, body):
            return '<section><div class="kicker">SENTINELAI</div><h2>' + esc(title) + '</h2>' + body + '</section>'

        risk_before = self._obj(evidence.get("risk_before", {}))
        risk_after = self._obj(evidence.get("risk_after", {}))
        gate = self._obj(evidence.get("security_gate", {}))
        git = self._obj(evidence.get("git_audit", {}))

        before_score = risk_before.get("overall_score", 0) if isinstance(risk_before, dict) else 0
        after_score = risk_after.get("overall_score", 0) if isinstance(risk_after, dict) else 0
        gate_ok = gate.get("allowed", False) if isinstance(gate, dict) else False

        risk_html = (
            '<div class="grid">'
            '<div class="card"><b>RISK BEFORE</b><div class="risk">' + esc(before_score) +
            '</div><div class="track"><div class="fill" style="width:' + str(before_score) + '%"></div></div></div>'
            '<div class="card"><b>RISK AFTER</b><div class="risk">' + esc(after_score) +
            '</div><div class="track"><div class="fill" style="width:' + str(after_score) + '%"></div></div></div>'
            '</div>'
        )

        lineage = (
            '<table><tr><th>Stage</th><th>Meaning</th><th>Evidence</th></tr>'
            '<tr><td>MAIN</td><td>Original repository baseline</td><td>' + esc(evidence.get("original_commit")) + '</td></tr>'
            '<tr><td>LOCAL</td><td>Developer-provided proposal</td><td>' + esc(evidence.get("local_file")) + '</td></tr>'
            '<tr><td>AI REVIEW</td><td>Existing SentinelAI review</td><td>' + esc(self._obj(evidence.get("ai_review", {}))) + '</td></tr>'
            '<tr><td>AI REMEDIATION</td><td>Existing SentinelAI remediation</td><td>' + esc(self._obj(evidence.get("ai_remediation", {}))) + '</td></tr>'
            '<tr><td>VERIFICATION</td><td>Post-change verification</td><td>' + esc(self._obj(evidence.get("verification", {}))) + '</td></tr>'
            '<tr><td>CANDIDATE</td><td>Isolated branch</td><td>' + esc(git.get("candidate_branch", "") if isinstance(git, dict) else "") + '</td></tr>'
            '</table>'
            '<div class="flow">MAIN → LOCAL → AI REVIEW → AI REMEDIATION → VERIFICATION → SECURITY RESCAN → RISK → GATE → CANDIDATE → PR</div>'
        )

        document = """<!doctype html><html><head><meta charset="utf-8">
<title>SentinelAI Remediation Report</title>
<style>
body{margin:0;background:#edf3f8;color:#162235;font-family:Arial,Helvetica,sans-serif}
.cover{padding:70px;color:white;background:linear-gradient(135deg,#07111f,#123452,#075985)}
.brand{color:#7dd3fc;letter-spacing:4px;font-size:12px;font-weight:700}
h1{font-size:44px;line-height:1.05;margin:70px 0 18px}.subtitle{color:#dbeafe;font-size:17px;line-height:1.6}
.meta{margin-top:45px;padding:20px;border:1px solid #46627e;border-radius:14px;background:#0b1728}
.container{max-width:980px;margin:auto;background:white;padding:40px 48px}
section{margin-bottom:42px}.kicker{color:#2563eb;font-size:11px;font-weight:800;letter-spacing:2px}
h2{font-size:27px;margin:5px 0 18px}h3{font-size:16px;margin:20px 0 8px}
p{font-size:14px;line-height:1.65}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.card{border:1px solid #dbe3ee;border-radius:12px;padding:18px;background:#fbfdff}
.risk{font-size:32px;font-weight:800;margin:8px 0}.track{height:11px;background:#e2e8f0;border-radius:20px;overflow:hidden}
.fill{height:100%;background:#2563eb}table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:10px;border-bottom:1px solid #e2e8f0;text-align:left;vertical-align:top}th{background:#f8fafc}
pre{background:#0b1220;color:#dbeafe;padding:15px;border-radius:10px;font-size:10px;line-height:1.45;white-space:pre-wrap}
.flow{margin-top:16px;padding:18px;border:1px solid #dbe3ee;border-radius:12px;background:#f8fbff;font-family:Consolas,monospace;line-height:1.6}
</style></head><body>
<div class="cover"><div class="brand">SENTINELAI · DEVSECOPS EVIDENCE</div>
<h1>Remediation &amp;<br>Reasoning Report</h1>
<div class="subtitle">Developer request → original baseline → local proposal → AI reasoning → verification → security → risk → Git/GitHub.</div>
<div class="meta">
<div><b>Repository:</b> """ + esc(evidence.get("repository_url")) + """</div>
<div><b>Target:</b> """ + esc(evidence.get("target")) + """</div>
<div><b>Run ID:</b> """ + esc(run_id) + """</div>
<div><b>Candidate:</b> """ + esc(git.get("candidate_branch","") if isinstance(git,dict) else "") + """</div>
<div><b>Security Gate:</b> """ + ("PASSED" if gate_ok else "NOT PASSED") + """</div>
</div></div><div class="container">
""" + section("1. Executive Summary", '<div class="card"><b>Developer reason</b><p>' + esc(evidence.get("developer_reason")) + '</p></div>') + """
""" + section("2. Change Lineage", lineage) + """
""" + section("3. Original vs Local Proposal", block("Comparison", evidence.get("comparison_original_local", {})) + block("Diff statistics", evidence.get("diff_statistics", {}))) + """
""" + section("4. AI Reasoning", block("AI review", evidence.get("ai_review", {})) + block("AI remediation", evidence.get("ai_remediation", {})) + block("AI verification", evidence.get("verification", {}))) + """
""" + section("5. Security & Risk", risk_html + block("Risk comparison", evidence.get("risk_comparison", {})) + block("Security before", evidence.get("security_before", {})) + block("Security after", evidence.get("security_after", {})) + block("Security gate", gate)) + """
""" + section("6. Verification & Tests", block("Verification", evidence.get("verification", {})) + block("Tests", evidence.get("tests", {}))) + """
""" + section("7. Git & GitHub Audit", block("Git audit", git) + block("GitHub audit", evidence.get("github_audit", {}))) + """
""" + section("8. Final Evidence Summary", '<p>The candidate is kept separate from main until the configured GitHub review/check workflow permits merge. Missing evidence is reported as missing rather than inferred.</p>') + """
</div></body></html>"""

        html_path.write_text(document, encoding="utf-8")
        self._write_pdf(pdf_path, evidence, run_id)
        return {"html": str(html_path), "pdf": str(pdf_path)}

    def _write_pdf(self, path, evidence, run_id):
        from reportlab.lib import colors
        from reportlab.lib.pagesizes import A4
        from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
        from reportlab.lib.units import mm
        from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak

        styles = getSampleStyleSheet()
        title = ParagraphStyle("SITitle", parent=styles["Title"], fontSize=27, leading=31, textColor=colors.HexColor("#0f2f4f"))
        h = ParagraphStyle("SIH", parent=styles["Heading1"], fontSize=18, textColor=colors.HexColor("#1d4ed8"))
        body = ParagraphStyle("SIBody", parent=styles["BodyText"], fontSize=9.5, leading=14)
        small = ParagraphStyle("SISmall", parent=styles["BodyText"], fontSize=7.2, leading=9.5)

        doc = SimpleDocTemplate(str(path), pagesize=A4, rightMargin=15*mm, leftMargin=15*mm,
                                topMargin=14*mm, bottomMargin=14*mm,
                                title="SentinelAI Remediation & Reasoning Report", author="SentinelAI")
        story = [
            Spacer(1,25*mm),
            Paragraph("SENTINELAI", ParagraphStyle("brand", parent=body, fontSize=11, textColor=colors.HexColor("#0284c7"), alignment=1)),
            Spacer(1,4*mm),
            Paragraph("REMEDIATION &amp; REASONING REPORT", title),
            Paragraph("Locally generated evidence document — no paid document-generation API.", body),
            Spacer(1,10*mm)
        ]
        meta = [
            ["Repository", str(evidence.get("repository_url",""))],
            ["Target", str(evidence.get("target",""))],
            ["Run ID", run_id],
            ["Candidate", str((evidence.get("git_audit") or {}).get("candidate_branch",""))],
            ["Gate", "PASSED" if (evidence.get("security_gate") or {}).get("allowed") else "NOT PASSED"]
        ]
        table = Table(meta, colWidths=[35*mm,132*mm])
        table.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(0,-1),colors.HexColor("#e8f1ff")),
            ("TEXTCOLOR",(0,0),(0,-1),colors.HexColor("#1e3a8a")),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cbd5e1")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("PADDING",(0,0),(-1,-1),7),("FONTSIZE",(0,0),(-1,-1),8)
        ]))
        story += [table, PageBreak(), Paragraph("1. Developer Request",h),
                  Paragraph(str(evidence.get("developer_reason","")),body),
                  Paragraph("2. Evidence Lineage",h)]
        lineage = [
            ["MAIN","Original baseline",str(evidence.get("original_commit",""))],
            ["LOCAL","Developer proposal",str(evidence.get("local_file",""))],
            ["AI REVIEW","Existing review",str(evidence.get("ai_review",{}))],
            ["AI REMEDIATION","Existing remediation",str(evidence.get("ai_remediation",{}))],
            ["VERIFICATION","Existing verification",str(evidence.get("verification",{}))],
            ["CANDIDATE","Isolated branch",str((evidence.get("git_audit") or {}).get("candidate_branch",""))]
        ]
        lt=Table(lineage,colWidths=[30*mm,55*mm,82*mm])
        lt.setStyle(TableStyle([
            ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#0f2f4f")),
            ("TEXTCOLOR",(0,0),(-1,0),colors.white),
            ("GRID",(0,0),(-1,-1),0.3,colors.HexColor("#cbd5e1")),
            ("VALIGN",(0,0),(-1,-1),"TOP"),("FONTSIZE",(0,0),(-1,-1),7.2),("PADDING",(0,0),(-1,-1),6)
        ]))
        story.append(lt)
        for key, heading in [
            ("comparison_original_local","3. Original vs Local"),
            ("ai_review","4. AI Review"),
            ("ai_remediation","5. AI Remediation"),
            ("verification","6. Verification"),
            ("security_before","7. Security Before"),
            ("security_after","8. Security After"),
            ("risk_before","9. Risk Before"),
            ("risk_after","10. Risk After"),
            ("risk_comparison","11. Risk Comparison"),
            ("security_gate","12. Security Gate"),
            ("git_audit","13. Git Audit"),
            ("github_audit","14. GitHub Audit"),
            ("tests","15. Tests")
        ]:
            story.append(Paragraph(heading,h))
            data=json.dumps(self._obj(evidence.get(key,{})),indent=2,ensure_ascii=False,default=str)
            for line in data.splitlines() or [""]:
                story.append(Paragraph(html.escape(line).replace(" ","&nbsp;"),small))
        doc.build(story)
