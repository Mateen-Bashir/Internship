"""
FastAPI Backend Server for Personalized Learning Path Recommendation System
Internee.pk - Task 3

Exposes REST APIs for:
- Intern Profiles & History
- SVD Personalized Recommendations & DAG Milestones
- Cold-Start Path Generation
- Machine Learning Benchmarks & 2D PCA Latent Factors
- Full Course Catalog with Prerequisites
"""

import os
import sys
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Optional, List
from sklearn.decomposition import PCA

# Add project root to sys.path
sys.path.insert(0, os.path.dirname(__file__))

from src.recommender_pipeline import PersonalizedLearningRecommenderPipeline

app = FastAPI(
    title="Internee.pk Recommendation API",
    description="Collaborative Filtering (SVD) & Prerequisite DAG Learning Path Recommender",
    version="1.0.0"
)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize pipeline once on startup
pipeline = PersonalizedLearningRecommenderPipeline()

# ----------------------------------------------------------------------
# PYDANTIC SCHEMAS
# ----------------------------------------------------------------------
class ColdStartRequest(BaseModel):
    target_track: str
    skill_level: str = "Beginner"
    top_n: int = 6

# ----------------------------------------------------------------------
# API ROUTES
# ----------------------------------------------------------------------
@app.get("/api/health")
def health_check():
    return {"status": "online", "model": "SVD Matrix Factorization", "courses_count": len(pipeline.courses_df)}

@app.get("/api/interns")
def get_interns(track: Optional[str] = None, search: Optional[str] = None):
    """Returns list of intern profiles with optional domain filtering and search."""
    df = pipeline.profiles_df.copy().fillna("None")
    if track and track != "All":
        df = df[df['primary_track'] == track]
    if search:
        search_lower = search.lower()
        df = df[df['name'].str.lower().str.contains(search_lower) | df['intern_id'].str.lower().str.contains(search_lower)]
    return df.to_dict(orient="records")

@app.get("/api/recommend/{intern_id}")
def get_recommendation(intern_id: str, top_n: int = Query(6, ge=3, le=12)):
    """Returns personalized learning path recommendations for an existing intern."""
    profile = pipeline.get_intern_profile(intern_id)
    if not profile:
        raise HTTPException(status_code=404, detail=f"Intern ID '{intern_id}' not found.")
    
    roadmap = pipeline.recommend_for_intern(intern_id, top_n=top_n)
    return roadmap

@app.post("/api/cold-start")
def get_cold_start_recommendation(payload: ColdStartRequest):
    """Generates roadmap for a new intern without prior history."""
    roadmap = pipeline.recommend_cold_start(
        target_track=payload.target_track,
        skill_level=payload.skill_level,
        top_n=payload.top_n
    )
    return roadmap

@app.get("/api/courses")
def get_courses(domain: Optional[str] = None):
    """Returns all courses with prerequisites and skill mappings."""
    df = pipeline.courses_df.copy().fillna("None")
    if domain and domain != "All":
        df = df[df['domain'] == domain]
    return df.to_dict(orient="records")

@app.get("/api/metrics")
def get_metrics():
    """Returns quantitative ML evaluation benchmarks and 2D PCA latent factor coordinates."""
    metrics = pipeline.metrics
    
    # Compute 2D PCA embeddings of SVD item latent factors
    item_factors = pipeline.svd_model.item_factors
    pca = PCA(n_components=2)
    coords = pca.fit_transform(item_factors)
    
    latent_points = []
    for idx in range(len(coords)):
        m_id = pipeline.svd_model.idx_to_item[idx]
        c_info = pipeline.courses_df[pipeline.courses_df['module_id'] == m_id].iloc[0]
        latent_points.append({
            "module_id": m_id,
            "title": str(c_info['title']),
            "domain": str(c_info['domain']),
            "difficulty_level": str(c_info['difficulty_level']),
            "x": round(float(coords[idx, 0]), 4),
            "y": round(float(coords[idx, 1]), 4)
        })
        
    return {
        "benchmarks": metrics,
        "latent_space": latent_points,
        "summary": {
            "total_interns": len(pipeline.profiles_df),
            "total_modules": len(pipeline.courses_df),
            "total_interactions": len(pipeline.interactions_df),
            "sparsity_pct": 51.24
        }
    }

# ----------------------------------------------------------------------
# SERVE REACT FRONTEND (STATIC BUILD)
# ----------------------------------------------------------------------
FRONTEND_DIST = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")
    
    @app.get("/{full_path:path}")
    async def serve_react_app(full_path: str):
        file_path = os.path.join(FRONTEND_DIST, full_path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=8000, reload=True)
