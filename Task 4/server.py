"""
FastAPI Server for AI Interview Question Generator
Provides REST API endpoints and serves the interactive web frontend.
"""

import os
import json
from typing import Dict, Any, Optional, List
from fastapi import FastAPI, HTTPException, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from src.data_loader import DataLoader
from src.gap_analyzer import GapAnalyzer
from src.llm_generator import InterviewQuestionGenerator
from src.rubric_engine import RubricEngine
from src.mock_evaluator import MockResponseEvaluator
from src.export_service import ExportService
from src.evaluator import GenerationEvaluator

app = FastAPI(
    title="Internee.pk AI Interview Question Generator",
    description="Automated, role-specific technical and behavioral interview question set generator for interns",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize core services
loader = DataLoader()
generator = InterviewQuestionGenerator(loader)

# Ensure web directory exists
WEB_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "web")
os.makedirs(WEB_DIR, exist_ok=True)
os.makedirs("exports", exist_ok=True)

# ----------------- Request Models -----------------

class GapAnalysisRequest(BaseModel):
    profile: Dict[str, Any]
    job_desc: Dict[str, Any]

class GenerateKitRequest(BaseModel):
    profile: Dict[str, Any]
    job_desc: Dict[str, Any]
    backend: str = "rag_neural"
    api_key: Optional[str] = None
    model_name: Optional[str] = None
    api_url: Optional[str] = None
    num_technical: int = 5
    num_behavioral: int = 3
    num_project: int = 2

class EvaluateResponseRequest(BaseModel):
    question_data: Dict[str, Any]
    candidate_response: str

class ExportRequest(BaseModel):
    kit: Dict[str, Any]
    format: str = "markdown"  # "markdown", "json", "html"

# ----------------- REST Endpoints -----------------

@app.get("/api/health")
def health_check():
    return {"status": "online", "system": "AI Interview Question Generator", "version": "1.0.0"}

@app.get("/api/stats")
def get_system_stats():
    return {
        "total_questions": len(loader.question_bank),
        "total_profiles": len(loader.intern_profiles),
        "total_jobs": len(loader.job_descriptions),
        "tracks": loader.get_tracks()
    }

@app.get("/api/profiles")
def get_profiles():
    return loader.intern_profiles

@app.get("/api/jobs")
def get_jobs():
    return loader.job_descriptions

@app.get("/api/tracks")
def get_tracks():
    return loader.get_tracks()

@app.get("/api/search-questions")
def search_questions(
    track: Optional[str] = None,
    difficulty: Optional[str] = None,
    q_type: Optional[str] = None,
    keyword: Optional[str] = None,
    limit: int = 30
):
    return loader.search_questions(track=track, difficulty=difficulty, q_type=q_type, keyword=keyword, limit=limit)

@app.post("/api/analyze-gap")
def analyze_gap(req: GapAnalysisRequest):
    try:
        res = GapAnalyzer.analyze(req.profile, req.job_desc)
        return res
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/generate-kit")
def generate_kit(req: GenerateKitRequest):
    try:
        kit = generator.generate(
            profile=req.profile,
            job_desc=req.job_desc,
            backend=req.backend,
            api_key=req.api_key,
            model_name=req.model_name,
            api_url=req.api_url,
            num_technical=req.num_technical,
            num_behavioral=req.num_behavioral,
            num_project=req.num_project
        )
        # Compute benchmark evaluation metrics
        benchmark = GenerationEvaluator.evaluate_kit(kit, req.profile, req.job_desc)
        scorecard = RubricEngine.generate_scorecard_template(kit)
        
        return {
            "kit": kit,
            "benchmark": benchmark,
            "scorecard": scorecard
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/evaluate-response")
def evaluate_candidate_response(req: EvaluateResponseRequest):
    try:
        feedback = MockResponseEvaluator.evaluate_response(req.question_data, req.candidate_response)
        return feedback
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/export")
def export_kit(req: ExportRequest):
    try:
        cand_name = req.kit.get("interview_meta", {}).get("candidate_name", "candidate").lower().replace(" ", "_")
        if req.format == "json":
            filename = f"interview_kit_{cand_name}.json"
            path = os.path.join("exports", filename)
            ExportService.to_json(req.kit, path)
            return FileResponse(path, media_type="application/json", filename=filename)
        elif req.format == "html":
            filename = f"interview_kit_{cand_name}.html"
            path = os.path.join("exports", filename)
            ExportService.to_html(req.kit, path)
            return FileResponse(path, media_type="text/html", filename=filename)
        else:
            filename = f"interview_kit_{cand_name}.md"
            path = os.path.join("exports", filename)
            ExportService.to_markdown(req.kit, path)
            return FileResponse(path, media_type="text/markdown", filename=filename)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Mount static web directory
app.mount("/static", StaticFiles(directory=WEB_DIR), name="static")

@app.get("/")
def serve_index():
    index_file = os.path.join(WEB_DIR, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return HTMLResponse("<h2>AI Interview Question Generator is running. Static files are being compiled...</h2>")

if __name__ == "__main__":
    import uvicorn
    print("Starting Internee.pk Interview Question Generator Server on http://127.0.0.1:8000 ...")
    uvicorn.run(app, host="127.0.0.1", port=8000)
