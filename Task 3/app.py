"""
Personalized Learning Path Recommendation System - Interactive Web Dashboard
Internee.pk - Task 3

Features:
1. Personalized Intern Roadmap Visualizer (Milestones, SVD Predicted Scores, Prerequisite Tags)
2. Cold-Start New Intern Path Builder
3. Machine Learning Analytics Lab (SVD vs NMF Benchmarks, Latent Factor 2D Projection, Matrix Sparsity)
4. Interactive Course & Prerequisite Dependency Catalog
"""

import os
import sys
import numpy as np
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt
from sklearn.decomposition import PCA

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from src.recommender_pipeline import PersonalizedLearningRecommenderPipeline

# Page configuration
st.set_page_config(
    page_title="Internee.pk - AI Learning Path Recommender",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom High-End CSS Design System
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@300;400;500;600;700;800&display=swap');

    html, body, [class*="css"] {
        font-family: 'Plus Jakarta Sans', sans-serif;
    }

    /* Main Container Styling */
    .main {
        background: linear-gradient(135deg, #0f172a 0%, #1e1b4b 50%, #0f172a 100%);
        color: #f8fafc;
    }

    /* Hero Banner */
    .hero-container {
        background: linear-gradient(135deg, rgba(30, 41, 59, 0.7) 0%, rgba(99, 102, 241, 0.15) 100%);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 28px;
        margin-bottom: 24px;
        backdrop-filter: blur(12px);
        box-shadow: 0 8px 32px 0 rgba(0, 0, 0, 0.37);
    }
    
    .hero-title {
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(90deg, #38bdf8 0%, #818cf8 50%, #c084fc 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 6px;
    }
    
    .hero-subtitle {
        color: #94a3b8;
        font-size: 15px;
        font-weight: 400;
    }

    /* Metric Cards */
    .kpi-card {
        background: rgba(30, 41, 59, 0.6);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 18px;
        text-align: center;
        backdrop-filter: blur(8px);
        transition: transform 0.2s ease, border-color 0.2s ease;
    }
    .kpi-card:hover {
        transform: translateY(-3px);
        border-color: rgba(99, 102, 241, 0.4);
    }
    .kpi-value {
        font-size: 24px;
        font-weight: 700;
        color: #38bdf8;
    }
    .kpi-label {
        font-size: 12px;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-top: 4px;
    }

    /* Milestone Header */
    .milestone-header {
        font-size: 18px;
        font-weight: 700;
        color: #e2e8f0;
        padding: 10px 16px;
        background: rgba(99, 102, 241, 0.12);
        border-left: 4px solid #6366f1;
        border-radius: 0 8px 8px 0;
        margin-top: 24px;
        margin-bottom: 14px;
    }

    /* Course Module Card */
    .module-card {
        background: rgba(15, 23, 42, 0.75);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 14px;
        padding: 20px;
        margin-bottom: 14px;
        transition: all 0.25s ease;
    }
    .module-card:hover {
        border-color: rgba(56, 189, 248, 0.5);
        box-shadow: 0 10px 25px -5px rgba(56, 189, 248, 0.1);
        transform: translateY(-2px);
    }
    
    .module-title {
        font-size: 17px;
        font-weight: 700;
        color: #f1f5f9;
        margin-bottom: 6px;
    }
    
    .badge-beginner {
        background: rgba(16, 185, 129, 0.15);
        color: #34d399;
        border: 1px solid rgba(16, 185, 129, 0.3);
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-intermediate {
        background: rgba(245, 158, 11, 0.15);
        color: #fbbf24;
        border: 1px solid rgba(245, 158, 11, 0.3);
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-advanced {
        background: rgba(239, 68, 68, 0.15);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.3);
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .badge-svd {
        background: rgba(99, 102, 241, 0.15);
        color: #a5b4fc;
        border: 1px solid rgba(99, 102, 241, 0.3);
        padding: 3px 9px;
        border-radius: 12px;
        font-size: 11px;
        font-weight: 600;
    }
    .skill-pill {
        display: inline-block;
        background: rgba(51, 65, 85, 0.6);
        color: #cbd5e1;
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        margin-right: 4px;
        margin-top: 4px;
    }
    .prereq-pill {
        display: inline-block;
        background: rgba(225, 29, 72, 0.15);
        color: #fda4af;
        border: 1px solid rgba(225, 29, 72, 0.3);
        padding: 2px 8px;
        border-radius: 6px;
        font-size: 11px;
        margin-right: 4px;
        margin-top: 4px;
    }
</style>
""", unsafe_allow_html=True)

# Cache Recommender Pipeline in Streamlit Memory
@st.cache_resource
def load_pipeline():
    return PersonalizedLearningRecommenderPipeline()

pipeline = load_pipeline()

# ----------------------------------------------------------------------
# SIDEBAR NAVIGATION
# ----------------------------------------------------------------------
with st.sidebar:
    st.image("https://img.icons8.com/isometric/100/graduation-cap.png", width=64)
    st.markdown("### **Internee.pk Recommender**")
    st.caption("Task 3: Collaborative Filtering Learning Paths")
    
    app_mode = st.radio(
        "Navigation",
        [
            "🧑‍🎓 Intern Personalized Roadmap",
            "⚡ Cold-Start Path Builder",
            "📊 ML Model Performance & Analytics",
            "📚 Course & Prerequisite Catalog"
        ]
    )
    
    st.markdown("---")
    st.markdown("#### **Recommender Engine Specs**")
    st.markdown("""
    - **Algorithm**: SVD Matrix Factorization
    - **Latent Factors**: $k = 12$
    - **Sparsity**: ~51.2%
    - **Sequencing**: Prerequisite DAG (NetworkX)
    """)
    st.caption("Developed for Internee.pk Internship Program")

# ----------------------------------------------------------------------
# VIEW 1: PERSONALIZED INTERN ROADMAP
# ----------------------------------------------------------------------
if app_mode == "🧑‍🎓 Intern Personalized Roadmap":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Personalized Learning Path Recommender</div>
        <div class="hero-subtitle">Generates pedagogical, prerequisite-verified course sequences tailored to each intern's affinity and learning history.</div>
    </div>
    """, unsafe_allow_html=True)
    
    # Intern Selector
    profiles_df = pipeline.profiles_df
    intern_list = [f"{row['intern_id']} - {row['name']} ({row['primary_track']})" for _, row in profiles_df.iterrows()]
    
    col_sel1, col_sel2 = st.columns([3, 1])
    with col_sel1:
        selected_intern_str = st.selectbox("Select Intern Profile:", intern_list, index=0)
        selected_id = selected_intern_str.split(" - ")[0]
    with col_sel2:
        top_n_modules = st.slider("Target Modules:", min_value=4, max_value=10, value=6)
        
    # Generate Roadmap
    roadmap = pipeline.recommend_for_intern(selected_id, top_n=top_n_modules)
    profile = roadmap['intern_profile']
    
    # Intern Profile Info Bar
    st.markdown(f"""
    <div style="background: rgba(30, 41, 59, 0.4); padding: 14px 20px; border-radius: 12px; margin-bottom: 20px; border: 1px solid rgba(255,255,255,0.05);">
        <span style="font-size: 16px; font-weight: 700; color: #f8fafc;">🧑‍💻 {profile['name']}</span> &nbsp;|&nbsp;
        <span style="color: #38bdf8;">Track: <b>{profile['primary_track']}</b></span> &nbsp;|&nbsp;
        <span style="color: #a78bfa;">Skill Level: <b>{profile['experience_level']}</b></span> &nbsp;|&nbsp;
        <span style="color: #94a3b8;">Pace: <b>{profile['learning_pace']}</b></span> &nbsp;|&nbsp;
        <span style="color: #34d399;">Completed Modules: <b>{roadmap['completed_modules_count']}</b></span>
    </div>
    """, unsafe_allow_html=True)
    
    # KPI Metrics
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{roadmap['total_modules']}</div><div class="kpi-label">Recommended Modules</div></div>""", unsafe_allow_html=True)
    with kpi2:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{roadmap['total_duration_hours']} hrs</div><div class="kpi-label">Estimated Time</div></div>""", unsafe_allow_html=True)
    with kpi3:
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{roadmap['skills_covered_count']}</div><div class="kpi-label">New Skills Gained</div></div>""", unsafe_allow_html=True)
    with kpi4:
        avg_pred = np.mean([m['predicted_rating'] for m in roadmap['sequential_modules']]) if roadmap['sequential_modules'] else 4.0
        st.markdown(f"""<div class="kpi-card"><div class="kpi-value">{avg_pred:.2f} / 5.0</div><div class="kpi-label">Avg SVD Affinity</div></div>""", unsafe_allow_html=True)
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Display Milestones
    for milestone_name, modules in roadmap['milestones'].items():
        st.markdown(f"""<div class="milestone-header">{milestone_name} ({len(modules)} Modules)</div>""", unsafe_allow_html=True)
        
        for m in modules:
            diff_class = f"badge-{m['difficulty_level'].lower()}"
            skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in m['skills']])
            
            prereqs_html = ""
            if m['prerequisites']:
                prereqs_html = "<div style='margin-top: 8px;'><span style='font-size: 12px; color: #f43f5e;'>Prerequisites Required: </span>" + "".join([f'<span class="prereq-pill">⛓️ {p}</span>' for p in m['prerequisites']]) + "</div>"
            else:
                prereqs_html = "<div style='margin-top: 8px;'><span style='font-size: 12px; color: #10b981;'>✓ No Prerequisites (Foundational)</span></div>"
                
            st.markdown(f"""
            <div class="module-card">
                <div style="display: flex; justify-content: space-between; align-items: flex-start;">
                    <div>
                        <span style="color: #64748b; font-weight: 700; font-size: 14px;">STEP {m['step_order']} &nbsp;•&nbsp; {m['module_id']}</span>
                        <div class="module-title">{m['title']}</div>
                    </div>
                    <div>
                        <span class="{diff_class}">{m['difficulty_level']}</span> &nbsp;
                        <span class="badge-svd">★ SVD Pred: {m['predicted_rating']}</span>
                    </div>
                </div>
                <p style="color: #94a3b8; font-size: 13px; margin: 8px 0;">{m['description']}</p>
                <div style="margin-top: 6px;">
                    <span style="font-size: 12px; color: #64748b;">Skills: </span> {skills_html}
                </div>
                {prereqs_html}
            </div>
            """, unsafe_allow_html=True)
            
    # Completed Modules Accordion
    with st.expander(f"📜 View Intern Completed & Enrolled History ({len(roadmap['history'])} courses)"):
        if roadmap['history']:
            hist_df = pd.DataFrame(roadmap['history'])[['module_id', 'title', 'domain', 'difficulty_level', 'rating', 'completion_percentage', 'status']]
            st.dataframe(hist_df, use_container_width=True)
        else:
            st.info("No prior interaction history found for this intern.")

# ----------------------------------------------------------------------
# VIEW 2: COLD-START PATHWAY BUILDER
# ----------------------------------------------------------------------
elif app_mode == "⚡ Cold-Start Path Builder":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Cold-Start Learning Path Builder</div>
        <div class="hero-subtitle">For new interns joining without past rating history: Bootstraps optimal paths using Track Knowledge Graphs and Difficulty Progression.</div>
    </div>
    """, unsafe_allow_html=True)
    
    col_c1, col_c2, col_c3 = st.columns(3)
    with col_c1:
        target_track = st.selectbox(
            "Select Desired Career Track:",
            [
                "AI & Machine Learning",
                "Data Science & Analytics",
                "Full-Stack Web Development",
                "Mobile Application Development",
                "Cloud Computing & DevOps",
                "Cybersecurity & Ethical Hacking"
            ]
        )
    with col_c2:
        skill_level = st.selectbox("Current Skill Baseline:", ["Beginner", "Intermediate", "Advanced"])
    with col_c3:
        num_mods = st.slider("Target Modules in Roadmap:", min_value=4, max_value=8, value=6)
        
    cold_roadmap = pipeline.recommend_cold_start(target_track=target_track, skill_level=skill_level, top_n=num_mods)
    
    st.success(f"Generated a {cold_roadmap['total_modules']}-module customized roadmap for **{target_track}** ({cold_roadmap['total_duration_hours']} hours total).")
    
    for milestone_name, modules in cold_roadmap['milestones'].items():
        st.markdown(f"""<div class="milestone-header">{milestone_name} ({len(modules)} Modules)</div>""", unsafe_allow_html=True)
        for m in modules:
            diff_class = f"badge-{m['difficulty_level'].lower()}"
            skills_html = "".join([f'<span class="skill-pill">{s}</span>' for s in m['skills']])
            prereqs_html = "".join([f'<span class="prereq-pill">⛓️ {p}</span>' for p in m['prerequisites']]) if m['prerequisites'] else "<span style='font-size: 12px; color: #10b981;'>✓ Direct Entry</span>"
            
            st.markdown(f"""
            <div class="module-card">
                <div style="display: flex; justify-content: space-between;">
                    <div>
                        <span style="color: #64748b; font-weight: 700; font-size: 14px;">STEP {m['step_order']} &nbsp;•&nbsp; {m['module_id']}</span>
                        <div class="module-title">{m['title']}</div>
                    </div>
                    <div>
                        <span class="{diff_class}">{m['difficulty_level']}</span> &nbsp;
                        <span style="color: #38bdf8; font-size: 12px;">⏱️ {m['duration_hours']} hrs</span>
                    </div>
                </div>
                <p style="color: #94a3b8; font-size: 13px; margin: 8px 0;">{m['description']}</p>
                <div style="margin-top: 6px;">
                    <span style="font-size: 12px; color: #64748b;">Skills: </span> {skills_html}
                </div>
                <div style="margin-top: 8px;">
                    <span style="font-size: 12px; color: #94a3b8;">Prerequisites: </span> {prereqs_html}
                </div>
            </div>
            """, unsafe_allow_html=True)

# ----------------------------------------------------------------------
# VIEW 3: ML PERFORMANCE & ANALYTICS LAB
# ----------------------------------------------------------------------
elif app_mode == "📊 ML Model Performance & Analytics":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Machine Learning Model Performance & Latent Space Lab</div>
        <div class="hero-subtitle">Quantitative evaluation of Collaborative Filtering (SVD) against NMF Baseline, plus 2D Latent Factor Embeddings.</div>
    </div>
    """, unsafe_allow_html=True)
    
    metrics = pipeline.metrics
    svd_m = metrics["SVD (Proposed)"]
    nmf_m = metrics["NMF (Baseline)"]
    
    st.markdown("### 📈 Evaluation Metrics Benchmark (20% Test Split)")
    b_col1, b_col2, b_col3, b_col4 = st.columns(4)
    with b_col1:
        st.metric("SVD RMSE (Lower is Better)", f"{svd_m['RMSE']}", delta=f"{nmf_m['RMSE'] - svd_m['RMSE']:.4f} vs NMF", delta_color="inverse")
    with b_col2:
        st.metric("SVD MAE", f"{svd_m['MAE']}", delta=f"{nmf_m['MAE'] - svd_m['MAE']:.4f} vs NMF", delta_color="inverse")
    with b_col3:
        st.metric("SVD Recall@5", f"{svd_m['Recall@5'] * 100:.1f}%", delta=f"{(svd_m['Recall@5'] - nmf_m['Recall@5']) * 100:.1f}%")
    with b_col4:
        st.metric("SVD NDCG@5 (Ranking Quality)", f"{svd_m['NDCG@5']:.4f}", delta=f"{svd_m['NDCG@5'] - nmf_m['NDCG@5']:.4f}")
        
    st.markdown("<br>", unsafe_allow_html=True)
    
    # Latent Factor Embedding 2D Projection
    st.markdown("### 🌌 Course Latent Space Embeddings (PCA 2D Projection)")
    st.caption("Visualizes how SVD automatically groups courses by tech domain in latent space without supervision.")
    
    item_factors = pipeline.svd_model.item_factors
    pca = PCA(n_components=2)
    coords = pca.fit_transform(item_factors)
    
    plot_df = pd.DataFrame({
        'x': coords[:, 0],
        'y': coords[:, 1],
        'module_id': [pipeline.svd_model.idx_to_item[i] for i in range(len(coords))]
    })
    plot_df = plot_df.merge(pipeline.courses_df[['module_id', 'title', 'domain', 'difficulty_level']], on='module_id')
    
    fig, ax = plt.subplots(figsize=(10, 6), facecolor='#0f172a')
    ax.set_facecolor('#1e293b')
    
    domain_colors = {
        "AI & Machine Learning": "#818cf8",
        "Data Science & Analytics": "#38bdf8",
        "Full-Stack Web Development": "#34d399",
        "Mobile Application Development": "#fbbf24",
        "Cloud Computing & DevOps": "#f87171",
        "Cybersecurity & Ethical Hacking": "#c084fc"
    }
    
    for domain, grp in plot_df.groupby('domain'):
        color = domain_colors.get(domain, '#ffffff')
        ax.scatter(grp['x'], grp['y'], label=domain, color=color, s=80, alpha=0.9, edgecolors='none')
        for _, row in grp.iterrows():
            ax.annotate(row['module_id'], (row['x'], row['y']), color='#cbd5e1', fontsize=7, alpha=0.8, xytext=(4, 4), textcoords='offset points')
            
    ax.set_title("SVD Course Latent Factor Projections", color='#f8fafc', fontsize=14, pad=12, fontweight='bold')
    ax.set_xlabel("Latent Factor Dimension 1", color='#94a3b8')
    ax.set_ylabel("Latent Factor Dimension 2", color='#94a3b8')
    ax.tick_params(colors='#64748b')
    ax.legend(facecolor='#0f172a', edgecolor='#334155', labelcolor='#f1f5f9', fontsize=8)
    for spine in ax.spines.values():
        spine.set_color('#334155')
        
    st.pyplot(fig)

# ----------------------------------------------------------------------
# VIEW 4: INTERACTIVE COURSE CATALOG & PREREQUISITES
# ----------------------------------------------------------------------
elif app_mode == "📚 Course & Prerequisite Catalog":
    st.markdown("""
    <div class="hero-container">
        <div class="hero-title">Course Catalog & Prerequisite Knowledge Graph</div>
        <div class="hero-subtitle">Explore the full curriculum of 37 modules across 6 technical domains with prerequisite linkages.</div>
    </div>
    """, unsafe_allow_html=True)
    
    courses_df = pipeline.courses_df
    
    selected_domain = st.selectbox("Filter by Domain Track:", ["All Tracks"] + list(courses_df['domain'].unique()))
    if selected_domain != "All Tracks":
        filtered_df = courses_df[courses_df['domain'] == selected_domain]
    else:
        filtered_df = courses_df
        
    st.dataframe(
        filtered_df[['module_id', 'title', 'domain', 'difficulty_level', 'duration_hours', 'rating_avg', 'prerequisites', 'skills']],
        use_container_width=True
    )
