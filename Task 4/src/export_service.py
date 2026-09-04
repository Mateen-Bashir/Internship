"""
Export Service for Interview Question Kits
Supports Markdown (.md), JSON (.json), and Printable HTML / PDF formats.
"""

import json
import os
from typing import Dict, Any

class ExportService:
    """Handles formatted file exports for interview packets."""

    @staticmethod
    def to_markdown(kit: Dict[str, Any], filepath: str) -> str:
        """Exports interview kit as clean GitHub-Flavored Markdown."""
        meta = kit.get("interview_meta", {})
        gap = kit.get("gap_analysis", {})
        tech_q = kit.get("technical_questions", [])
        beh_q = kit.get("behavioral_questions", [])
        proj_q = kit.get("project_deep_dive_questions", [])
        coding = kit.get("coding_scenario", {})

        md = []
        md.append(f"# 📋 Custom Interview Kit: {meta.get('candidate_name', 'Candidate')}")
        md.append(f"**Target Role:** {meta.get('target_role', 'Internship Role')}  ")
        md.append(f"**Track:** {meta.get('track', 'Engineering')} | **Match Fit Score:** {meta.get('fit_score', 'N/A')}%  ")
        md.append(f"**Candidate:** {meta.get('degree')} — {meta.get('university')}  ")
        md.append(f"**Engine:** {meta.get('generation_backend', 'Neural RAG Synthesizer')}  \n")
        md.append("---\n")

        # Gap Summary
        md.append("## 📊 Candidate-Job Gap Analysis")
        md.append(f"- **Matched Core Skills:** {', '.join(gap.get('matched_required_skills', ['None identified']))}")
        md.append(f"- **Missing Skills to Probe:** {', '.join(gap.get('missing_required_skills', ['None - Full Match']))}")
        md.append(f"- **Candidate Bonus Skills:** {', '.join(gap.get('surplus_skills', ['N/A']))}\n")

        if gap.get("recommendations"):
            md.append("### 🎯 Recommended Interview Strategy")
            for rec in gap.get("recommendations", []):
                md.append(f"- {rec}")
            md.append("\n")

        md.append("---\n")

        # Technical Questions
        md.append(f"## 🛠️ Technical Questions ({len(tech_q)} Questions)\n")
        for q in tech_q:
            md.append(f"### [{q.get('id')}] {q.get('topic')} — *{q.get('difficulty')} Difficulty*")
            md.append(f"**Targeted Skill:** `{q.get('skill_targeted')}`  ")
            md.append(f"**Rationale:** {q.get('rationale')}  \n")
            md.append(f"> **Question:** {q.get('question')}\n")
            md.append("**Expected Key Points:**")
            for pt in q.get("expected_answer_points", []):
                md.append(f"- {pt}")
            md.append(f"\n**Rubric (5/5 Standard):** {q.get('rubric_5_scale')}")
            md.append(f"**Follow-up Probe:** *\"{q.get('follow_up_probe')}\"*\n")

        md.append("---\n")

        # Behavioral Questions
        md.append(f"## 🤝 Behavioral Questions — STAR Framework ({len(beh_q)} Questions)\n")
        for q in beh_q:
            star = q.get("star_framework", {})
            md.append(f"### [{q.get('id')}] Competency: {q.get('competency')}")
            md.append(f"> **Question:** {q.get('question')}\n")
            md.append("**STAR Framework Expectations:**")
            md.append(f"- **Situation:** {star.get('situation')}")
            md.append(f"- **Task:** {star.get('task')}")
            md.append(f"- **Action:** {star.get('action')}")
            md.append(f"- **Result:** {star.get('result')}\n")
            md.append(f"🟢 **Green Flags:** {', '.join(q.get('green_flags', []))}")
            md.append(f"🔴 **Red Flags:** {', '.join(q.get('red_flags', []))}")
            md.append(f"**Follow-up Probe:** *\"{q.get('follow_up_probe')}\"*\n")

        md.append("---\n")

        # Project Deep-Dive
        if proj_q:
            md.append(f"## 🚀 Project Portfolio Deep-Dive ({len(proj_q)} Questions)\n")
            for q in proj_q:
                md.append(f"### [{q.get('id')}] Project: {q.get('project_name')}")
                md.append(f"**Focus:** {q.get('architectural_focus')}")
                md.append(f"> **Question:** {q.get('question')}\n")
                md.append(f"**Follow-up Probe:** *\"{q.get('follow_up_probe')}\"*\n")

        md.append("---\n")

        # Coding Scenario
        if coding:
            md.append("## 💻 Live Practical / Troubleshooting Scenario")
            md.append(f"### {coding.get('title')}")
            md.append(f"> {coding.get('scenario')}\n")
            md.append("**Evaluation Criteria:**")
            for crit in coding.get("evaluation_criteria", []):
                md.append(f"- {crit}")
            md.append("\n")

        content = "\n".join(md)
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return content

    @staticmethod
    def to_json(kit: Dict[str, Any], filepath: str) -> str:
        """Exports interview kit as formatted JSON."""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(kit, f, indent=2)
        return json.dumps(kit, indent=2)

    @staticmethod
    def to_html(kit: Dict[str, Any], filepath: str) -> str:
        """Exports interview kit as modern, print-ready HTML / PDF format."""
        meta = kit.get("interview_meta", {})
        gap = kit.get("gap_analysis", {})
        tech_q = kit.get("technical_questions", [])
        beh_q = kit.get("behavioral_questions", [])
        proj_q = kit.get("project_deep_dive_questions", [])
        coding = kit.get("coding_scenario", {})

        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Interview Packet - {meta.get('candidate_name')}</title>
    <style>
        body {{ font-family: 'Segoe UI', system-ui, -apple-system, sans-serif; line-height: 1.5; color: #1e293b; max-width: 900px; margin: 0 auto; padding: 30px; background: #f8fafc; }}
        .header {{ background: #0f172a; color: #ffffff; padding: 25px 30px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.1); }}
        .header h1 {{ margin: 0 0 10px 0; font-size: 24px; }}
        .badge {{ display: inline-block; padding: 4px 10px; border-radius: 6px; font-size: 12px; font-weight: bold; margin-right: 8px; }}
        .badge-match {{ background: #10b981; color: #fff; }}
        .badge-track {{ background: #3b82f6; color: #fff; }}
        .card {{ background: #ffffff; border: 1px solid #e2e8f0; border-radius: 10px; padding: 20px; margin-bottom: 20px; box-shadow: 0 2px 4px rgba(0,0,0,0.03); }}
        .q-box {{ background: #f1f5f9; border-left: 4px solid #3b82f6; padding: 12px 16px; border-radius: 4px; font-size: 15px; font-weight: 500; margin: 12px 0; }}
        .star-box {{ background: #fefce8; border: 1px solid #fef08a; padding: 12px; border-radius: 8px; font-size: 13px; margin-top: 10px; }}
        .rubric-tag {{ color: #0284c7; font-weight: bold; }}
        .flag-green {{ color: #16a34a; font-weight: 600; }}
        .flag-red {{ color: #dc2626; font-weight: 600; }}
        h2 {{ color: #0f172a; border-bottom: 2px solid #e2e8f0; padding-bottom: 8px; font-size: 18px; margin-top: 30px; }}
        h3 {{ color: #334155; font-size: 16px; margin-bottom: 6px; }}
        ul {{ margin-top: 6px; }}
        @media print {{ body {{ background: #fff; padding: 0; }} .card {{ page-break-inside: avoid; }} }}
    </style>
</head>
<body>
    <div class="header">
        <h1>Internee.pk Interview Assessment Packet</h1>
        <div>
            <span class="badge badge-match">Fit Score: {meta.get('fit_score')}%</span>
            <span class="badge badge-track">{meta.get('track')}</span>
        </div>
        <p style="margin: 10px 0 0 0; opacity: 0.9; font-size: 14px;">
            Candidate: <strong>{meta.get('candidate_name')}</strong> ({meta.get('degree')} &bull; {meta.get('university')})<br>
            Target Role: <strong>{meta.get('target_role')}</strong> &bull; Generated via {meta.get('generation_backend')}
        </p>
    </div>

    <div class="card">
        <h3>Candidate-Job Gap Analysis Summary</h3>
        <p><strong>Matched Core Skills:</strong> {', '.join(gap.get('matched_required_skills', []))}</p>
        <p><strong>Missing Skills to Probe:</strong> {', '.join(gap.get('missing_required_skills', ['None - Full Match']))}</p>
        <p><strong>Candidate Bonus Skills:</strong> {', '.join(gap.get('surplus_skills', []))}</p>
    </div>

    <h2>Technical Questions ({len(tech_q)})</h2>
"""
        for q in tech_q:
            html += f"""
    <div class="card">
        <h3>[{q.get('id')}] {q.get('topic')} &mdash; <small style="color: #64748b;">({q.get('difficulty')} &bull; {q.get('skill_targeted')})</small></h3>
        <p style="font-size: 13px; color: #64748b; margin: 0;"><em>Rationale: {q.get('rationale')}</em></p>
        <div class="q-box">"{q.get('question')}"</div>
        <p><strong>Expected Key Points:</strong></p>
        <ul>
            {''.join([f'<li>{p}</li>' for p in q.get('expected_answer_points', [])])}
        </ul>
        <p><span class="rubric-tag">5/5 Rubric:</span> {q.get('rubric_5_scale')}</p>
        <p style="font-size: 13px; color: #475569;"><strong>Follow-up:</strong> <em>"{q.get('follow_up_probe')}"</em></p>
    </div>
"""

        html += f"""
    <h2>Behavioral Questions &mdash; STAR Framework ({len(beh_q)})</h2>
"""
        for q in beh_q:
            star = q.get("star_framework", {})
            html += f"""
    <div class="card">
        <h3>[{q.get('id')}] Competency: {q.get('competency')}</h3>
        <div class="q-box">"{q.get('question')}"</div>
        <div class="star-box">
            <strong>STAR Expectations:</strong><br>
            <strong>S:</strong> {star.get('situation')}<br>
            <strong>T:</strong> {star.get('task')}<br>
            <strong>A:</strong> {star.get('action')}<br>
            <strong>R:</strong> {star.get('result')}
        </div>
        <p style="margin-top: 10px;"><span class="flag-green">&check; Green Flags:</span> {', '.join(q.get('green_flags', []))}</p>
        <p><span class="flag-red">&#9888; Red Flags:</span> {', '.join(q.get('red_flags', []))}</p>
    </div>
"""

        if proj_q:
            html += f"""<h2>Project Portfolio Deep-Dive ({len(proj_q)})</h2>"""
            for q in proj_q:
                html += f"""
    <div class="card">
        <h3>[{q.get('id')}] Project: {q.get('project_name')}</h3>
        <p style="font-size: 13px; color: #64748b; margin: 0;">Focus: {q.get('architectural_focus')}</p>
        <div class="q-box">"{q.get('question')}"</div>
        <p style="font-size: 13px; color: #475569;"><strong>Follow-up:</strong> <em>"{q.get('follow_up_probe')}"</em></p>
    </div>
"""

        if coding:
            html += f"""
    <h2>Live Practical & Troubleshooting Scenario</h2>
    <div class="card">
        <h3>{coding.get('title')}</h3>
        <div class="q-box">{coding.get('scenario')}</div>
        <p><strong>Evaluation Criteria:</strong></p>
        <ul>
            {''.join([f'<li>{c}</li>' for c in coding.get('evaluation_criteria', [])])}
        </ul>
    </div>
"""

        html += """
</body>
</html>
"""
        os.makedirs(os.path.dirname(filepath) or ".", exist_ok=True)
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html)
        return html
