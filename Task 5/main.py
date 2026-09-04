"""
Main Pipeline Execution Script:
Intern Skill Gap Analysis & Industry Demand Alignment.
Runs the end-to-end NLP & K-Means workflow, analyzes intern cohorts,
generates training recommendations, and exports visual figures and summary reports.
"""

import os
import json
import pandas as pd
import numpy as np

from src.data_generator import generate_all_datasets
from src.nlp_clustering import IndustrySkillClusterModel
from src.skill_gap_analyzer import SkillGapAnalyzer
from src.recommender import TrainingRecommender
from src.visualizer import generate_all_visualizations

def run_pipeline():
    print("=" * 70)
    print("      INTERN SKILL GAP ANALYSIS & INDUSTRY DEMAND ALIGNMENT      ")
    print("                   NLP (TF-IDF) + K-MEANS ENGINE                  ")
    print("=" * 70)

    # 1. Check/Load Datasets
    if not os.path.exists("data/job_postings.csv") or not os.path.exists("data/intern_skills.csv"):
        print("\n[Step 1] Datasets missing. Generating realistic datasets...")
        jobs_df, interns_df, catalog_df = generate_all_datasets()
    else:
        print("\n[Step 1] Loading existing datasets from data/...")
        jobs_df = pd.read_csv("data/job_postings.csv")
        interns_df = pd.read_csv("data/intern_skills.csv")
        catalog_df = pd.read_csv("data/training_catalog.csv")
        print(f"Loaded {len(jobs_df)} Job Postings, {len(interns_df)} Intern Profiles, {len(catalog_df)} Catalog Modules.")

    # 2. Train NLP TF-IDF & K-Means Clustering Model
    print("\n[Step 2] Vectorizing Job Postings with TF-IDF & Fitting K-Means (k=6)...")
    cluster_model = IndustrySkillClusterModel(n_clusters=6, max_features=600)
    cluster_model.fit(jobs_df)
    
    print(f"-> Model Convergence Achieved!")
    print(f"-> Average Silhouette Score: {cluster_model.silhouette_avg:.4f}")
    
    print("\nExtracted Industry Demand Clusters:")
    for cid, info in cluster_model.cluster_labels_map.items():
        print(f"  * Cluster {cid}: {info['name']} ({info['total_jobs']} postings) | Top Skills: {', '.join(info['top_keywords'][:5])}")

    # 3. Initialize Skill Gap Analyzer
    print("\n[Step 3] Initializing Skill Gap & Benchmark Engine...")
    gap_analyzer = SkillGapAnalyzer(cluster_model, jobs_df)
    
    # 4. Batch Analyze Intern Profiles
    print("\n[Step 4] Performing Skill Gap Analysis on 160 Intern Profiles...")
    analyzed_interns_df = gap_analyzer.batch_analyze_interns(interns_df)
    
    avg_readiness = float(analyzed_interns_df["readiness_percentage"].mean())
    avg_similarity = float(analyzed_interns_df["cosine_similarity"].mean())
    print(f"-> Cohort Average Readiness Score: {avg_readiness:.1f}%")
    print(f"-> Cohort Average Vector Cosine Similarity: {avg_similarity:.4f}")

    # 5. Initialize Recommendation Engine & Generate Sample Roadmap
    print("\n[Step 5] Initializing Training & Upskilling Recommender...")
    recommender = TrainingRecommender(catalog_df)
    
    sample_intern_id = analyzed_interns_df.iloc[0]["intern_id"]
    sample_intern_row = interns_df[interns_df["intern_id"] == sample_intern_id].iloc[0]
    sample_analysis = gap_analyzer.analyze_intern(
        intern_skills_str=sample_intern_row["current_skills"],
        target_domain=sample_intern_row["target_domain"],
        target_role=sample_intern_row["target_role"]
    )
    sample_roadmap = recommender.generate_learning_roadmap(sample_analysis)
    
    print(f"\nSample Intern Case Study [{sample_intern_row['name']} - {sample_intern_row['target_role']}]:")
    print(f"  - Target Domain: {sample_analysis['target_domain']}")
    print(f"  - Current Readiness: {sample_analysis['readiness_percentage']}% ({sample_analysis['gap_severity']})")
    print(f"  - Matched Skills ({len(sample_analysis['matched_skills'])}): {', '.join([s['skill'] for s in sample_analysis['matched_skills']])}")
    print(f"  - Critical Missing Skills ({len(sample_analysis['missing_critical_skills'])}): {', '.join([s['skill'] for s in sample_analysis['missing_critical_skills'][:4]])}")
    print(f"  - Recommended Roadmap Duration: {sample_roadmap['total_estimated_weeks']} Weeks")

    # 6. Generate Figures and Visualizations
    print("\n[Step 6] Generating High-Resolution Analytical Charts...")
    generate_all_visualizations(cluster_model, jobs_df, interns_df, analyzed_interns_df)

    # 7. Export Outputs & Summary JSON
    print("\n[Step 7] Exporting Reports & Model Artifacts...")
    cluster_model.save_model("reports/cluster_model.joblib")
    
    analyzed_interns_df.to_csv("reports/analyzed_interns_summary.csv", index=False)
    
    summary_report = {
        "dataset_statistics": {
            "total_job_postings": int(len(jobs_df)),
            "total_intern_profiles": int(len(interns_df)),
            "total_training_courses": int(len(catalog_df)),
            "industry_domains": list(cluster_model.cluster_labels_map.values())
        },
        "model_evaluation": {
            "algorithm": "TF-IDF + K-Means Clustering",
            "k_clusters": 6,
            "average_silhouette_score": round(float(cluster_model.silhouette_avg), 4),
            "max_features": 600,
            "sublinear_tf": True
        },
        "cohort_skill_gap_metrics": {
            "average_readiness_score": round(avg_readiness, 2),
            "average_cosine_similarity": round(avg_similarity, 4),
            "severity_distribution": analyzed_interns_df["gap_severity"].apply(lambda s: s.split("(")[0].strip()).value_counts().to_dict()
        }
    }
    
    with open("reports/analysis_summary.json", "w") as f:
        json.dump(summary_report, f, indent=4)
        
    print(f"Summary JSON saved to reports/analysis_summary.json")
    print(f"Detailed CSV saved to reports/analyzed_interns_summary.csv")
    print("\n" + "=" * 70)
    print("             PIPELINE COMPLETED SUCCESSFULLY!              ")
    print("=" * 70)

if __name__ == "__main__":
    run_pipeline()
