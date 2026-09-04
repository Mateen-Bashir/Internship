import sys
import urllib.request
import json
import os

if sys.platform.startswith("win"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

BASE_URL = "http://127.0.0.1:8000"

def test_api():
    print(f"Testing FastAPI server endpoints at {BASE_URL}...")

    # 1. Test Index
    with urllib.request.urlopen(f"{BASE_URL}/") as res:
        assert res.status == 200
        html = res.read().decode("utf-8")
        assert "Internee.pk Interview Studio" in html
        print("✓ GET / (HTML index) passed")

    # 2. Test CSS Static
    with urllib.request.urlopen(f"{BASE_URL}/static/app.css") as res:
        assert res.status == 200
        print("✓ GET /static/app.css passed")

    # 3. Test JS Static
    with urllib.request.urlopen(f"{BASE_URL}/static/app.js") as res:
        assert res.status == 200
        print("✓ GET /static/app.js passed")

    # 4. Test Stats
    with urllib.request.urlopen(f"{BASE_URL}/api/stats") as res:
        assert res.status == 200
        data = json.loads(res.read().decode("utf-8"))
        assert data["total_questions"] >= 900
        assert data["total_profiles"] == 60
        assert data["total_jobs"] == 8
        print(f"✓ GET /api/stats passed ({data['total_questions']} questions, {data['total_profiles']} profiles)")

    # 5. Test Profiles
    with urllib.request.urlopen(f"{BASE_URL}/api/profiles") as res:
        assert res.status == 200
        profiles = json.loads(res.read().decode("utf-8"))
        assert len(profiles) == 60
        print("✓ GET /api/profiles passed")

    # 6. Test Jobs
    with urllib.request.urlopen(f"{BASE_URL}/api/jobs") as res:
        assert res.status == 200
        jobs = json.loads(res.read().decode("utf-8"))
        assert len(jobs) == 8
        print("✓ GET /api/jobs passed")

    # 7. Test Gap Analysis Endpoint
    gap_payload = json.dumps({"profile": profiles[0], "job_desc": jobs[0]}).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/analyze-gap", data=gap_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        gap_res = json.loads(res.read().decode("utf-8"))
        assert "overall_fit_score" in gap_res
        print(f"✓ POST /api/analyze-gap passed (Fit Score: {gap_res['overall_fit_score']}%)")

    # 8. Test Generation Endpoint
    gen_payload = json.dumps({
        "profile": profiles[0],
        "job_desc": jobs[0],
        "backend": "rag_neural",
        "num_technical": 5,
        "num_behavioral": 3,
        "num_project": 2
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/generate-kit", data=gen_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        gen_res = json.loads(res.read().decode("utf-8"))
        assert "kit" in gen_res
        assert len(gen_res["kit"]["technical_questions"]) == 5
        assert len(gen_res["kit"]["behavioral_questions"]) == 3
        print(f"✓ POST /api/generate-kit passed (CQI: {gen_res['benchmark']['composite_quality_index']}%)")

    # 9. Test Evaluate Response Endpoint
    eval_payload = json.dumps({
        "question_data": gen_res["kit"]["technical_questions"][0],
        "candidate_response": "We use gradient descent with learning rate decay to minimize loss calculated by the chain rule."
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/evaluate-response", data=eval_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        eval_res = json.loads(res.read().decode("utf-8"))
        assert "score" in eval_res
        print(f"✓ POST /api/evaluate-response passed (Score: {eval_res['score']}/5.0)")

    # 10. Test Export Endpoint
    export_payload = json.dumps({
        "kit": gen_res["kit"],
        "format": "markdown"
    }).encode("utf-8")
    req = urllib.request.Request(f"{BASE_URL}/api/export", data=export_payload, headers={"Content-Type": "application/json"})
    with urllib.request.urlopen(req) as res:
        assert res.status == 200
        print("✓ POST /api/export passed (Markdown generated)")

    print("\n🎉 ALL 10 SERVER ENDPOINTS & STATIC ASSETS VERIFIED 100% WORKING!\n")

if __name__ == "__main__":
    test_api()
