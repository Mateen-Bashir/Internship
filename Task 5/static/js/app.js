/**
 * SkillMatrix AI - Frontend Logic
 * Handles interactive tabs, Chart.js visualizations, cohort search/filtering,
 * intern deep-dive drawer, and live custom resume/profile NLP analyzer.
 */

document.addEventListener("DOMContentLoaded", () => {
    initNavigation();
    initOverviewCharts();
    initInternsDirectory();
    initCustomAnalyzer();
});

// -------------------------------------------------------------
// 1. Navigation & Tab Switching
// -------------------------------------------------------------
function initNavigation() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabPanes = document.querySelectorAll(".tab-pane");
    const pageTitle = document.getElementById("page-title");
    const pageSubtitle = document.getElementById("page-subtitle");

    const titles = {
        "overview": {
            title: "Industry Demand & Intern Cohort Overview",
            sub: "NLP-driven skill gap quantification and personalized upskilling pathways"
        },
        "interns": {
            title: "Intern Cohort Talent Pool Directory",
            sub: "Explore individual readiness scores, skill deficiencies, and learning paths"
        },
        "custom-analyzer": {
            title: "Real-Time NLP Skill Gap Analyzer",
            sub: "Test custom resumes and skill sets against live industry benchmarks"
        },
        "methodology": {
            title: "Pipeline Architecture & Mathematical Formulation",
            sub: "TF-IDF Vectorization, K-Means Clustering, and Cosine Similarity equations"
        }
    };

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const tabKey = item.getAttribute("data-tab");
            
            navItems.forEach(n => n.classList.remove("active"));
            tabPanes.forEach(p => p.classList.remove("active"));

            item.classList.add("active");
            const targetPane = document.getElementById(`tab-${tabKey}`);
            if (targetPane) targetPane.classList.add("active");

            if (titles[tabKey]) {
                pageTitle.textContent = titles[tabKey].title;
                pageSubtitle.textContent = titles[tabKey].sub;
            }
        });
    });
}

// -------------------------------------------------------------
// 2. Overview Charts (Chart.js)
// -------------------------------------------------------------
let clusterChartInstance = null;
let skillGapBarChartInstance = null;

const CLUSTER_COLORS = ["#3b82f6", "#10b981", "#f59e0b", "#8b5cf6", "#ec4899", "#06b6d4"];

function initOverviewCharts() {
    // 2A. Cluster Scatter Chart
    fetch("/api/cluster-data")
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;
            renderClusterScatter(data.points, data.centroids);
        })
        .catch(err => console.error("Error loading cluster data:", err));

    // 2B. Skill Gap Bar Chart
    const domainSelector = document.getElementById("domainGapSelector");
    if (domainSelector) {
        domainSelector.addEventListener("change", (e) => {
            renderDomainSkillGapBar(e.target.value);
        });
        renderDomainSkillGapBar(domainSelector.value);
    }
}

function renderClusterScatter(points, centroids) {
    const ctx = document.getElementById("clusterScatterChart").getContext("2d");
    
    // Group points by cluster
    const datasets = [];
    const clusterNames = [
        "Cybersecurity", "Mobile Dev", "Cloud & DevOps", 
        "AI & ML", "Full Stack Web", "Data Science"
    ];

    for (let c = 0; c < 6; c++) {
        const clusterPts = points.filter(p => p.cluster === c).map(p => ({
            x: p.x,
            y: p.y,
            title: p.title,
            company: p.company
        }));

        datasets.push({
            label: clusterNames[c] || `Cluster ${c}`,
            data: clusterPts,
            backgroundColor: CLUSTER_COLORS[c % CLUSTER_COLORS.length] + "99",
            borderColor: CLUSTER_COLORS[c % CLUSTER_COLORS.length],
            borderWidth: 1,
            pointRadius: 4,
            pointHoverRadius: 7
        });
    }

    if (clusterChartInstance) clusterChartInstance.destroy();

    clusterChartInstance = new Chart(ctx, {
        type: "scatter",
        data: { datasets },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#9ca3af", font: { size: 10, family: "Plus Jakarta Sans" }, boxWidth: 10 }
                },
                tooltip: {
                    callbacks: {
                        label: (ctx) => {
                            const raw = ctx.raw;
                            return `${raw.title} (${raw.company})`;
                        }
                    }
                }
            },
            scales: {
                x: {
                    title: { display: true, text: "Principal Component 1", color: "#6b7280" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#6b7280" }
                },
                y: {
                    title: { display: true, text: "Principal Component 2", color: "#6b7280" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" },
                    ticks: { color: "#6b7280" }
                }
            }
        }
    });
}

const DOMAIN_SKILL_BENCHMARKS = {
    "AI & Machine Learning": {
        skills: ["PyTorch", "TensorFlow", "Deep Learning", "NLP", "Transformers", "Computer Vision", "MLOps", "Scikit-Learn"],
        demand: [92, 88, 95, 84, 76, 72, 68, 90],
        internSupply: [35, 40, 42, 28, 18, 22, 12, 65]
    },
    "Data Science & Analytics": {
        skills: ["Python", "SQL", "Pandas", "Scikit-Learn", "Tableau", "Power BI", "Feature Eng.", "Statistical Mod."],
        demand: [98, 94, 92, 85, 78, 70, 75, 80],
        internSupply: [90, 68, 75, 48, 25, 30, 22, 35]
    },
    "Full Stack & Web Development": {
        skills: ["JavaScript", "React", "Node.js", "TypeScript", "REST APIs", "MongoDB", "PostgreSQL", "Next.js"],
        demand: [96, 92, 86, 78, 88, 72, 70, 64],
        internSupply: [85, 62, 50, 28, 55, 45, 32, 20]
    },
    "Cloud Computing & DevOps": {
        skills: ["AWS", "Docker", "Kubernetes", "CI/CD", "Linux", "Terraform", "Git", "Prometheus"],
        demand: [90, 88, 82, 85, 92, 74, 94, 60],
        internSupply: [30, 42, 18, 25, 60, 15, 85, 10]
    },
    "Cybersecurity & Information Security": {
        skills: ["Network Security", "Linux", "Wireshark", "Ethical Hacking", "SIEM Tools", "OWASP Top 10", "Python", "Splunk"],
        demand: [94, 88, 80, 85, 76, 78, 82, 65],
        internSupply: [40, 55, 32, 28, 15, 20, 65, 12]
    },
    "Mobile Application Development": {
        skills: ["Flutter", "Dart", "React Native", "Mobile UI/UX", "REST APIs", "Firebase", "State Mgmt", "Kotlin"],
        demand: [88, 85, 80, 78, 90, 82, 84, 68],
        internSupply: [45, 42, 38, 52, 60, 40, 25, 18]
    }
};

function renderDomainSkillGapBar(domain) {
    const data = DOMAIN_SKILL_BENCHMARKS[domain] || DOMAIN_SKILL_BENCHMARKS["AI & Machine Learning"];
    const ctx = document.getElementById("skillGapBarChart").getContext("2d");

    if (skillGapBarChartInstance) skillGapBarChartInstance.destroy();

    skillGapBarChartInstance = new Chart(ctx, {
        type: "bar",
        data: {
            labels: data.skills,
            datasets: [
                {
                    label: "Industry Market Demand (%)",
                    data: data.demand,
                    backgroundColor: "rgba(59, 130, 246, 0.8)",
                    borderRadius: 4
                },
                {
                    label: "Intern Cohort Supply (%)",
                    data: data.internSupply,
                    backgroundColor: "rgba(16, 185, 129, 0.8)",
                    borderRadius: 4
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#9ca3af", font: { size: 10, family: "Plus Jakarta Sans" } }
                }
            },
            scales: {
                x: {
                    ticks: { color: "#9ca3af", font: { size: 10 } },
                    grid: { display: false }
                },
                y: {
                    max: 100,
                    ticks: { color: "#6b7280", callback: v => v + "%" },
                    grid: { color: "rgba(255, 255, 255, 0.05)" }
                }
            }
        }
    });
}

// -------------------------------------------------------------
// 3. Intern Cohort Directory & Deep Dive
// -------------------------------------------------------------
let allInternsList = [];

function initInternsDirectory() {
    const listContainer = document.getElementById("internsList");
    const countBadge = document.getElementById("internsCount");
    const searchInput = document.getElementById("internSearchInput");
    const domainFilter = document.getElementById("internDomainFilter");
    const severityFilter = document.getElementById("internSeverityFilter");

    function fetchAndRenderInterns() {
        const dVal = domainFilter.value;
        const sVal = severityFilter.value;
        const qVal = searchInput.value;

        const params = new URLSearchParams({
            domain: dVal,
            severity: sVal,
            q: qVal
        });

        fetch(`/api/interns?${params.toString()}`)
            .then(res => res.json())
            .then(data => {
                if (!data.success) return;
                allInternsList = data.interns;
                countBadge.textContent = data.count;
                renderInternsList(allInternsList);
            });
    }

    searchInput.addEventListener("input", debounce(fetchAndRenderInterns, 250));
    domainFilter.addEventListener("change", fetchAndRenderInterns);
    severityFilter.addEventListener("change", fetchAndRenderInterns);

    fetchAndRenderInterns();
}

function renderInternsList(interns) {
    const listContainer = document.getElementById("internsList");
    listContainer.innerHTML = "";

    if (interns.length === 0) {
        listContainer.innerHTML = `<div style="padding: 20px; text-align: center; color: var(--text-muted);">No interns match filters.</div>`;
        return;
    }

    interns.forEach((intern, idx) => {
        const item = document.createElement("div");
        item.className = "intern-item";
        if (idx === 0) item.classList.add("active");

        const scoreClass = intern.readiness_percentage >= 75 ? "high" : (intern.readiness_percentage >= 50 ? "moderate" : "low");

        item.innerHTML = `
            <div class="intern-item-top">
                <span class="intern-item-name">${intern.name}</span>
                <span class="badge-score ${scoreClass}">${intern.readiness_percentage}%</span>
            </div>
            <div class="intern-item-role">${intern.target_role}</div>
        `;

        item.addEventListener("click", () => {
            document.querySelectorAll(".intern-item").forEach(el => el.classList.remove("active"));
            item.classList.add("active");
            loadInternDetails(intern.intern_id);
        });

        listContainer.appendChild(item);
    });

    if (interns.length > 0) {
        loadInternDetails(interns[0].intern_id);
    }
}

function loadInternDetails(internId) {
    fetch(`/api/intern/${internId}`)
        .then(res => res.json())
        .then(data => {
            if (!data.success) return;
            renderInternDetailPane(data.profile, data.analysis, data.roadmap);
        });
}

function renderInternDetailPane(profile, analysis, roadmap) {
    const emptyState = document.getElementById("detailEmptyState");
    const detailContent = document.getElementById("detailContent");

    emptyState.style.display = "none";
    detailContent.style.display = "block";

    const scoreColor = analysis.readiness_percentage >= 75 ? "var(--emerald)" : (analysis.readiness_percentage >= 50 ? "var(--amber)" : "var(--rose)");

    // Matched Badges
    const matchedHtml = analysis.matched_skills.map(s => 
        `<span class="badge-skill acquired"><i class="fa-solid fa-check"></i> ${s.skill}</span>`
    ).join("");

    // Missing Critical Badges
    const criticalHtml = analysis.missing_critical_skills.map(s => 
        `<span class="badge-skill critical"><i class="fa-solid fa-triangle-exclamation"></i> ${s.skill} (${s.market_demand_weight}%)</span>`
    ).join("");

    // Missing Secondary Badges
    const secondaryHtml = analysis.missing_secondary_skills.map(s => 
        `<span class="badge-skill secondary"><i class="fa-regular fa-circle-dot"></i> ${s.skill}</span>`
    ).join("");

    // Phased Roadmap Steps
    const p1 = roadmap.phase_1_core_foundations;
    const p2 = roadmap.phase_2_specialization;
    const p3 = roadmap.phase_3_capstone;

    detailContent.innerHTML = `
        <div class="profile-hero">
            <div class="profile-title">
                <h2>${profile.name}</h2>
                <div class="profile-role-tag"><i class="fa-solid fa-bullseye"></i> ${profile.target_role} (${profile.target_domain})</div>
                <div class="profile-meta">
                    <span><i class="fa-solid fa-graduation-cap"></i> ${profile.education}</span>
                    <span><i class="fa-solid fa-star"></i> GPA: ${profile.gpa}</span>
                    <span><i class="fa-solid fa-fingerprint"></i> ID: ${profile.intern_id}</span>
                </div>
            </div>
            <div class="gauge-block">
                <div class="gauge-score" style="color: ${scoreColor}">${analysis.readiness_percentage}%</div>
                <div class="gauge-label">Industry Readiness Score</div>
                <div style="font-size: 11px; color: var(--cyan); margin-top: 2px;">Cosine Sim: ${analysis.cosine_similarity}</div>
            </div>
        </div>

        <div class="skills-comparison-grid">
            <div class="skill-list-card matched">
                <h4><i class="fa-solid fa-circle-check"></i> Acquired Skills (${analysis.matched_skills.length})</h4>
                <div class="skill-badges-flow">${matchedHtml || '<span style="color: var(--text-muted); font-size: 12px;">No skills mapped</span>'}</div>
            </div>
            <div class="skill-list-card missing">
                <h4><i class="fa-solid fa-circle-exclamation"></i> High-Demand Missing Skills (${analysis.missing_critical_skills.length})</h4>
                <div class="skill-badges-flow">${criticalHtml || '<span style="color: var(--emerald); font-size: 12px;">No critical gaps!</span>'}</div>
            </div>
        </div>

        ${analysis.missing_secondary_skills.length > 0 ? `
            <div style="margin-bottom: 20px;">
                <span style="font-size: 11px; color: var(--text-muted); font-weight: 600; text-transform: uppercase;">Secondary / Emerging Tools to Explore:</span>
                <div class="skill-badges-flow" style="margin-top: 6px;">${secondaryHtml}</div>
            </div>
        ` : ''}

        <div class="roadmap-box">
            <div class="roadmap-header">
                <h4><i class="fa-solid fa-route"></i> Personalized Upskilling Roadmap</h4>
                <span class="card-tag"><i class="fa-regular fa-clock"></i> Est. Total Duration: ${roadmap.total_estimated_weeks} Weeks</span>
            </div>
            <div class="timeline">
                <div class="timeline-step">
                    <div class="step-phase">${p1.phase_title} (${p1.duration})</div>
                    <div class="step-title">${p1.recommendations.map(r => r.course_name).join(" • ") || "Foundation Refresh"}</div>
                    <div class="step-desc">Focused on bridging primary technical deficiencies through hands-on project labs.</div>
                </div>
                ${p2.recommendations && p2.recommendations.length > 0 ? `
                <div class="timeline-step">
                    <div class="step-phase">${p2.phase_title} (${p2.duration})</div>
                    <div class="step-title">${p2.recommendations.map(r => r.course_name).join(" • ")}</div>
                    <div class="step-desc">Advanced framework mastery and tooling workflow integration.</div>
                </div>
                ` : ''}
                <div class="timeline-step">
                    <div class="step-phase">${p3.phase_title}</div>
                    <div class="step-title">${p3.project_details.title}</div>
                    <div class="step-desc">${p3.project_details.description}</div>
                </div>
            </div>
        </div>
    `;
}

// -------------------------------------------------------------
// 4. Custom Profile / Resume Live Analyzer
// -------------------------------------------------------------
function initCustomAnalyzer() {
    const form = document.getElementById("customAnalyzeForm");
    const roleInput = document.getElementById("customRole");
    const domainSelect = document.getElementById("customDomain");
    const skillsInput = document.getElementById("customSkills");
    const resultPane = document.getElementById("customResultContent");
    const emptyState = document.getElementById("customEmptyState");
    const submitBtn = document.getElementById("btnRunAnalysis");

    // Presets
    document.querySelectorAll(".preset-btn").forEach(btn => {
        btn.addEventListener("click", () => {
            const p = btn.getAttribute("data-preset");
            if (p === "ds") {
                roleInput.value = "Data Scientist";
                domainSelect.value = "Data Science & Analytics";
                skillsInput.value = "Python, Pandas, NumPy, SQL, Exploratory Data Analysis, Git";
            } else if (p === "web") {
                roleInput.value = "Frontend React Developer";
                domainSelect.value = "Full Stack & Web Development";
                skillsInput.value = "HTML5, CSS3, JavaScript, Git, Basic React";
            } else if (p === "cloud") {
                roleInput.value = "DevOps Engineer";
                domainSelect.value = "Cloud Computing & DevOps";
                skillsInput.value = "Linux, Git, Bash Scripting, Basic Docker";
            }
        });
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const role = roleInput.value.trim();
        const domain = domainSelect.value;
        const skillsText = skillsInput.value.trim();

        if (!skillsText) {
            alert("Please provide candidate skills text.");
            return;
        }

        submitBtn.disabled = true;
        submitBtn.innerHTML = `<i class="fa-solid fa-spinner fa-spin"></i> Analyzing with NLP...`;

        fetch("/api/analyze-custom", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                target_role: role,
                target_domain: domain,
                skills_text: skillsText
            })
        })
        .then(res => res.json())
        .then(data => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="fa-solid fa-microchip"></i> Run NLP Skill Gap Analysis`;

            if (!data.success) {
                alert(data.error || "Analysis failed");
                return;
            }

            renderCustomResult(data.analysis, data.roadmap);
        })
        .catch(err => {
            submitBtn.disabled = false;
            submitBtn.innerHTML = `<i class="fa-solid fa-microchip"></i> Run NLP Skill Gap Analysis`;
            console.error("Custom analysis error:", err);
        });
    });
}

function renderCustomResult(analysis, roadmap) {
    const emptyState = document.getElementById("customEmptyState");
    const resultPane = document.getElementById("customResultContent");

    emptyState.style.display = "none";
    resultPane.style.display = "block";

    const scoreColor = analysis.readiness_percentage >= 75 ? "var(--emerald)" : (analysis.readiness_percentage >= 50 ? "var(--amber)" : "var(--rose)");

    const matchedHtml = analysis.matched_skills.map(s => 
        `<span class="badge-skill acquired"><i class="fa-solid fa-check"></i> ${s.skill}</span>`
    ).join("");

    const criticalHtml = analysis.missing_critical_skills.map(s => 
        `<span class="badge-skill critical"><i class="fa-solid fa-triangle-exclamation"></i> ${s.skill} (${s.market_demand_weight}%)</span>`
    ).join("");

    resultPane.innerHTML = `
        <div class="profile-hero" style="margin-bottom: 16px; padding-bottom: 16px;">
            <div>
                <h3 style="font-family: var(--font-heading); font-size: 20px;">NLP Analysis Results</h3>
                <div class="profile-role-tag"><i class="fa-solid fa-layer-group"></i> ${analysis.target_domain} • ${analysis.target_role}</div>
                <div style="font-size: 12px; color: var(--text-muted);">
                    <i class="fa-solid fa-circle-info"></i> Severity: <strong>${analysis.gap_severity}</strong>
                </div>
            </div>
            <div class="gauge-block">
                <div class="gauge-score" style="color: ${scoreColor}">${analysis.readiness_percentage}%</div>
                <div class="gauge-label">Readiness Score</div>
                <div style="font-size: 11px; color: var(--cyan); margin-top: 2px;">Cosine Sim: ${analysis.cosine_similarity}</div>
            </div>
        </div>

        <div class="skills-comparison-grid" style="margin-bottom: 16px;">
            <div class="skill-list-card matched">
                <h4><i class="fa-solid fa-circle-check"></i> Detected Strengths (${analysis.matched_skills.length})</h4>
                <div class="skill-badges-flow">${matchedHtml || '<span style="color: var(--text-muted); font-size: 12px;">No skills matched</span>'}</div>
            </div>
            <div class="skill-list-card missing">
                <h4><i class="fa-solid fa-circle-exclamation"></i> Primary Missing Skills (${analysis.missing_critical_skills.length})</h4>
                <div class="skill-badges-flow">${criticalHtml || '<span style="color: var(--emerald); font-size: 12px;">Profile fully aligned!</span>'}</div>
            </div>
        </div>

        <div class="roadmap-box">
            <div class="roadmap-header">
                <h4><i class="fa-solid fa-graduation-cap"></i> Recommended Upskilling Modules</h4>
                <span class="card-tag">${roadmap.total_estimated_weeks} Weeks Plan</span>
            </div>
            <div style="display: flex; flex-direction: column; gap: 10px; margin-top: 10px;">
                ${roadmap.all_recommendations.slice(0, 4).map(r => `
                    <div style="background: rgba(255, 255, 255, 0.03); border: 1px solid var(--border-color); border-radius: var(--radius-sm); padding: 10px 14px;">
                        <div style="display: flex; justify-content: space-between; align-items: center;">
                            <strong style="font-size: 13px; color: #e2e8f0;">${r.course_name}</strong>
                            <span style="font-size: 11px; color: var(--cyan);">${r.duration_weeks} wks • ${r.platform}</span>
                        </div>
                        <p style="font-size: 11px; color: var(--text-secondary); margin-top: 4px;">🎯 <strong>Hands-on Project:</strong> ${r.project_task}</p>
                    </div>
                `).join('')}
            </div>
        </div>
    `;
}

// Utility debounce helper
function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}
