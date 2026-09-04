"""
Mock Interview Response Grader and Feedback Engine
Evaluates candidate answers against rubrics, expected points, and STAR framework criteria.
"""

from typing import Dict, Any, List
import re

class MockResponseEvaluator:
    """Evaluates candidate interview responses and computes scores, strengths, and feedback."""

    @classmethod
    def evaluate_response(
        cls,
        question_data: Dict[str, Any],
        candidate_response: str
    ) -> Dict[str, Any]:
        """Analyzes candidate answer and scores on a 1-5 scale with detailed rubric breakdown."""
        
        response_text = candidate_response.strip()
        if not response_text or len(response_text) < 10:
            return {
                "score": 1.0,
                "rating": "Unsatisfactory (1/5)",
                "strengths": [],
                "missing_elements": ["Response is too brief or empty to assess."],
                "feedback": "Please provide a substantive answer explaining your reasoning, context, and technical choices.",
                "follow_up_prompt": question_data.get("follow_up_probe", "Could you elaborate in detail on your technical approach?")
            }

        q_type = question_data.get("category", "Technical")
        expected_points = question_data.get("expected_answer_points", [])
        
        # 1. Check keyword and concept overlap
        matched_concepts = []
        missing_concepts = []

        words_in_response = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", response_text.lower()))
        
        for pt in expected_points:
            pt_clean = pt.replace("Situation:", "").replace("Task:", "").replace("Action:", "").replace("Result:", "").strip()
            pt_tokens = set(re.findall(r"\b[a-zA-Z0-9_-]+\b", pt_clean.lower()))
            # Remove generic stopwords
            stopwords = {"the", "a", "an", "and", "or", "of", "to", "in", "for", "with", "on", "is", "by", "from", "as", "at", "it", "that", "this", "mastery"}
            informative_tokens = pt_tokens - stopwords
            
            overlap = informative_tokens.intersection(words_in_response)
            if overlap or len(informative_tokens) == 0:
                matched_concepts.append(pt_clean)
            else:
                missing_concepts.append(pt_clean)

        # 2. Length and structure bonus
        word_count = len(response_text.split())
        length_multiplier = 1.0
        if word_count >= 80:
            length_multiplier = 1.15
        elif word_count >= 30:
            length_multiplier = 1.0
        elif word_count >= 15:
            length_multiplier = 0.9
        else:
            length_multiplier = 0.6

        # 3. Behavioral STAR analysis
        star_elements_found = []
        if q_type == "Behavioral" or "star_framework" in question_data:
            lower_res = response_text.lower()
            if any(k in lower_res for k in ["situation", "when i was", "at my university", "during my project", "in our team", "context"]):
                star_elements_found.append("Situation (Context)")
            if any(k in lower_res for k in ["task", "goal", "needed to", "required", "objective", "threatened", "my role"]):
                star_elements_found.append("Task (Objective)")
            if any(k in lower_res for k in ["i implemented", "i investigated", "i debugged", "i researched", "i decided", "action", "we designed", "step"]):
                star_elements_found.append("Action (Technical Execution)")
            if any(k in lower_res for k in ["result", "outcome", "metric", "improved", "learned", "achieved", "delivered", "%", "faster"]):
                star_elements_found.append("Result (Impact & Takeaway)")

        # 4. Compute numeric score (1.0 to 5.0)
        total_pts = len(expected_points) if expected_points else 3
        concept_coverage_ratio = len(matched_concepts) / total_pts if total_pts > 0 else 0.5

        base_score = 1.0 + (concept_coverage_ratio * 3.5 * length_multiplier)
        
        # Add STAR structure bonus for behavioral questions
        if q_type == "Behavioral":
            star_bonus = (len(star_elements_found) / 4.0) * 1.2
            base_score = 1.0 + (concept_coverage_ratio * 2.8) + star_bonus

        score = min(5.0, max(1.0, round(base_score, 1)))

        # 5. Rating Label
        if score >= 4.5:
            rating = "Exceptional / Expert (5/5)"
            feedback_summary = "Outstanding response! Comprehensive depth, clear trade-offs, and practical execution awareness."
        elif score >= 3.5:
            rating = "Advanced / Strong (4/5)"
            feedback_summary = "Very strong answer with solid technical foundations and practical examples."
        elif score >= 2.5:
            rating = "Competent / Solid (3/5)"
            feedback_summary = "Satisfactory answer covering the basics, but could benefit from deeper architectural reasoning."
        elif score >= 1.8:
            rating = "Developing / Basic (2/5)"
            feedback_summary = "Developing grasp of the topic. Missed several key architectural or execution details."
        else:
            rating = "Unsatisfactory (1/5)"
            feedback_summary = "Insufficient technical depth or unclear structure."

        strengths = []
        if matched_concepts:
            strengths.append(f"Successfully addressed {len(matched_concepts)} key criteria: {', '.join(matched_concepts[:2])}.")
        if word_count >= 80:
            strengths.append("Provided detailed, articulate explanation with concrete context.")
        if star_elements_found:
            strengths.append(f"Structured behavioral narrative with: {', '.join(star_elements_found)}.")

        if not missing_concepts:
            missing_concepts = ["None! Addressed all expected key points."]

        return {
            "score": score,
            "rating": rating,
            "word_count": word_count,
            "concept_coverage_pct": round(concept_coverage_ratio * 100, 1),
            "matched_criteria": matched_concepts,
            "missing_elements": missing_concepts,
            "star_components_identified": star_elements_found,
            "strengths": strengths,
            "feedback": feedback_summary,
            "follow_up_prompt": question_data.get("follow_up_probe", "How would you optimize this under high production load?")
        }
