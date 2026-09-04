"""
Visualization Generator for Intern Skill Gap Analysis & Industry Demands.
Saves high-resolution plots for reports, dashboards, and internship submission.
"""

import os
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for generating figures
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

# Set global modern styling
plt.style.use("seaborn-v0_8-whitegrid" if "seaborn-v0_8-whitegrid" in plt.style.available else "default")
plt.rcParams["font.family"] = "sans-serif"
plt.rcParams["font.size"] = 10
plt.rcParams["axes.titlesize"] = 12
plt.rcParams["axes.titleweight"] = "bold"
plt.rcParams["axes.labelsize"] = 11

COLORS = ["#4361ee", "#3a0ca3", "#7209b7", "#f72585", "#4cc9f0", "#10b981", "#f59e0b"]

def plot_clusters_2d(cluster_model, output_path="reports/figures/kmeans_clusters_2d.png"):
    """Plots 2D PCA projection of job postings clustered by K-Means."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    pca_coords = cluster_model.pca_coords
    labels = cluster_model.cluster_assignments
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    unique_clusters = np.unique(labels)
    for idx, cluster_id in enumerate(unique_clusters):
        mask = labels == cluster_id
        cluster_info = cluster_model.cluster_labels_map.get(cluster_id, {})
        domain_name = cluster_info.get("name", f"Cluster {cluster_id}")
        
        ax.scatter(
            pca_coords[mask, 0],
            pca_coords[mask, 1],
            c=COLORS[idx % len(COLORS)],
            label=f"{domain_name} ({mask.sum()} jobs)",
            alpha=0.65,
            edgecolors="none",
            s=45
        )
        
    # Project and plot centroids
    centroids_pca = cluster_model.pca.transform(cluster_model.kmeans.cluster_centers_)
    ax.scatter(
        centroids_pca[:, 0],
        centroids_pca[:, 1],
        c="#000000",
        marker="X",
        s=140,
        linewidths=1.5,
        edgecolors="#ffffff",
        label="Cluster Centroids",
        zorder=10
    )
    
    ax.set_title("K-Means Clustering of Tech Industry Job Demands (PCA 2D Projection)", pad=15)
    ax.set_xlabel("Principal Component 1 (Major Skill Variance)")
    ax.set_ylabel("Principal Component 2 (Domain Specificity)")
    ax.legend(loc="upper right", frameon=True, framealpha=0.9, fontsize=9)
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved cluster plot to {output_path}")

def plot_skill_gap_comparison(jobs_df, interns_df, target_domain="AI & Machine Learning", output_path="reports/figures/domain_skill_gap.png"):
    """Compares industry demand frequency vs intern possession for top skills in a domain."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    # 1. Calculate industry demand %
    domain_jobs = jobs_df[jobs_df["domain"] == target_domain]
    job_skills_list = []
    for s in domain_jobs["required_skills"].dropna():
        job_skills_list.extend([x.strip() for x in s.split(",") if x.strip()])
    job_skill_counts = pd.Series(job_skills_list).value_counts().head(8)
    job_demand_pct = (job_skill_counts / len(domain_jobs)) * 100
    
    # 2. Calculate intern possession % for those same skills
    domain_interns = interns_df[interns_df["target_domain"] == target_domain]
    intern_skills_list = []
    for s in domain_interns["current_skills"].dropna():
        intern_skills_list.extend([x.strip() for x in s.split(",") if x.strip()])
    intern_skill_counts = pd.Series(intern_skills_list).value_counts()
    
    intern_possession_pct = []
    for skill in job_demand_pct.index:
        count = intern_skill_counts.get(skill, 0)
        pct = (count / max(1, len(domain_interns))) * 100
        intern_possession_pct.append(pct)
        
    skills = job_demand_pct.index.tolist()
    demand_vals = job_demand_pct.values
    supply_vals = np.array(intern_possession_pct)
    
    x = np.arange(len(skills))
    width = 0.38
    
    fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
    
    rects1 = ax.bar(x - width/2, demand_vals, width, label="Industry Market Demand (%)", color="#3b82f6", edgecolor="none", alpha=0.9)
    rects2 = ax.bar(x + width/2, supply_vals, width, label="Intern Talent Supply (%)", color="#10b981", edgecolor="none", alpha=0.9)
    
    # Highlight gaps with subtle red shading if supply < demand
    for i in range(len(skills)):
        gap = demand_vals[i] - supply_vals[i]
        if gap > 20:
            ax.annotate(f"Gap: -{gap:.0f}%", 
                        xy=(x[i] + width/2, supply_vals[i] + 2),
                        xytext=(0, 5), textcoords="offset points",
                        ha='center', va='bottom', fontsize=8, fontweight='bold', color='#ef4444')
    
    ax.set_title(f"Skill Gap Benchmark Analysis: {target_domain}", pad=15)
    ax.set_ylabel("Percentage (%)")
    ax.set_xticks(x)
    ax.set_xticklabels(skills, rotation=25, ha="right", fontweight="medium")
    ax.set_ylim(0, 115)
    ax.legend(loc="upper right", frameon=True, framealpha=0.9)
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved skill gap comparison plot to {output_path}")

def plot_intern_readiness_distribution(analyzed_interns_df, output_path="reports/figures/intern_readiness_dist.png"):
    """Plots the readiness score distribution across all interns."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13, 5), dpi=300)
    
    # 1. Histogram / Density of Readiness Scores
    scores = analyzed_interns_df["readiness_percentage"]
    ax1.hist(scores, bins=15, color="#6366f1", edgecolor="#ffffff", alpha=0.85, density=False)
    ax1.axvline(scores.mean(), color="#ef4444", linestyle="--", linewidth=2, label=f"Mean: {scores.mean():.1f}%")
    ax1.axvline(scores.median(), color="#10b981", linestyle=":", linewidth=2, label=f"Median: {scores.median():.1f}%")
    
    ax1.set_title("Intern Job-Readiness Score Distribution")
    ax1.set_xlabel("Readiness Percentage (%)")
    ax1.set_ylabel("Number of Interns")
    ax1.legend(loc="upper right", frameon=True)
    
    # 2. Donut Chart of Gap Severity
    severity_counts = analyzed_interns_df["gap_severity"].apply(lambda s: s.split("(")[0].strip()).value_counts()
    colors_dict = {"Low": "#10b981", "Moderate": "#f59e0b", "High": "#ef4444"}
    donut_colors = [colors_dict.get(k, "#6b7280") for k in severity_counts.index]
    
    wedges, texts, autotexts = ax2.pie(
        severity_counts.values,
        labels=severity_counts.index,
        autopct="%1.1f%%",
        startangle=140,
        colors=donut_colors,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2),
        textprops=dict(fontweight="bold")
    )
    ax2.set_title("Intern Skill Gap Severity Breakdown")
    
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"Saved readiness distribution plot to {output_path}")

def generate_all_visualizations(cluster_model, jobs_df, interns_df, analyzed_interns_df):
    plot_clusters_2d(cluster_model)
    plot_skill_gap_comparison(jobs_df, interns_df, target_domain="AI & Machine Learning", output_path="reports/figures/skill_gap_ai.png")
    plot_skill_gap_comparison(jobs_df, interns_df, target_domain="Data Science & Analytics", output_path="reports/figures/skill_gap_datascience.png")
    plot_skill_gap_comparison(jobs_df, interns_df, target_domain="Full Stack & Web Development", output_path="reports/figures/skill_gap_fullstack.png")
    plot_intern_readiness_distribution(analyzed_interns_df)
