"""
Prompt Templates and System Directives for LLM Text Generation
"""

from typing import Dict, Any, List

SYSTEM_PROMPT_INTERVIEWER = """You are an expert Technical Interview Architect and Engineering Leader at a top-tier tech organization.
Your objective is to generate rigorous, highly tailored, and role-calibrated interview question sets for intern candidates.

Guiding Principles:
1. Ground questions directly in the candidate's profile, projects, and target Job Description.
2. Formulate behavioral questions using the STAR framework (Situation, Task, Action, Result) with clear behavioral indicators.
3. Formulate technical questions calibrated across 3 difficulty tiers (Easy/Fundamentals, Medium/Applied, Hard/System Architecture).
4. Provide structured scoring rubrics on a 1-5 scale with concrete expected answer points, green flags, and follow-up probes.
5. Return clean, valid JSON formatted output matching the requested schema.
"""

def build_interview_kit_prompt(
    profile: Dict[str, Any],
    job_desc: Dict[str, Any],
    gap_analysis: Dict[str, Any],
    num_technical: int = 5,
    num_behavioral: int = 3,
    num_project: int = 2
) -> str:
    """Builds a comprehensive prompt for LLM text generation engines."""
    
    projects_text = "\n".join([
        f"- Project '{p.get('title')}': {p.get('desc')} (Tech: {', '.join(p.get('tech', []))})"
        for p in profile.get("projects", [])
    ])

    return f"""
Generate an automated, role-specific Interview Question Kit for the following candidate and position:

### CANDIDATE PROFILE:
- Name: {profile.get('name')}
- Degree: {profile.get('degree')} from {profile.get('university')} (GPA: {profile.get('gpa')})
- Target Track: {profile.get('track')}
- Technical Skills: {', '.join(profile.get('technical_skills', []))}
- Experience Summary: {profile.get('experience_summary')}
- Projects:
{projects_text}
- Identified Strengths: {', '.join(profile.get('strengths', []))}
- Areas to Probe: {', '.join(profile.get('areas_to_probe', []))}

### TARGET JOB DESCRIPTION:
- Role Title: {job_desc.get('title')}
- Track: {job_desc.get('track')}
- Department: {job_desc.get('department')}
- Required Skills: {', '.join(job_desc.get('required_skills', []))}
- Preferred Skills: {', '.join(job_desc.get('preferred_skills', []))}
- Core Responsibilities: {'; '.join(job_desc.get('responsibilities', []))}

### GAP ANALYSIS CONTEXT:
- Overall Match Fit: {gap_analysis.get('overall_fit_score')}%
- Matched Core Skills: {', '.join(gap_analysis.get('matched_required_skills', []))}
- Missing Skills (Areas to Probe): {', '.join(gap_analysis.get('missing_required_skills', []))}
- Candidate Bonus Skills: {', '.join(gap_analysis.get('surplus_skills', []))}

### GENERATION REQUIREMENTS:
Please generate:
1. Exactly {num_technical} Technical Questions (covering Easy, Medium, Hard difficulty, targeting matched competencies and probing gaps).
2. Exactly {num_behavioral} Behavioral Questions (using the STAR methodology with explicit competency tags and Green/Red flags).
3. Exactly {num_project} Project Deep-Dive Questions (specifically probing the candidate's actual projects listed above).

Provide the output formatted as a structured JSON object with the following schema:
{{
  "interview_meta": {{
    "candidate_name": "{profile.get('name')}",
    "target_role": "{job_desc.get('title')}",
    "fit_score": {gap_analysis.get('overall_fit_score')}
  }},
  "technical_questions": [
    {{
      "id": "T-1",
      "category": "Technical",
      "topic": "string",
      "skill_targeted": "string",
      "difficulty": "Easy | Medium | Hard",
      "question": "string",
      "rationale": "Why this question is tailored for this candidate and JD",
      "expected_answer_points": ["point 1", "point 2", "point 3"],
      "rubric_5_scale": "Description of what constitutes a 5/5 expert answer",
      "follow_up_probe": "string"
    }}
  ],
  "behavioral_questions": [
    {{
      "id": "B-1",
      "category": "Behavioral",
      "competency": "string",
      "difficulty": "Medium",
      "question": "string",
      "star_framework": {{
        "situation": "string",
        "task": "string",
        "action": "string",
        "result": "string"
      }},
      "green_flags": ["positive signal 1", "positive signal 2"],
      "red_flags": ["warning signal 1", "warning signal 2"],
      "rubric_5_scale": "string",
      "follow_up_probe": "string"
    }}
  ],
  "project_deep_dive_questions": [
    {{
      "id": "P-1",
      "category": "Project Deep Dive",
      "project_name": "string",
      "question": "string",
      "architectural_focus": "string",
      "expected_answer_points": ["point 1", "point 2"],
      "follow_up_probe": "string"
    }}
  ]
}}
"""
