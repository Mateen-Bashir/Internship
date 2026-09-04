"""
Skill Gap Analyzer Module.
Quantifies skill gaps between an intern profile and industry demands using
Cosine Similarity and TF-IDF weighted skill deficiency matching.
"""

import re
import numpy as np
import pandas as pd
from sklearn.metrics.pairwise import cosine_similarity

try:
    from src.preprocessor import clean_text, parse_skills_list
    from src.nlp_clustering import IndustrySkillClusterModel
except ImportError:
    from preprocessor import clean_text, parse_skills_list
    from nlp_clustering import IndustrySkillClusterModel

class SkillGapAnalyzer:
    def __init__(self, cluster_model: IndustrySkillClusterModel, jobs_df: pd.DataFrame):
        self.cluster_model = cluster_model
        self.jobs_df = jobs_df
        self._build_domain_skill_benchmarks()

    def _build_domain_skill_benchmarks(self):
        """Builds a frequency and importance dictionary of skills for each domain."""
        self.domain_benchmarks = {}
        
        for domain, group in self.jobs_df.groupby("domain"):
            all_skills_in_domain = []
            for s_str in group["required_skills"].dropna():
                all_skills_in_domain.extend(parse_skills_list(s_str))
            
            # Count frequencies
            skill_counts = pd.Series(all_skills_in_domain).value_counts()
            total_jobs = len(group)
            
            # Normalize to frequency percentage (e.g. 0.85 = required in 85% of jobs)
            skill_importance = (skill_counts / total_jobs).to_dict()
            
            # Extract domain centroid in TF-IDF space
            domain_texts = group.apply(
                lambda r: f"{r['job_title']} {r['required_skills']} {r['job_description']}", axis=1
            )
            cleaned_corpus = [clean_text(t) for t in domain_texts]
            domain_tfidf = self.cluster_model.vectorizer.transform(cleaned_corpus)
            domain_centroid = np.asarray(domain_tfidf.mean(axis=0))
            
            self.domain_benchmarks[domain] = {
                "skill_importance": skill_importance,
                "domain_centroid": domain_centroid,
                "top_skills": list(skill_importance.keys())[:12]
            }

    def analyze_intern(self, intern_skills_str: str, target_domain: str = None, target_role: str = None) -> dict:
        """
        Performs a full gap analysis for an intern profile.
        Returns:
            - matched_cluster
            - cosine_similarity_score
            - readiness_percentage
            - matched_skills
            - missing_critical_skills
            - missing_secondary_skills
            - gap_severity
        """
        intern_skills = parse_skills_list(intern_skills_str)
        intern_skills_lower = set(s.lower().strip() for s in intern_skills)
        
        # Transform intern into TF-IDF vector
        intern_vec = self.cluster_model.transform_intern(intern_skills_str)
        
        # Determine domain benchmark to compare against
        if target_domain and target_domain in self.domain_benchmarks:
            active_domain = target_domain
        else:
            # Predict closest cluster
            cluster_id, cluster_info = self.cluster_model.predict_intern_cluster(intern_vec)
            active_domain = cluster_info.get("name", list(self.domain_benchmarks.keys())[0])
            
        benchmark = self.domain_benchmarks.get(active_domain, list(self.domain_benchmarks.values())[0])
        domain_centroid = benchmark["domain_centroid"]
        
        # 1. Cosine Similarity Score (0.0 to 1.0)
        cos_sim = float(cosine_similarity(intern_vec, domain_centroid)[0][0])
        
        # 2. Skill-by-skill evaluation against domain benchmark
        matched_skills = []
        missing_critical_skills = []
        missing_secondary_skills = []
        
        importance_dict = benchmark["skill_importance"]
        
        for skill_name, imp_score in importance_dict.items():
            # Check if skill exists in intern's skill list
            # Match either exact or substring (e.g. 'react' matches 'react.js')
            skill_clean = skill_name.lower().strip()
            is_present = False
            for isk in intern_skills_lower:
                if isk in skill_clean or skill_clean in isk:
                    is_present = True
                    break
            
            skill_record = {
                "skill": skill_name,
                "market_demand_weight": round(imp_score * 100, 1),
                "status": "Acquired" if is_present else "Missing"
            }
            
            if is_present:
                matched_skills.append(skill_record)
            else:
                if imp_score >= 0.40:  # In at least 40% of domain job postings
                    missing_critical_skills.append(skill_record)
                else:
                    missing_secondary_skills.append(skill_record)
        
        # Sort missing by market demand weight descending
        missing_critical_skills = sorted(missing_critical_skills, key=lambda x: x["market_demand_weight"], reverse=True)
        missing_secondary_skills = sorted(missing_secondary_skills, key=lambda x: x["market_demand_weight"], reverse=True)
        
        # 3. Overall Readiness Calculation
        # Weighted combination of vector cosine similarity (40%) and critical skill coverage (60%)
        total_critical_skills = len(matched_skills) + len(missing_critical_skills)
        coverage_ratio = len(matched_skills) / max(1, total_critical_skills)
        
        raw_readiness = (0.40 * cos_sim) + (0.60 * coverage_ratio)
        # Scale and bound to 0-100%
        readiness_score = round(min(100.0, max(10.0, raw_readiness * 100)), 1)
        
        # Gap Severity classification
        if readiness_score >= 75.0:
            gap_severity = "Low (Job Ready / Minor Refinements Needed)"
            badge_color = "success"
        elif readiness_score >= 50.0:
            gap_severity = "Moderate (Core Skills Present, Advanced Gaps)"
            badge_color = "warning"
        else:
            gap_severity = "High (Critical Foundational Gaps)"
            badge_color = "danger"
            
        return {
            "target_domain": active_domain,
            "target_role": target_role or "Tech Professional",
            "cosine_similarity": round(cos_sim, 4),
            "readiness_percentage": readiness_score,
            "gap_severity": gap_severity,
            "badge_color": badge_color,
            "matched_skills": matched_skills,
            "missing_critical_skills": missing_critical_skills,
            "missing_secondary_skills": missing_secondary_skills,
            "total_matched_count": len(matched_skills),
            "total_missing_count": len(missing_critical_skills) + len(missing_secondary_skills)
        }

    def batch_analyze_interns(self, interns_df: pd.DataFrame) -> pd.DataFrame:
        """Analyzes all interns in a dataframe and returns summary metrics."""
        results = []
        for _, row in interns_df.iterrows():
            analysis = self.analyze_intern(
                intern_skills_str=row["current_skills"],
                target_domain=row.get("target_domain"),
                target_role=row.get("target_role")
            )
            results.append({
                "intern_id": row["intern_id"],
                "name": row["name"],
                "target_domain": row["target_domain"],
                "target_role": row["target_role"],
                "current_skills": row["current_skills"],
                "readiness_percentage": analysis["readiness_percentage"],
                "cosine_similarity": analysis["cosine_similarity"],
                "gap_severity": analysis["gap_severity"],
                "matched_count": analysis["total_matched_count"],
                "critical_missing_count": len(analysis["missing_critical_skills"]),
                "critical_missing_skills": ", ".join([s["skill"] for s in analysis["missing_critical_skills"][:4]])
            })
        return pd.DataFrame(results)
