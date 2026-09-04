"""
Interview Scorecard and Rubric Evaluation Engine
"""

from typing import Dict, Any, List

class RubricEngine:
    """Generates structured evaluation rubrics and interview scorecards."""

    RUBRIC_LEVELS = {
        1: {
            "title": "Unsatisfactory (1/5)",
            "summary": "Struggles with foundational concepts, provides incorrect reasoning, or exhibits critical red flags."
        },
        2: {
            "title": "Developing / Basic (2/5)",
            "summary": "Demonstrates superficial knowledge, requires heavy prompting, misses core trade-offs."
        },
        3: {
            "title": "Competent / Solid (3/5)",
            "summary": "Provides sound technical explanation, understands standard best practices and debugging."
        },
        4: {
            "title": "Advanced / Strong (4/5)",
            "summary": "Deep architectural understanding, articulates trade-offs proactively, references production realities."
        },
        5: {
            "title": "Exceptional / Expert (5/5)",
            "summary": "Exemplary mastery, comprehensive system design depth, outstanding clarity, engineering leadership."
        }
    }

    EVALUATION_CRITERIA = [
        {"dimension": "Technical Depth & Accuracy", "weight": "35%", "desc": "Correctness, foundational depth, and understanding of mechanics"},
        {"dimension": "Problem Solving & Analytical Agility", "weight": "25%", "desc": "Methodical debugging, structured decomposition, and trade-off evaluation"},
        {"dimension": "Communication & STAR Structure", "weight": "20%", "desc": "Clarity, concise articulation, structured STAR storytelling for behavioral questions"},
        {"dimension": "Curiosity & Learning Agility", "weight": "20%", "desc": "Receptiveness to hints, self-directed exploration, and passion for engineering"}
    ]

    @classmethod
    def generate_scorecard_template(cls, kit: Dict[str, Any]) -> Dict[str, Any]:
        """Creates a ready-to-fill structured scorecard for interviewers."""
        meta = kit.get("interview_meta", {})
        
        tech_items = [
            {"id": q["id"], "topic": q.get("topic"), "difficulty": q.get("difficulty"), "score": None, "notes": ""}
            for q in kit.get("technical_questions", [])
        ]
        
        beh_items = [
            {"id": q["id"], "competency": q.get("competency"), "score": None, "notes": ""}
            for q in kit.get("behavioral_questions", [])
        ]
        
        proj_items = [
            {"id": q["id"], "project_name": q.get("project_name"), "score": None, "notes": ""}
            for q in kit.get("project_deep_dive_questions", [])
        ]

        return {
            "candidate_name": meta.get("candidate_name", "Candidate"),
            "target_role": meta.get("target_role", "Role"),
            "rubric_scale": cls.RUBRIC_LEVELS,
            "dimensions": cls.EVALUATION_CRITERIA,
            "scorecard_entries": {
                "technical": tech_items,
                "behavioral": beh_items,
                "project_deep_dive": proj_items
            },
            "overall_recommendation": ["Strong Hire", "Hire", "Leaning Hire", "No Hire", "Strong No Hire"]
        }
