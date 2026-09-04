"""
Automated Training & Upskilling Recommendation Engine.
Maps identified intern skill deficiencies to targeted online courses,
hands-on portfolio projects, certifications, and multi-week learning roadmaps.
"""

import pandas as pd

class TrainingRecommender:
    def __init__(self, catalog_df: pd.DataFrame):
        self.catalog_df = catalog_df
        self._build_lookup_index()

    def _build_lookup_index(self):
        """Indexes courses by lowercase skill for fast O(1) matching."""
        self.skill_to_courses = {}
        for _, row in self.catalog_df.iterrows():
            skill_key = str(row["skill"]).strip().lower()
            if skill_key not in self.skill_to_courses:
                self.skill_to_courses[skill_key] = []
            self.skill_to_courses[skill_key].append(row.to_dict())

    def get_recommendations_for_skills(self, missing_skills_list: list) -> list:
        """
        Takes a list of missing skill dicts (or strings) and returns recommended
        courses, projects, duration, and platforms.
        """
        recommendations = []
        seen_courses = set()

        for item in missing_skills_list:
            skill_name = item["skill"] if isinstance(item, dict) else str(item)
            skill_clean = skill_name.strip().lower()
            
            # Find matching course in catalog
            matched = False
            for cat_skill, courses in self.skill_to_courses.items():
                if cat_skill in skill_clean or skill_clean in cat_skill:
                    for course in courses:
                        if course["course_name"] not in seen_courses:
                            rec_item = dict(course)
                            rec_item["target_missing_skill"] = skill_name
                            if isinstance(item, dict) and "market_demand_weight" in item:
                                rec_item["market_demand_weight"] = item["market_demand_weight"]
                            recommendations.append(rec_item)
                            seen_courses.add(course["course_name"])
                            matched = True
                    break
                    
            # If no direct match in catalog, generate fallback structured module
            if not matched and skill_clean:
                fallback = {
                    "skill": skill_name,
                    "course_name": f"Comprehensive {skill_name} Practical Mastery",
                    "platform": "Coursera / Udemy",
                    "duration_weeks": 3,
                    "difficulty": "Intermediate",
                    "project_task": f"Build a production-grade module utilizing {skill_name} and integrate it into a portfolio GitHub repository.",
                    "target_missing_skill": skill_name,
                    "market_demand_weight": item.get("market_demand_weight", 50.0) if isinstance(item, dict) else 50.0
                }
                recommendations.append(fallback)

        return recommendations

    def generate_learning_roadmap(self, gap_analysis_result: dict) -> dict:
        """
        Constructs a phased, milestone-based upskilling roadmap for an intern.
        Phases:
          - Phase 1: High-Priority Core Gaps (Weeks 1 to N)
          - Phase 2: Advanced Industry Tools & Frameworks
          - Phase 3: Capstone Portfolio Integration
        """
        critical_missing = gap_analysis_result.get("missing_critical_skills", [])
        secondary_missing = gap_analysis_result.get("missing_secondary_skills", [])
        
        crit_recs = self.get_recommendations_for_skills(critical_missing)
        sec_recs = self.get_recommendations_for_skills(secondary_missing)
        
        all_recs = crit_recs + sec_recs
        total_estimated_weeks = sum(r.get("duration_weeks", 3) for r in all_recs[:6])
        
        # Build phases
        phase1_courses = crit_recs[:3]
        phase2_courses = (crit_recs[3:5] if len(crit_recs) > 3 else []) + sec_recs[:2]
        
        capstone_project = {
            "title": f"End-to-End {gap_analysis_result.get('target_domain', 'Industry')} Production Capstone",
            "description": f"Architect and deploy a complete project for a {gap_analysis_result.get('target_role', 'Tech Professional')} incorporating newly acquired skills: {', '.join([r['target_missing_skill'] for r in all_recs[:4]])}.",
            "deliverables": [
                "Public GitHub repository with automated CI/CD pipeline",
                "Live deployed demo link & architecture diagram",
                "Technical documentation & benchmark testing"
            ]
        }
        
        return {
            "target_domain": gap_analysis_result.get("target_domain"),
            "target_role": gap_analysis_result.get("target_role"),
            "current_readiness": gap_analysis_result.get("readiness_percentage"),
            "total_estimated_weeks": total_estimated_weeks,
            "phase_1_core_foundations": {
                "phase_title": "Phase 1: High-Impact Core Skill Acquisition",
                "duration": f"{sum(r.get('duration_weeks', 3) for r in phase1_courses)} Weeks",
                "recommendations": phase1_courses
            },
            "phase_2_specialization": {
                "phase_title": "Phase 2: Advanced Tooling & Framework Mastery",
                "duration": f"{sum(r.get('duration_weeks', 3) for r in phase2_courses)} Weeks",
                "recommendations": phase2_courses
            },
            "phase_3_capstone": {
                "phase_title": "Phase 3: Portfolio Capstone Project",
                "duration": "2 Weeks",
                "project_details": capstone_project
            },
            "all_recommendations": all_recs
        }
