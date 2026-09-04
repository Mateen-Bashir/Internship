"""
End-to-End Execution & Evaluation Script
Internee.pk - Task 3: Personalized Learning Path Recommendation System

Runs:
1. Data verification / generation
2. SVD Matrix Factorization training & baseline comparison
3. Metric reporting (RMSE, MAE, Precision@K, Recall@K, NDCG@K)
4. Sample learning path recommendations with prerequisite DAG verification
"""

import os
import sys
import pandas as pd

# Ensure root directory is on Python path
sys.path.insert(0, os.path.dirname(__file__))

from src.recommender_pipeline import PersonalizedLearningRecommenderPipeline

def print_separator(title=""):
    print("\n" + "=" * 65)
    if title:
        print(f"  {title.upper()}")
        print("=" * 65)

def format_milestone_output(roadmap):
    print(f"\n[PROFILE]: {roadmap['intern_profile']['name']} ({roadmap['intern_profile']['intern_id']})")
    print(f"[TRACK]  : {roadmap['intern_profile']['primary_track']} | Level: {roadmap['intern_profile']['experience_level']}")
    print(f"[SUMMARY]: {roadmap['total_modules']} Recommended Modules | {roadmap['total_duration_hours']} Total Hours | {roadmap['skills_covered_count']} Skills")
    print("-" * 65)
    
    for milestone_name, modules in roadmap['milestones'].items():
        print(f"\n>>> {milestone_name}")
        for m in modules:
            prereq_str = f" [Prereqs: {', '.join(m['prerequisites'])}]" if m['prerequisites'] else " [No Prereqs]"
            print(f"   [{m['step_order']}] {m['module_id']}: {m['title']}")
            print(f"       Difficulty: {m['difficulty_level']} | Duration: {m['duration_hours']}h | SVD Pred Rating: {m['predicted_rating']}/5.0{prereq_str}")
            print(f"       Skills: {', '.join(m['skills'][:4])}")

def main():
    print_separator("INTERNEE.PK TASK 3: PERSONALIZED LEARNING PATH RECOMMENDER")
    
    # 1. Initialize Recommender Pipeline
    print("[*] Initializing & Training Matrix Factorization Models...")
    pipeline = PersonalizedLearningRecommenderPipeline()
    print("[+] Models trained successfully!")
    
    # 2. Display Model Performance Benchmarks
    print_separator("MODEL PERFORMANCE BENCHMARKS (TEST SPLIT 20%)")
    metrics = pipeline.metrics
    
    benchmark_data = [
        {
            "Model": "SVD Matrix Factorization (Proposed)",
            "RMSE": metrics["SVD (Proposed)"]["RMSE"],
            "MAE": metrics["SVD (Proposed)"]["MAE"],
            "Precision@5": metrics["SVD (Proposed)"]["Precision@5"],
            "Recall@5": metrics["SVD (Proposed)"]["Recall@5"],
            "NDCG@5": metrics["SVD (Proposed)"]["NDCG@5"]
        },
        {
            "Model": "NMF Matrix Factorization (Baseline)",
            "RMSE": metrics["NMF (Baseline)"]["RMSE"],
            "MAE": metrics["NMF (Baseline)"]["MAE"],
            "Precision@5": metrics["NMF (Baseline)"]["Precision@5"],
            "Recall@5": metrics["NMF (Baseline)"]["Recall@5"],
            "NDCG@5": metrics["NMF (Baseline)"]["NDCG@5"]
        }
    ]
    df_metrics = pd.DataFrame(benchmark_data)
    print(df_metrics.to_string(index=False))
    
    # 3. Test Sample 1: Existing Intern in Data Science
    print_separator("SAMPLE 1: EXISTING INTERN (DATA SCIENCE & ANALYTICS)")
    # Find a data science intern
    ds_interns = pipeline.profiles_df[pipeline.profiles_df['primary_track'] == "Data Science & Analytics"]
    ds_id = ds_interns.iloc[0]['intern_id'] if not ds_interns.empty else "INT_0001"
    
    ds_roadmap = pipeline.recommend_for_intern(ds_id, top_n=6)
    format_milestone_output(ds_roadmap)
    
    # 4. Test Sample 2: Existing Intern in Web Development
    print_separator("SAMPLE 2: EXISTING INTERN (FULL-STACK WEB DEV)")
    web_interns = pipeline.profiles_df[pipeline.profiles_df['primary_track'] == "Full-Stack Web Development"]
    web_id = web_interns.iloc[0]['intern_id'] if not web_interns.empty else "INT_0002"
    
    web_roadmap = pipeline.recommend_for_intern(web_id, top_n=6)
    format_milestone_output(web_roadmap)
    
    # 5. Test Sample 3: Cold-Start New Intern (AI & Machine Learning)
    print_separator("SAMPLE 3: COLD-START NEW INTERN (AI & MACHINE LEARNING)")
    cold_roadmap = pipeline.recommend_cold_start(target_track="AI & Machine Learning", skill_level="Beginner", top_n=6)
    format_milestone_output(cold_roadmap)
    
    print_separator("PIPELINE EXECUTION COMPLETE")

if __name__ == "__main__":
    main()
