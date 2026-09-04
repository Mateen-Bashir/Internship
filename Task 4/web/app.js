// State variables
let profiles = [];
let jobs = [];
let tracks = [];
let currentGapAnalysis = null;
let currentGeneratedKit = null;
let currentMockQuestion = null;

// Initialization
document.addEventListener("DOMContentLoaded", async () => {
    await loadInitialData();
    drawRadarChart({
        "Core Technical Match": 85,
        "Preferred Tooling": 65,
        "Track Alignment": 100,
        "Project Relevance": 90,
        "Academic / Foundational": 88
    });
    searchQuestionBank();
});

async function loadInitialData() {
    try {
        const [statsRes, profilesRes, jobsRes, tracksRes] = await Promise.all([
            fetch("/api/stats").then(r => r.json()),
            fetch("/api/profiles").then(r => r.json()),
            fetch("/api/jobs").then(r => r.json()),
            fetch("/api/tracks").then(r => r.json())
        ]);

        profiles = profilesRes;
        jobs = jobsRes;
        tracks = tracksRes;

        // Populate stats in header
        if (statsRes.total_questions) document.getElementById("stat-q-count").innerText = `${statsRes.total_questions}+`;
        if (statsRes.total_profiles) document.getElementById("stat-p-count").innerText = statsRes.total_profiles;
        if (statsRes.total_jobs) document.getElementById("stat-j-count").innerText = statsRes.total_jobs;

        // Populate Profiles Dropdown
        const profSelect = document.getElementById("select-profile");
        profSelect.innerHTML = profiles.map(p => `
            <option value="${p.id}">${p.name} (${p.degree} &bull; ${p.track})</option>
        `).join("");

        // Populate Jobs Dropdown
        const jobSelect = document.getElementById("select-job");
        jobSelect.innerHTML = jobs.map(j => `
            <option value="${j.id}">${j.title} &bull; [${j.track}]</option>
        `).join("");

        // Populate Track Filters
        const trackFilter = document.getElementById("filter-track");
        trackFilter.innerHTML = `<option value="">All Tracks</option>` + tracks.map(t => `<option value="${t}">${t}</option>`).join("");

        // Initial Gap Analysis
        await onProfileChange();
    } catch (e) {
        console.error("Error loading initial data:", e);
        showToast("Error loading system data. Check server console.");
    }
}

// Navigation Tabs
function switchTab(tabId) {
    document.querySelectorAll(".tab-pane").forEach(p => p.classList.remove("active"));
    document.querySelectorAll(".tab-btn").forEach(b => b.classList.remove("active"));

    if (tabId === "studio") {
        document.getElementById("tab-studio").classList.add("active");
        event?.currentTarget?.classList.add("active") || document.querySelectorAll(".tab-btn")[0].classList.add("active");
    } else if (tabId === "mock") {
        document.getElementById("tab-mock").classList.add("active");
        event?.currentTarget?.classList.add("active") || document.querySelectorAll(".tab-btn")[1].classList.add("active");
        populateMockQuestions();
    } else if (tabId === "benchmarks") {
        document.getElementById("tab-benchmarks").classList.add("active");
        event?.currentTarget?.classList.add("active") || document.querySelectorAll(".tab-btn")[2].classList.add("active");
    }
}

function onBackendChange() {
    const val = document.getElementById("select-backend").value;
    const apiKeyGroup = document.getElementById("api-key-group");
    if (val === "openai" || val === "groq" || val === "custom_api") {
        apiKeyGroup.style.display = "block";
    } else {
        apiKeyGroup.style.display = "none";
    }
}

// Update Gap Analysis when candidate or job changes
async function onProfileChange() {
    const pId = document.getElementById("select-profile").value;
    const profile = profiles.find(p => p.id === pId);
    if (!profile) return;

    // Update summary text
    document.getElementById("cand-summary-preview").innerHTML = `
        <strong>${profile.name}</strong> &bull; ${profile.university} (GPA: ${profile.gpa})<br>
        <em>Skills:</em> ${profile.technical_skills.join(", ")}
    `;

    await runGapAnalysis();
}

async function onJobChange() {
    await runGapAnalysis();
}

async function runGapAnalysis() {
    const pId = document.getElementById("select-profile").value;
    const jId = document.getElementById("select-job").value;
    const profile = profiles.find(p => p.id === pId);
    const job = jobs.find(j => j.id === jId);

    if (!profile || !job) return;

    try {
        const res = await fetch("/api/analyze-gap", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ profile, job_desc: job })
        });
        const data = await res.json();
        currentGapAnalysis = data;

        // Update UI
        const scoreVal = document.getElementById("fit-score-val");
        scoreVal.innerText = `${data.overall_fit_score}%`;
        
        const badge = document.getElementById("gap-badge");
        if (data.overall_fit_score >= 80) {
            badge.className = "badge badge-easy";
            badge.innerText = "High Compatibility";
        } else if (data.overall_fit_score >= 60) {
            badge.className = "badge badge-medium";
            badge.innerText = "Moderate Fit";
        } else {
            badge.className = "badge badge-hard";
            badge.innerText = "Challenging Fit";
        }

        // Matched Skills
        const matchedContainer = document.getElementById("matched-skills-tags");
        matchedContainer.innerHTML = data.matched_required_skills.length > 0 
            ? data.matched_required_skills.map(s => `<span class="tag tag-match">✓ ${s}</span>`).join("")
            : `<span style="font-size:0.75rem; color:var(--text-muted);">None directly matched</span>`;

        // Missing Skills
        const missingContainer = document.getElementById("missing-skills-tags");
        missingContainer.innerHTML = data.missing_required_skills.length > 0 
            ? data.missing_required_skills.map(s => `<span class="tag tag-gap">⚠ ${s}</span>`).join("")
            : `<span class="tag tag-match">✓ Complete Core Match</span>`;

        // Strategy Recommendations
        const recList = document.getElementById("strategy-recommendations");
        recList.innerHTML = data.recommendations.map(r => `<li>${r}</li>`).join("");

        // Draw Canvas Radar Chart
        if (data.radar_dimensions) {
            drawRadarChart(data.radar_dimensions);
        }
    } catch (e) {
        console.error("Gap analysis error:", e);
    }
}

// -------------------------------------------------------------
// Pure Canvas Radar Chart
// -------------------------------------------------------------
function drawRadarChart(dimensions) {
    const canvas = document.getElementById("radarChart");
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    const width = canvas.width;
    const height = canvas.height;
    const centerX = width / 2;
    const centerY = height / 2 + 5;
    const radius = Math.min(centerX, centerY) - 38;

    ctx.clearRect(0, 0, width, height);

    const keys = Object.keys(dimensions);
    const numPoints = keys.length;
    const angleStep = (Math.PI * 2) / numPoints;

    // Draw concentric polygon grid
    const levels = 4;
    for (let l = 1; l <= levels; l++) {
        const levelRadius = (radius / levels) * l;
        ctx.beginPath();
        for (let i = 0; i < numPoints; i++) {
            const angle = i * angleStep - Math.PI / 2;
            const x = centerX + levelRadius * Math.cos(angle);
            const y = centerY + levelRadius * Math.sin(angle);
            if (i === 0) ctx.moveTo(x, y);
            else ctx.lineTo(x, y);
        }
        ctx.closePath();
        ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    // Draw spokes and labels
    ctx.font = "10px Inter, sans-serif";
    ctx.fillStyle = "#94a3b8";
    ctx.textAlign = "center";
    ctx.textBaseline = "middle";

    for (let i = 0; i < numPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const xSpoke = centerX + radius * Math.cos(angle);
        const ySpoke = centerY + radius * Math.sin(angle);

        ctx.beginPath();
        ctx.moveTo(centerX, centerY);
        ctx.lineTo(xSpoke, ySpoke);
        ctx.strokeStyle = "rgba(255, 255, 255, 0.08)";
        ctx.stroke();

        // Label Position
        const labelRadius = radius + 22;
        const xLabel = centerX + labelRadius * Math.cos(angle);
        const yLabel = centerY + labelRadius * Math.sin(angle);
        ctx.fillText(keys[i], xLabel, yLabel);
    }

    // Draw Data Polygon
    ctx.beginPath();
    for (let i = 0; i < numPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const val = dimensions[keys[i]] || 50;
        const pointRadius = (radius * (val / 100));
        const x = centerX + pointRadius * Math.cos(angle);
        const y = centerY + pointRadius * Math.sin(angle);
        if (i === 0) ctx.moveTo(x, y);
        else ctx.lineTo(x, y);
    }
    ctx.closePath();
    
    // Fill Gradient
    const gradient = ctx.createRadialGradient(centerX, centerY, 10, centerX, centerY, radius);
    gradient.addColorStop(0, "rgba(99, 102, 241, 0.45)");
    gradient.addColorStop(1, "rgba(6, 182, 212, 0.2)");
    ctx.fillStyle = gradient;
    ctx.fill();

    ctx.strokeStyle = "#6366f1";
    ctx.lineWidth = 2.2;
    ctx.stroke();

    // Data points circles
    for (let i = 0; i < numPoints; i++) {
        const angle = i * angleStep - Math.PI / 2;
        const val = dimensions[keys[i]] || 50;
        const pointRadius = (radius * (val / 100));
        const x = centerX + pointRadius * Math.cos(angle);
        const y = centerY + pointRadius * Math.sin(angle);

        ctx.beginPath();
        ctx.arc(x, y, 4, 0, Math.PI * 2);
        ctx.fillStyle = "#38bdf8";
        ctx.fill();
        ctx.strokeStyle = "#fff";
        ctx.lineWidth = 1.5;
        ctx.stroke();
    }
}

// -------------------------------------------------------------
// Generate Interview Kit Action
// -------------------------------------------------------------
async function generateInterviewKit() {
    const pId = document.getElementById("select-profile").value;
    const jId = document.getElementById("select-job").value;
    const backend = document.getElementById("select-backend").value;
    const apiKey = document.getElementById("input-api-key").value;
    const numTech = parseInt(document.getElementById("num-tech").value) || 5;
    const numBeh = parseInt(document.getElementById("num-beh").value) || 3;
    const numProj = parseInt(document.getElementById("num-proj").value) || 2;

    const profile = profiles.find(p => p.id === pId);
    const job = jobs.find(j => j.id === jId);

    if (!profile || !job) {
        showToast("Please select a candidate profile and target job.");
        return;
    }

    const btn = document.getElementById("btn-generate");
    const originalText = btn.innerHTML;
    btn.innerHTML = `<span class="loading-spinner"></span> Generating Custom Kit...`;
    btn.disabled = true;

    try {
        const response = await fetch("/api/generate-kit", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                profile,
                job_desc: job,
                backend,
                api_key: apiKey,
                num_technical: numTech,
                num_behavioral: numBeh,
                num_project: numProj
            })
        });

        if (!response.ok) {
            const err = await response.json();
            throw new Error(err.detail || "Generation failed.");
        }

        const data = await response.json();
        currentGeneratedKit = data.kit;

        // Render Generated Kit
        renderKit(data.kit);

        // Update Benchmark tab values
        if (data.benchmark) {
            updateBenchmarkMetrics(data.benchmark);
        }

        showToast("✓ Custom Interview Kit generated successfully!");
    } catch (e) {
        console.error("Kit Generation Error:", e);
        showToast(`Generation Error: ${e.message}`);
    } finally {
        btn.innerHTML = originalText;
        btn.disabled = false;
    }
}

function renderKit(kit) {
    const meta = kit.interview_meta || {};
    const techQ = kit.technical_questions || [];
    const behQ = kit.behavioral_questions || [];
    const projQ = kit.project_deep_dive_questions || [];
    const coding = kit.coding_scenario || null;

    document.getElementById("kit-meta-desc").innerText = `Target: ${meta.target_role} • Candidate: ${meta.candidate_name} • Backend: ${meta.generation_backend}`;

    let html = "";

    // 1. Technical Questions Section
    html += `
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.05rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>🛠️</span> Technical Questions (${techQ.length} Questions)
            </h3>
    `;

    techQ.forEach((q) => {
        const diffClass = q.difficulty === "Easy" ? "badge-easy" : q.difficulty === "Hard" ? "badge-hard" : "badge-medium";
        html += `
            <div class="q-item-card">
                <div class="q-header">
                    <div class="q-title">[${q.id}] ${q.topic}</div>
                    <div>
                        <span class="badge ${diffClass}">${q.difficulty}</span>
                        <span class="badge" style="background: rgba(255,255,255,0.06); color: #cbd5e1;">${q.skill_targeted}</span>
                    </div>
                </div>
                <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;"><em>Rationale: ${q.rationale}</em></p>
                <div class="q-text">"${q.question}"</div>
                
                <div class="q-detail-box">
                    <strong>Expected Key Concepts:</strong>
                    <ul style="margin: 0.3rem 0 0.5rem 1.2rem; font-size: 0.82rem;">
                        ${q.expected_answer_points.map(p => `<li>${p}</li>`).join("")}
                    </ul>
                    <div style="margin-top: 0.4rem;">
                        <span style="color: #38bdf8; font-weight: 600;">5/5 Rubric:</span> ${q.rubric_5_scale}
                    </div>
                    <div style="margin-top: 0.4rem; color: #a5b4fc;">
                        <strong>Follow-up Probe:</strong> <em>"${q.follow_up_probe}"</em>
                    </div>
                </div>
            </div>
        `;
    });
    html += `</div>`;

    // 2. Behavioral Questions Section
    html += `
        <div style="margin-bottom: 1.5rem;">
            <h3 style="font-size: 1.05rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                <span>🤝</span> Behavioral Questions &bull; STAR Methodology (${behQ.length} Questions)
            </h3>
    `;

    behQ.forEach((q) => {
        const star = q.star_framework || {};
        html += `
            <div class="q-item-card">
                <div class="q-header">
                    <div class="q-title">[${q.id}] Competency: ${q.competency}</div>
                    <span class="badge badge-medium">STAR Framework</span>
                </div>
                <div class="q-text">"${q.question}"</div>
                
                <div class="q-detail-box">
                    <strong>STAR Framework Indicators:</strong>
                    <div class="star-grid">
                        <div class="star-cell"><strong>S (Situation):</strong> ${star.situation || 'Context of challenge'}</div>
                        <div class="star-cell"><strong>T (Task):</strong> ${star.task || 'Objective required'}</div>
                        <div class="star-cell"><strong>A (Action):</strong> ${star.action || 'Engineering steps taken'}</div>
                        <div class="star-cell"><strong>R (Result):</strong> ${star.result || 'Outcome and learning'}</div>
                    </div>
                    <div style="margin-top: 0.6rem; display: flex; gap: 1rem; flex-wrap: wrap;">
                        <div style="color: #34d399; font-size: 0.8rem;">
                            <strong>✓ Green Flags:</strong> ${(q.green_flags || []).join(", ")}
                        </div>
                        <div style="color: #f87171; font-size: 0.8rem;">
                            <strong>⚠ Red Flags:</strong> ${(q.red_flags || []).join(", ")}
                        </div>
                    </div>
                    <div style="margin-top: 0.4rem; color: #a5b4fc;">
                        <strong>Follow-up Probe:</strong> <em>"${q.follow_up_probe}"</em>
                    </div>
                </div>
            </div>
        `;
    });
    html += `</div>`;

    // 3. Project Deep-Dive Section
    if (projQ.length > 0) {
        html += `
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.05rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>🚀</span> Project Portfolio Deep-Dive (${projQ.length} Questions)
                </h3>
        `;
        projQ.forEach((q) => {
            html += `
                <div class="q-item-card">
                    <div class="q-header">
                        <div class="q-title">[${q.id}] Flagship Project: ${q.project_name}</div>
                        <span class="badge" style="background: rgba(139,92,246,0.2); color: #c084fc;">Project Deep-Dive</span>
                    </div>
                    <p style="font-size: 0.8rem; color: var(--text-muted); margin-bottom: 0.5rem;"><em>Focus: ${q.architectural_focus}</em></p>
                    <div class="q-text">"${q.question}"</div>
                    <div style="font-size: 0.85rem; color: #a5b4fc; margin-top: 0.5rem;">
                        <strong>Follow-up Probe:</strong> <em>"${q.follow_up_probe}"</em>
                    </div>
                </div>
            `;
        });
        html += `</div>`;
    }

    // 4. Live Coding / Practical Troubleshooting Scenario
    if (coding) {
        html += `
            <div style="margin-bottom: 1.5rem;">
                <h3 style="font-size: 1.05rem; color: #fff; margin-bottom: 0.75rem; display: flex; align-items: center; gap: 0.5rem;">
                    <span>💻</span> Live Practical Scenario
                </h3>
                <div class="q-item-card" style="border-left: 3px solid var(--accent-cyan);">
                    <div class="q-title" style="margin-bottom: 0.5rem;">${coding.title}</div>
                    <div class="q-text" style="border-left: none; background: transparent; padding: 0;">${coding.scenario}</div>
                    <div class="q-detail-box" style="margin-top: 0.75rem;">
                        <strong>Evaluation Criteria:</strong>
                        <ul style="margin: 0.3rem 0 0 1.2rem; font-size: 0.82rem;">
                            ${coding.evaluation_criteria.map(c => `<li>${c}</li>`).join("")}
                        </ul>
                    </div>
                </div>
            </div>
        `;
    }

    document.getElementById("kit-content-container").innerHTML = html;
}

// -------------------------------------------------------------
// Export Action
// -------------------------------------------------------------
async function exportKit(format) {
    if (!currentGeneratedKit) {
        showToast("Please generate an interview kit first.");
        return;
    }

    try {
        const response = await fetch("/api/export", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                kit: currentGeneratedKit,
                format: format
            })
        });

        if (!response.ok) throw new Error("Export failed.");

        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement("a");
        a.href = url;
        const candName = (currentGeneratedKit.interview_meta?.candidate_name || "candidate").toLowerCase().replace(/ /g, "_");
        const ext = format === "json" ? "json" : format === "html" ? "html" : "md";
        a.download = `interview_kit_${candName}.${ext}`;
        document.body.appendChild(a);
        a.click();
        a.remove();
        showToast(`✓ Downloaded ${format.toUpperCase()} packet!`);
    } catch (e) {
        console.error("Export error:", e);
        showToast("Export failed.");
    }
}

// -------------------------------------------------------------
// Mock Interview & Grader Tab Logic
// -------------------------------------------------------------
function populateMockQuestions() {
    const select = document.getElementById("mock-question-select");
    let options = [];

    if (currentGeneratedKit && currentGeneratedKit.technical_questions) {
        options.push(...currentGeneratedKit.technical_questions.map(q => ({
            id: q.id,
            label: `[Generated] ${q.topic} (${q.difficulty})`,
            data: q
        })));
        options.push(...currentGeneratedKit.behavioral_questions.map(q => ({
            id: q.id,
            label: `[Generated STAR] ${q.competency}`,
            data: q
        })));
    } else {
        options = [
            {
                id: "T-DEFAULT-1",
                label: "Machine Learning: Overfitting & L1/L2 Regularization (Easy)",
                data: {
                    category: "Technical",
                    question: "What is the difference between L1 (Lasso) and L2 (Ridge) regularization, and when would you choose one over the other?",
                    expected_answer_points: [
                        "L1 penalizes absolute value of weights and induces sparsity",
                        "L2 penalizes squared magnitude of weights, shrinking weights without zeroing them",
                        "L1 is suitable for feature selection; L2 when many collinear features exist"
                    ],
                    rubric_5_scale: "Accurately explains mathematical difference, sparsity effect, and feature selection vs collinearity trade-offs.",
                    follow_up_probe: "What is ElasticNet and in what scenario does it outperform pure Lasso or Ridge?"
                }
            },
            {
                id: "B-DEFAULT-2",
                label: "Behavioral STAR: Handling Technical Disagreement & Conflict",
                data: {
                    category: "Behavioral",
                    question: "Describe a situation where you had a technical disagreement with a team member. How did you navigate the conversation to reach consensus?",
                    expected_answer_points: [
                        "Situation: Context of the technical disagreement",
                        "Task: Need to choose architecture without delaying progress",
                        "Action: Data-driven comparison, active listening, proof-of-concept testing",
                        "Result: Team alignment and positive project delivery"
                    ],
                    rubric_5_scale: "Structured STAR response emphasizing data over ego, active listening, and collective ownership.",
                    follow_up_probe: "If the chosen solution later caused a production regression, how did you handle it?"
                }
            }
        ];
    }

    select.innerHTML = options.map((opt, idx) => `
        <option value="${idx}">${opt.label}</option>
    `).join("");

    window._mockQuestionsList = options;
    onMockQuestionChange();
}

function onMockQuestionChange() {
    const idx = parseInt(document.getElementById("mock-question-select").value) || 0;
    if (window._mockQuestionsList && window._mockQuestionsList[idx]) {
        currentMockQuestion = window._mockQuestionsList[idx].data;
        document.getElementById("mock-question-display").innerText = `"${currentMockQuestion.question}"`;
    }
}

function loadSampleAnswer() {
    if (!currentMockQuestion) return;
    const isBeh = currentMockQuestion.category === "Behavioral" || currentMockQuestion.competency;
    if (isBeh) {
        document.getElementById("mock-candidate-response").value = 
`During our university final year capstone project, our team had a major disagreement on whether to use MongoDB or PostgreSQL for our transaction system (Situation). My role was backend lead, and we needed to finalize the database schema by Friday without causing friction (Task). 

Instead of arguing theoretically, I organized a 1-hour benchmark session where we built quick proof-of-concepts for both databases testing concurrency and query execution times under 50,000 mock transactions (Action). The benchmark showed PostgreSQL had superior transaction ACID guarantees and indexing speed for our specific relational user ledger.

As a result, the team unanimously agreed on PostgreSQL, we delivered the sprint 2 days early, and our database supported all user transactions during the final presentation with zero errors (Result).`;
    } else {
        document.getElementById("mock-candidate-response").value = 
`L1 (Lasso) regularization adds a penalty equal to the absolute value of the magnitude of coefficients (|w|), which drives less important feature weights exactly to zero, effectively acting as an automatic feature selection mechanism. 

In contrast, L2 (Ridge) regularization adds a penalty equal to the square of the magnitude of coefficients (w^2), which shrinks weights smoothly towards zero without making them exactly zero. 

I would choose L1 when I have a high-dimensional dataset with many irrelevant or noisy features where a sparse, interpretable model is needed. I would choose L2 when dealing with multicollinearity, where correlated features share the penalty and retain their combined predictive power.`;
    }
    showToast("✨ Sample candidate answer loaded!");
}

async function gradeCandidateResponse() {
    if (!currentMockQuestion) {
        showToast("Please select a question to grade.");
        return;
    }
    const responseText = document.getElementById("mock-candidate-response").value;
    if (!responseText.trim()) {
        showToast("Please enter an answer before grading.");
        return;
    }

    const badge = document.getElementById("grade-status-badge");
    badge.className = "badge badge-medium";
    badge.innerText = "Grading...";

    try {
        const res = await fetch("/api/evaluate-response", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                question_data: currentMockQuestion,
                candidate_response: responseText
            })
        });

        const data = await res.json();
        renderGradeResult(data);
        badge.className = data.score >= 3.5 ? "badge badge-easy" : "badge badge-medium";
        badge.innerText = `Score: ${data.score}/5.0`;
        showToast("✓ Evaluation completed!");
    } catch (e) {
        console.error("Grading error:", e);
        showToast("Error grading response.");
    }
}

function renderGradeResult(data) {
    const container = document.getElementById("grade-result-container");
    
    let html = `
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div class="score-badge-huge">${data.score} <span style="font-size: 1.4rem; color: var(--text-secondary); font-weight: 500;">/ 5.0</span></div>
            <div style="font-size: 1.1rem; font-weight: 700; color: #fff; margin-top: 0.25rem;">${data.rating}</div>
            <p style="font-size: 0.85rem; color: var(--text-secondary); max-width: 450px; margin: 0.4rem auto 0;">${data.feedback}</p>
        </div>

        <div style="margin-bottom: 1.25rem;">
            <div style="display: flex; justify-content: space-between; font-size: 0.8rem; font-weight: 600;">
                <span>Key Criteria Coverage</span>
                <span>${data.concept_coverage_pct}%</span>
            </div>
            <div class="progress-bar">
                <div class="progress-fill" style="width: ${data.concept_coverage_pct}%;"></div>
            </div>
        </div>

        <div style="margin-bottom: 1rem;">
            <label style="margin-bottom: 0.2rem;">Identified Strengths:</label>
            <ul style="font-size: 0.85rem; color: #34d399; padding-left: 1.2rem;">
                ${data.strengths.map(s => `<li>${s}</li>`).join("")}
            </ul>
        </div>

        <div style="margin-bottom: 1rem;">
            <label style="margin-bottom: 0.2rem;">Areas for Improvement / Missing Criteria:</label>
            <ul style="font-size: 0.85rem; color: #fbbf24; padding-left: 1.2rem;">
                ${data.missing_elements.map(m => `<li>${m}</li>`).join("")}
            </ul>
        </div>

        <div class="q-detail-box" style="border-left: 3px solid var(--accent-violet);">
            <strong style="color: #c084fc;">Recommended Adaptive Follow-up:</strong><br>
            <em style="color: #f1f5f9; font-size: 0.9rem;">"${data.follow_up_prompt}"</em>
        </div>
    `;

    container.innerHTML = html;
}

// -------------------------------------------------------------
// Benchmark Tab Logic & Question Bank Search
// -------------------------------------------------------------
function updateBenchmarkMetrics(bench) {
    if (!bench) return;
    document.getElementById("m-cqi").innerText = `${bench.composite_quality_index}%`;
    document.getElementById("m-coverage").innerText = `${bench.skill_coverage_pct}%`;
    document.getElementById("m-diff").innerText = `${bench.difficulty_balance_score}%`;
    document.getElementById("m-star").innerText = `${bench.star_completeness_pct}%`;
    document.getElementById("m-dist2").innerText = `${bench.lexical_distinct_2_ratio}`;
    document.getElementById("m-pers").innerText = `${bench.personalization_pct}%`;
}

async function searchQuestionBank() {
    const track = document.getElementById("filter-track")?.value || "";
    const difficulty = document.getElementById("filter-difficulty")?.value || "";
    const keyword = document.getElementById("filter-search")?.value || "";

    const params = new URLSearchParams();
    if (track) params.append("track", track);
    if (difficulty) params.append("difficulty", difficulty);
    if (keyword) params.append("keyword", keyword);
    params.append("limit", "25");

    try {
        const res = await fetch(`/api/search-questions?${params.toString()}`);
        const questions = await res.json();

        const container = document.getElementById("bank-search-results");
        if (!questions || questions.length === 0) {
            container.innerHTML = `<div style="text-align: center; color: var(--text-muted); padding: 2rem;">No questions found matching criteria.</div>`;
            return;
        }

        container.innerHTML = questions.map(q => {
            const diffClass = q.difficulty === "Easy" ? "badge-easy" : q.difficulty === "Hard" ? "badge-hard" : "badge-medium";
            return `
                <div class="q-item-card" style="padding: 0.85rem; margin-bottom: 0.75rem;">
                    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.4rem;">
                        <span style="font-weight: 700; font-size: 0.85rem; color: #fff;">[${q.id}] ${q.topic}</span>
                        <div>
                            <span class="badge ${diffClass}" style="font-size: 0.7rem;">${q.difficulty}</span>
                            <span class="badge" style="font-size: 0.7rem; background: rgba(255,255,255,0.06);">${q.track}</span>
                        </div>
                    </div>
                    <div style="font-size: 0.9rem; color: #f1f5f9; margin-bottom: 0.4rem;">"${q.question}"</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted);">
                        <strong>Skill:</strong> ${q.skill} &bull; <strong>Follow-up:</strong> "${q.follow_up}"
                    </div>
                </div>
            `;
        }).join("");
    } catch (e) {
        console.error("Bank search error:", e);
    }
}

// Toast Notification
function showToast(msg) {
    const toast = document.getElementById("toast");
    toast.innerText = msg;
    toast.style.display = "block";
    setTimeout(() => {
        toast.style.display = "none";
    }, 3500);
}
