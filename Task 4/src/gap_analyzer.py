"""
Candidate-Job Description Gap Analyzer & Skill Alignment Engine
"""

from typing import Dict, Any, List, Set

class GapAnalyzer:
    """Analyzes candidate profile alignment against target job description requirements."""

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        s = skill.lower().strip()
        # Clean common synonyms
        replacements = {
            "react": "react.js",
            "reactjs": "react.js",
            "next": "next.js",
            "nextjs": "next.js",
            "node": "node.js",
            "nodejs": "node.js",
            "golang": "go",
            "postgres": "postgresql",
            "scikit": "scikit-learn",
            "sklearn": "scikit-learn",
            "tailwind": "tailwindcss",
            "ci cd": "ci/cd",
            "ci/cd pipelines": "ci/cd"
        }
        for k, v in replacements.items():
            if s == k:
                return v
        return s

    @classmethod
    def analyze(cls, profile: Dict[str, Any], job_desc: Dict[str, Any]) -> Dict[str, Any]:
        """Performs multi-dimensional gap analysis between intern profile and job description."""
        
        # 1. Collect skills from candidate
        cand_tech_skills = profile.get("technical_skills", [])
        cand_project_skills = []
        for proj in profile.get("projects", []):
            cand_project_skills.extend(proj.get("tech", []))
        
        all_cand_skills_raw = set(cand_tech_skills + cand_project_skills)
        cand_skills_norm = {cls._normalize_skill(s): s for s in all_cand_skills_raw}

        # 2. Collect skills from JD
        jd_req_raw = job_desc.get("required_skills", [])
        jd_pref_raw = job_desc.get("preferred_skills", [])

        jd_req_norm = {cls._normalize_skill(s): s for s in jd_req_raw}
        jd_pref_norm = {cls._normalize_skill(s): s for s in jd_pref_raw}

        # 3. Calculate intersections and differences
        matched_req = []
        missing_req = []
        for norm_s, orig_s in jd_req_norm.items():
            if norm_s in cand_skills_norm or any(norm_s in c or c in norm_s for c in cand_skills_norm):
                matched_req.append(orig_s)
            else:
                missing_req.append(orig_s)

        matched_pref = []
        missing_pref = []
        for norm_s, orig_s in jd_pref_norm.items():
            if norm_s in cand_skills_norm or any(norm_s in c or c in norm_s for c in cand_skills_norm):
                matched_pref.append(orig_s)
            else:
                missing_pref.append(orig_s)

        surplus_skills = []
        all_jd_norm = set(jd_req_norm.keys()) | set(jd_pref_norm.keys())
        for norm_s, orig_s in cand_skills_norm.items():
            if not any(norm_s in j or j in norm_s for j in all_jd_norm):
                surplus_skills.append(orig_s)

        # 4. Compute Scores
        req_total = len(jd_req_raw) if jd_req_raw else 1
        pref_total = len(jd_pref_raw) if jd_pref_raw else 1

        req_match_pct = round((len(matched_req) / req_total) * 100, 1)
        pref_match_pct = round((len(matched_pref) / pref_total) * 100, 1)

        # Track Alignment
        cand_track = profile.get("track", "").lower()
        jd_track = job_desc.get("track", "").lower()
        track_alignment_score = 100 if cand_track == jd_track or (cand_track in jd_track or jd_track in cand_track) else 65

        # Project Alignment
        proj_count = len(profile.get("projects", []))
        proj_score = min(100, proj_count * 45)

        # Overall composite fit score (Weighted)
        # 50% Required skills + 20% Preferred skills + 15% Track Fit + 15% Project Depth
        overall_fit = round(
            (req_match_pct * 0.50) +
            (pref_match_pct * 0.20) +
            (track_alignment_score * 0.15) +
            (proj_score * 0.15),
            1
        )
        overall_fit = min(100.0, max(0.0, overall_fit))

        # 5. Recommendation Strategy
        recommendations = []
        if matched_req:
            recommendations.append(f"Validate hands-on depth in core strengths: {', '.join(matched_req[:3])}.")
        if missing_req:
            recommendations.append(f"Probe foundational learning agility regarding missing required skills: {', '.join(missing_req[:3])}.")
        if profile.get("projects"):
            recommendations.append(f"Conduct deep-dive on flagship project: '{profile['projects'][0].get('title', 'Portfolio Project')}'.")
        if surplus_skills:
            recommendations.append(f"Inquire how candidate's unique skills ({', '.join(surplus_skills[:2])}) can add cross-disciplinary value.")

        return {
            "overall_fit_score": overall_fit,
            "required_match_pct": req_match_pct,
            "preferred_match_pct": pref_match_pct,
            "matched_required_skills": matched_req,
            "missing_required_skills": missing_req,
            "matched_preferred_skills": matched_pref,
            "missing_preferred_skills": missing_pref,
            "surplus_skills": surplus_skills,
            "radar_dimensions": {
                "Core Technical Match": req_match_pct,
                "Preferred Tooling": pref_match_pct,
                "Track Alignment": track_alignment_score,
                "Project Relevance": proj_score,
                "Academic / Foundational": min(100, int(profile.get("gpa", 3.0) / 4.0 * 100))
            },
            "recommendations": recommendations
        }
