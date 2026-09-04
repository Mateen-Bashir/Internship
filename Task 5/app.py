"""
Flask Application for Intern Skill Gap Analysis & Industry Demand Alignment.
Provides an interactive dashboard, intern cohort explorer, and real-time custom profile analyzer.
"""

import os
import json
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify

from src.nlp_clustering import IndustrySkillClusterModel
from src.skill_gap_analyzer import SkillGapAnalyzer
from src.recommender import TrainingRecommender

app = Flask(__name__)

# Global instances
JOBS_DF = None
INTERNS_DF = None
CATALOG_DF = None
CLUSTER_MODEL = None
GAP_ANALYZER = None
RECOMMENDER = None
ANALYZED_INTERNS_DF = None
SUMMARY_METRICS = None

def init_app_state():
    global JOBS_DF, INTERNS_DF, CATALOG_DF, CLUSTER_MODEL, GAP_ANALYZER, RECOMMENDER, ANALYZED_INTERNS_DF, SUMMARY_METRICS
    
    # Load datasets
    JOBS_DF = pd.read_csv("data/job_postings.csv")
    INTERNS_DF = pd.read_csv("data/intern_skills.csv")
    CATALOG_DF = pd.read_csv("data/training_catalog.csv")
    
    # Load model
    model_path = "reports/cluster_model.joblib"
    if os.path.exists(model_path):
        CLUSTER_MODEL = IndustrySkillClusterModel.load_model(model_path)
    else:
        CLUSTER_MODEL = IndustrySkillClusterModel(n_clusters=6)
        CLUSTER_MODEL.fit(JOBS_DF)
        CLUSTER_MODEL.save_model(model_path)
        
    GAP_ANALYZER = SkillGapAnalyzer(CLUSTER_MODEL, JOBS_DF)
    RECOMMENDER = TrainingRecommender(CATALOG_DF)
    
    if os.path.exists("reports/analyzed_interns_summary.csv"):
        ANALYZED_INTERNS_DF = pd.read_csv("reports/analyzed_interns_summary.csv")
    else:
        ANALYZED_INTERNS_DF = GAP_ANALYZER.batch_analyze_interns(INTERNS_DF)
        ANALYZED_INTERNS_DF.to_csv("reports/analyzed_interns_summary.csv", index=False)
        
    if os.path.exists("reports/analysis_summary.json"):
        with open("reports/analysis_summary.json", "r") as f:
            SUMMARY_METRICS = json.load(f)
    else:
        SUMMARY_METRICS = {
            "dataset_statistics": {
                "total_job_postings": len(JOBS_DF),
                "total_intern_profiles": len(INTERNS_DF)
            }
        }

init_app_state()

@app.route("/")
def index():
    domains = list(GAP_ANALYZER.domain_benchmarks.keys())
    return render_template(
        "index.html",
        domains=domains,
        summary=SUMMARY_METRICS,
        clusters=CLUSTER_MODEL.cluster_labels_map
    )

@app.route("/api/interns", methods=["GET"])
def get_interns():
    """Returns the list of analyzed interns with filter options."""
    domain_filter = request.args.get("domain", "")
    severity_filter = request.args.get("severity", "")
    search_query = request.args.get("q", "").lower()
    
    df = ANALYZED_INTERNS_DF.copy()
    
    if domain_filter and domain_filter != "All":
        df = df[df["target_domain"] == domain_filter]
        
    if severity_filter and severity_filter != "All":
        df = df[df["gap_severity"].str.startswith(severity_filter)]
        
    if search_query:
        df = df[
            df["name"].str.lower().str.contains(search_query) |
            df["target_role"].str.lower().str.contains(search_query) |
            df["current_skills"].str.lower().str.contains(search_query)
        ]
        
    records = df.to_dict(orient="records")
    return jsonify({"success": True, "count": len(records), "interns": records})

@app.route("/api/intern/<intern_id>", methods=["GET"])
def get_intern_details(intern_id):
    """Returns deep-dive gap analysis & recommended roadmap for a specific intern."""
    intern_row = INTERNS_DF[INTERNS_DF["intern_id"] == intern_id]
    if intern_row.empty:
        return jsonify({"success": False, "error": "Intern not found"}), 404
        
    row = intern_row.iloc[0]
    analysis = GAP_ANALYZER.analyze_intern(
        intern_skills_str=row["current_skills"],
        target_domain=row["target_domain"],
        target_role=row["target_role"]
    )
    roadmap = RECOMMENDER.generate_learning_roadmap(analysis)
    
    return jsonify({
        "success": True,
        "profile": {
            "intern_id": row["intern_id"],
            "name": row["name"],
            "education": row["education"],
            "gpa": row["gpa"],
            "target_domain": row["target_domain"],
            "target_role": row["target_role"],
            "current_skills": row["current_skills"],
            "profile_summary": row["profile_summary"]
        },
        "analysis": analysis,
        "roadmap": roadmap
    })

@app.route("/api/analyze-custom", methods=["POST"])
def analyze_custom_profile():
    """Analyzes a custom input resume text / skills list in real time."""
    data = request.get_json() or {}
    skills_text = data.get("skills_text", "").strip()
    target_domain = data.get("target_domain", "").strip()
    target_role = data.get("target_role", "Tech Professional").strip()
    
    if not skills_text:
        return jsonify({"success": False, "error": "Skills text is required."}), 400
        
    analysis = GAP_ANALYZER.analyze_intern(
        intern_skills_str=skills_text,
        target_domain=target_domain if target_domain != "Auto-Detect" else None,
        target_role=target_role
    )
    roadmap = RECOMMENDER.generate_learning_roadmap(analysis)
    
    return jsonify({
        "success": True,
        "analysis": analysis,
        "roadmap": roadmap
    })

@app.route("/api/cluster-data", methods=["GET"])
def get_cluster_data():
    """Returns PCA coordinates and cluster details for frontend interactive charts."""
    sample_size = min(300, len(JOBS_DF))
    sample_indices = np.random.RandomState(42).choice(len(JOBS_DF), sample_size, replace=False)
    
    pca_subset = CLUSTER_MODEL.pca_coords[sample_indices]
    labels_subset = CLUSTER_MODEL.cluster_assignments[sample_indices]
    
    points = []
    for idx, orig_i in enumerate(sample_indices):
        points.append({
            "x": round(float(pca_subset[idx, 0]), 4),
            "y": round(float(pca_subset[idx, 1]), 4),
            "cluster": int(labels_subset[idx]),
            "title": JOBS_DF.iloc[orig_i]["job_title"],
            "domain": JOBS_DF.iloc[orig_i]["domain"],
            "company": JOBS_DF.iloc[orig_i]["company"]
        })
        
    centroids_pca = CLUSTER_MODEL.pca.transform(CLUSTER_MODEL.kmeans.cluster_centers_)
    centroids = []
    for c_id in range(CLUSTER_MODEL.n_clusters):
        centroids.append({
            "cluster": c_id,
            "name": CLUSTER_MODEL.cluster_labels_map.get(c_id, {}).get("name", f"Cluster {c_id}"),
            "x": round(float(centroids_pca[c_id, 0]), 4),
            "y": round(float(centroids_pca[c_id, 1]), 4),
            "top_terms": CLUSTER_MODEL.cluster_top_terms.get(c_id, [])[:5]
        })
        
    return jsonify({
        "success": True,
        "points": points,
        "centroids": centroids
    })

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
