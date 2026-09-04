import json
import re
from typing import Dict, Any, List, Set

class GenerationEvaluator:
    """Evaluates the quality, coverage, and diversity of generated interview kits."""

    @classmethod
    def evaluate_kit(
        cls,
        kit: Dict[str, Any],
        profile: Dict[str, Any],
        job_desc: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Runs quantitative benchmark evaluation on a generated interview kit."""
        
        tech_q = kit.get("technical_questions", [])
        beh_q = kit.get("behavioral_questions", [])
        proj_q = kit.get("project_deep_dive_questions", [])
        all_q = tech_q + beh_q + proj_q

        # 1. Skill Coverage Index
        jd_skills = set([s.lower() for s in job_desc.get("required_skills", []) + job_desc.get("preferred_skills", [])])
        mentioned_skills = set()
        for q in tech_q:
            q_text = (q.get("question", "") + " " + q.get("skill_targeted", "") + " " + q.get("topic", "")).lower()
            for s in jd_skills:
                if s in q_text:
                    mentioned_skills.add(s)
        
        skill_coverage_pct = round((len(mentioned_skills) / len(jd_skills) * 100), 1) if jd_skills else 100.0

        # 2. Difficulty Balance Score
        diff_counts = {"Easy": 0, "Medium": 0, "Hard": 0}
        for q in tech_q:
            diff = q.get("difficulty", "Medium").capitalize()
            if diff in diff_counts:
                diff_counts[diff] += 1
            else:
                diff_counts["Medium"] += 1
        
        has_easy = diff_counts["Easy"] > 0
        has_med = diff_counts["Medium"] > 0
        has_hard = diff_counts["Hard"] > 0
        diff_balance_score = round(((has_easy + has_med + has_hard) / 3.0) * 100, 1)

        # 3. STAR Behavioral Completeness
        star_scores = []
        for b in beh_q:
            star = b.get("star_framework", {})
            has_s = bool(star.get("situation"))
            has_t = bool(star.get("task"))
            has_a = bool(star.get("action"))
            has_r = bool(star.get("result"))
            has_flags = bool(b.get("green_flags")) and bool(b.get("red_flags"))
            star_scores.append((has_s + has_t + has_a + has_r + has_flags) / 5.0)
        
        star_completeness_pct = round((sum(star_scores) / len(star_scores) * 100), 1) if star_scores else 100.0

        # 4. Lexical Uniqueness (Distinct-2 N-Grams)
        all_words = []
        bigrams = set()
        total_bigrams = 0
        for q in all_q:
            words = re.findall(r"\b[a-zA-Z]+\b", q.get("question", "").lower())
            all_words.extend(words)
            for i in range(len(words) - 1):
                bg = (words[i], words[i+1])
                bigrams.add(bg)
                total_bigrams += 1
        
        distinct_2_ratio = round((len(bigrams) / total_bigrams), 3) if total_bigrams > 0 else 1.0

        # 5. Candidate Personalization Grounding
        # Checks if project titles, university, or candidate skills appear in generated questions
        cand_anchor_terms = [p.get("title", "").lower() for p in profile.get("projects", [])]
        cand_anchor_terms.extend([s.lower() for s in profile.get("technical_skills", [])])
        cand_anchor_terms = [t for t in cand_anchor_terms if len(t) > 3]

        anchors_matched = 0
        kit_text = json.dumps(kit).lower()
        for term in cand_anchor_terms:
            if term in kit_text:
                anchors_matched += 1

        personalization_pct = round((anchors_matched / max(1, min(len(cand_anchor_terms), 10))) * 100, 1)
        personalization_pct = min(100.0, personalization_pct)

        # Composite Quality Index (CQI)
        composite_quality_index = round(
            (skill_coverage_pct * 0.25) +
            (diff_balance_score * 0.20) +
            (star_completeness_pct * 0.20) +
            (distinct_2_ratio * 100 * 0.15) +
            (personalization_pct * 0.20),
            1
        )

        return {
            "composite_quality_index": composite_quality_index,
            "skill_coverage_pct": skill_coverage_pct,
            "difficulty_balance_score": diff_balance_score,
            "difficulty_distribution": diff_counts,
            "star_completeness_pct": star_completeness_pct,
            "lexical_distinct_2_ratio": distinct_2_ratio,
            "personalization_pct": personalization_pct,
            "total_questions_generated": len(all_q),
            "benchmark_status": "EXCELLENT" if composite_quality_index >= 85 else "GOOD"
        }
