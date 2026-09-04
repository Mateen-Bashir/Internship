import React, { useState, useEffect } from 'react';
import { 
  GraduationCap, 
  Sparkles, 
  Compass, 
  BarChart3, 
  BookOpen, 
  Clock, 
  Layers, 
  CheckCircle2, 
  ArrowRight, 
  Search, 
  Filter, 
  User, 
  Cpu, 
  Database, 
  Globe, 
  Smartphone, 
  Cloud, 
  ShieldCheck,
  Star
} from 'lucide-react';

const API_BASE = window.location.origin.includes(':5173') 
  ? 'http://127.0.0.1:8000/api' 
  : '/api';

export default function App() {
  const [activeTab, setActiveTab] = useState('intern'); // 'intern' | 'coldstart' | 'analytics' | 'catalog'
  
  // Data states
  const [interns, setInterns] = useState([]);
  const [selectedInternId, setSelectedInternId] = useState('INT_0006');
  const [searchIntern, setSearchIntern] = useState('');
  const [trackFilter, setTrackFilter] = useState('All');
  const [topN, setTopN] = useState(6);
  
  // Recommendation state
  const [roadmap, setRoadmap] = useState(null);
  const [loadingRoadmap, setLoadingRoadmap] = useState(false);
  
  // Cold Start state
  const [coldTrack, setColdTrack] = useState('AI & Machine Learning');
  const [coldLevel, setColdLevel] = useState('Beginner');
  const [coldTopN, setColdTopN] = useState(6);
  const [coldRoadmap, setColdRoadmap] = useState(null);
  
  // Metrics & Courses
  const [metricsData, setMetricsData] = useState(null);
  const [courses, setCourses] = useState([]);
  const [courseDomainFilter, setCourseDomainFilter] = useState('All');
  
  // History Modal
  const [showHistoryModal, setShowHistoryModal] = useState(false);

  // Initial Data Load
  useEffect(() => {
    fetch(`${API_BASE}/interns`)
      .then(res => res.json())
      .then(data => {
        if (Array.isArray(data) && data.length > 0) {
          setInterns(data);
          setSelectedInternId(data[0].intern_id);
        }
      })
      .catch(err => {
        console.warn("Using fallback initial interns...", err);
      });

    fetch(`${API_BASE}/metrics`)
      .then(res => res.json())
      .then(data => setMetricsData(data))
      .catch(err => console.warn("Metrics load fallback", err));

    fetch(`${API_BASE}/courses`)
      .then(res => res.json())
      .then(data => setCourses(data))
      .catch(err => console.warn("Courses load fallback", err));
  }, []);

  // Fetch recommendation when selected intern changes
  useEffect(() => {
    if (!selectedInternId) return;
    setLoadingRoadmap(true);
    fetch(`${API_BASE}/recommend/${selectedInternId}?top_n=${topN}`)
      .then(res => res.json())
      .then(data => {
        setRoadmap(data);
        setLoadingRoadmap(false);
      })
      .catch(err => {
        console.error("Error loading roadmap:", err);
        setLoadingRoadmap(false);
      });
  }, [selectedInternId, topN]);

  // Handle Cold-Start Generation
  useEffect(() => {
    fetch(`${API_BASE}/cold-start`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        target_track: coldTrack,
        skill_level: coldLevel,
        top_n: coldTopN
      })
    })
      .then(res => res.json())
      .then(data => setColdRoadmap(data))
      .catch(err => console.error("Error cold start:", err));
  }, [coldTrack, coldLevel, coldTopN]);

  const filteredInterns = interns.filter(i => {
    const matchSearch = (i.name || '').toLowerCase().includes(searchIntern.toLowerCase()) || 
                        (i.intern_id || '').toLowerCase().includes(searchIntern.toLowerCase());
    const matchTrack = trackFilter === 'All' || i.primary_track === trackFilter;
    return matchSearch && matchTrack;
  });

  const getDomainIcon = (domain) => {
    switch (domain) {
      case 'AI & Machine Learning': return <Cpu size={16} color="#818cf8" />;
      case 'Data Science & Analytics': return <Database size={16} color="#38bdf8" />;
      case 'Full-Stack Web Development': return <Globe size={16} color="#34d399" />;
      case 'Mobile Application Development': return <Smartphone size={16} color="#fbbf24" />;
      case 'Cloud Computing & DevOps': return <Cloud size={16} color="#f87171" />;
      case 'Cybersecurity & Ethical Hacking': return <ShieldCheck size={16} color="#c084fc" />;
      default: return <BookOpen size={16} color="#94a3b8" />;
    }
  };

  const getDifficultyBadge = (level) => {
    const cls = level === 'Beginner' ? 'badge-beginner' : (level === 'Intermediate' ? 'badge-intermediate' : 'badge-advanced');
    return <span className={`badge-tier ${cls}`}>{level}</span>;
  };

  return (
    <div>
      {/* ----------------- NAVBAR ----------------- */}
      <header className="navbar-header">
        <div className="navbar-container">
          <div className="brand-section">
            <div className="brand-icon">
              <GraduationCap size={24} />
            </div>
            <div>
              <div className="brand-title-wrap">
                <span className="brand-title">LearnPath AI</span>
                <span className="brand-tag">ML Recommender</span>
              </div>
              <p className="brand-subtitle">Personalized Adaptive Learning Path Engine (SVD Matrix Factorization)</p>
            </div>
          </div>

          {/* Navigation Tabs */}
          <nav className="nav-tab-list">
            <button
              onClick={() => setActiveTab('intern')}
              className={`nav-tab-btn ${activeTab === 'intern' ? 'active' : ''}`}
            >
              <Sparkles size={16} />
              <span>Intern Roadmap</span>
            </button>

            <button
              onClick={() => setActiveTab('coldstart')}
              className={`nav-tab-btn ${activeTab === 'coldstart' ? 'active' : ''}`}
            >
              <Compass size={16} />
              <span>Cold-Start Builder</span>
            </button>

            <button
              onClick={() => setActiveTab('analytics')}
              className={`nav-tab-btn ${activeTab === 'analytics' ? 'active' : ''}`}
            >
              <BarChart3 size={16} />
              <span>ML Analytics</span>
            </button>

            <button
              onClick={() => setActiveTab('catalog')}
              className={`nav-tab-btn ${activeTab === 'catalog' ? 'active' : ''}`}
            >
              <BookOpen size={16} />
              <span>Course Catalog</span>
            </button>
          </nav>
        </div>
      </header>

      {/* ----------------- MAIN WRAPPER ----------------- */}
      <main className="main-wrapper">
        
        {/* ======================================================== */}
        {/* TAB 1: INTERN PERSONALIZED ROADMAP                       */}
        {/* ======================================================== */}
        {activeTab === 'intern' && (
          <div>
            {/* Control Panel Bar */}
            <div className="glass-box">
              <div className="control-grid">
                <div>
                  <label className="form-label">
                    Select Intern Profile ({filteredInterns.length} available)
                  </label>
                  <select
                    value={selectedInternId}
                    onChange={(e) => setSelectedInternId(e.target.value)}
                    className="input-control"
                  >
                    {filteredInterns.map(i => (
                      <option key={i.intern_id} value={i.intern_id}>
                        {i.intern_id} — {i.name} ({i.primary_track})
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="form-label">Filter by Domain Track</label>
                  <select
                    value={trackFilter}
                    onChange={(e) => setTrackFilter(e.target.value)}
                    className="input-control"
                  >
                    <option value="All">All Tracks (6 Domains)</option>
                    <option value="AI & Machine Learning">AI & Machine Learning</option>
                    <option value="Data Science & Analytics">Data Science & Analytics</option>
                    <option value="Full-Stack Web Development">Full-Stack Web Development</option>
                    <option value="Mobile Application Development">Mobile App Development</option>
                    <option value="Cloud Computing & DevOps">Cloud Computing & DevOps</option>
                    <option value="Cybersecurity & Ethical Hacking">Cybersecurity</option>
                  </select>
                </div>

                <div>
                  <label className="form-label">Search Intern Name / ID</label>
                  <input
                    type="text"
                    value={searchIntern}
                    onChange={(e) => setSearchIntern(e.target.value)}
                    placeholder="Search e.g. Iqra, INT_0012..."
                    className="input-control"
                  />
                </div>

                <div>
                  <label className="form-label">
                    Path Length: <span style={{ color: 'var(--cyan)' }}>{topN} Modules</span>
                  </label>
                  <input
                    type="range"
                    min="4"
                    max="10"
                    value={topN}
                    onChange={(e) => setTopN(parseInt(e.target.value))}
                    style={{ width: '100%', accentColor: 'var(--primary)', cursor: 'pointer' }}
                  />
                </div>
              </div>
            </div>

            {/* Profile Hero Card */}
            {roadmap && roadmap.intern_profile && (
              <div className="glass-box">
                <div className="profile-hero">
                  <div className="profile-identity">
                    <div className="avatar-badge">
                      {roadmap.intern_profile.name.charAt(0)}
                    </div>
                    <div>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.6rem' }}>
                        <h2 className="profile-name">{roadmap.intern_profile.name}</h2>
                        <span style={{ fontSize: '0.75rem', background: '#1e293b', color: '#94a3b8', padding: '2px 8px', borderRadius: '4px', fontFamily: 'monospace' }}>
                          {roadmap.intern_profile.intern_id}
                        </span>
                      </div>
                      <div className="profile-meta-row">
                        <span style={{ display: 'flex', alignItems: 'center', gap: '0.35rem', color: 'var(--cyan)', fontWeight: 'bold' }}>
                          {getDomainIcon(roadmap.intern_profile.primary_track)}
                          {roadmap.intern_profile.primary_track}
                        </span>
                        <span>•</span>
                        <span>Experience: <strong style={{ color: '#fff' }}>{roadmap.intern_profile.experience_level}</strong></span>
                        <span>•</span>
                        <span>Pace: <strong style={{ color: '#fff' }}>{roadmap.intern_profile.learning_pace}</strong></span>
                      </div>
                    </div>
                  </div>

                  <button
                    onClick={() => setShowHistoryModal(true)}
                    className="history-btn"
                  >
                    <CheckCircle2 size={16} color="#34d399" />
                    <span>Completed History ({roadmap.completed_modules_count} Modules)</span>
                  </button>
                </div>

                {/* KPI Ribbon */}
                <div className="kpi-row">
                  <div className="kpi-box">
                    <div className="kpi-value" style={{ color: 'var(--primary)' }}>{roadmap.total_modules}</div>
                    <div className="kpi-label">Recommended Modules</div>
                  </div>
                  <div className="kpi-box">
                    <div className="kpi-value" style={{ color: 'var(--cyan)' }}>{roadmap.total_duration_hours} hrs</div>
                    <div className="kpi-label">Estimated Time</div>
                  </div>
                  <div className="kpi-box">
                    <div className="kpi-value" style={{ color: 'var(--emerald)' }}>{roadmap.skills_covered_count}</div>
                    <div className="kpi-label">Target Skills</div>
                  </div>
                  <div className="kpi-box">
                    <div className="kpi-value" style={{ color: 'var(--amber)' }}>
                      {(roadmap.sequential_modules.reduce((acc, m) => acc + m.predicted_rating, 0) / (roadmap.sequential_modules.length || 1)).toFixed(2)} / 5.0
                    </div>
                    <div className="kpi-label">Avg SVD Affinity</div>
                  </div>
                </div>
              </div>
            )}

            {/* Milestones Sections */}
            {loadingRoadmap && (
              <div style={{ padding: '3rem', textAlign: 'center', color: '#94a3b8' }}>
                <p>Computing SVD Matrix Factorization & Prerequisite DAG...</p>
              </div>
            )}

            {!loadingRoadmap && roadmap && roadmap.milestones && (
              <div>
                {Object.entries(roadmap.milestones).map(([milestoneTitle, modules]) => (
                  <div key={milestoneTitle} className="milestone-group">
                    <div className="milestone-banner">
                      <h3 className="milestone-title">{milestoneTitle}</h3>
                      <span className="milestone-badge">{modules.length} Modules</span>
                    </div>

                    <div className="cards-grid">
                      {modules.map((module) => (
                        <div key={module.module_id} className="course-card">
                          <div>
                            <div className="card-top">
                              <div className="step-code-wrap">
                                <span className="step-number">{module.step_order}</span>
                                <span className="course-code">{module.module_id}</span>
                              </div>
                              <div style={{ display: 'flex', alignItems: 'center', gap: '0.4rem' }}>
                                {getDifficultyBadge(module.difficulty_level)}
                                <span className="svd-score-badge">
                                  <Star size={12} fill="#818cf8" color="#818cf8" />
                                  {module.predicted_rating}
                                </span>
                              </div>
                            </div>

                            <h4 className="course-name">{module.title}</h4>
                            <p className="course-desc">{module.description}</p>

                            <div className="skills-container">
                              {module.skills.map((skill, sIdx) => (
                                <span key={sIdx} className="skill-pill">{skill}</span>
                              ))}
                            </div>
                          </div>

                          <div className="card-bottom">
                            <span style={{ display: 'flex', alignItems: 'center', gap: '0.3rem', color: '#94a3b8' }}>
                              <Clock size={13} color="#64748b" />
                              {module.duration_hours} hrs
                            </span>

                            <div>
                              {module.prerequisites && module.prerequisites.length > 0 ? (
                                <span className="prereq-badge">
                                  ⛓️ Prereq: {module.prerequisites.join(', ')}
                                </span>
                              ) : (
                                <span className="direct-entry-badge">
                                  ✓ Direct Entry
                                </span>
                              )}
                            </div>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 2: COLD-START PATHWAY BUILDER                        */}
        {/* ======================================================== */}
        {activeTab === 'coldstart' && (
          <div>
            <div className="glass-box">
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Onboarding System
              </span>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-display)', marginTop: '0.25rem' }}>
                Cold-Start Learning Path Generator
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                Generates a verified curriculum for new interns joining without past rating history using Track DAGs and Heuristic Difficulty Progression.
              </p>

              <div className="control-grid" style={{ marginTop: '1.5rem', paddingTop: '1.25rem', borderTop: '1px solid var(--border-subtle)' }}>
                <div>
                  <label className="form-label">1. Desired Career Track</label>
                  <select
                    value={coldTrack}
                    onChange={(e) => setColdTrack(e.target.value)}
                    className="input-control"
                  >
                    <option value="AI & Machine Learning">AI & Machine Learning</option>
                    <option value="Data Science & Analytics">Data Science & Analytics</option>
                    <option value="Full-Stack Web Development">Full-Stack Web Development</option>
                    <option value="Mobile Application Development">Mobile App Development</option>
                    <option value="Cloud Computing & DevOps">Cloud Computing & DevOps</option>
                    <option value="Cybersecurity & Ethical Hacking">Cybersecurity & Ethical Hacking</option>
                  </select>
                </div>

                <div>
                  <label className="form-label">2. Current Experience Baseline</label>
                  <select
                    value={coldLevel}
                    onChange={(e) => setColdLevel(e.target.value)}
                    className="input-control"
                  >
                    <option value="Beginner">Beginner (Foundations)</option>
                    <option value="Intermediate">Intermediate (Core Practitioner)</option>
                    <option value="Advanced">Advanced (Specialist)</option>
                  </select>
                </div>

                <div>
                  <label className="form-label">3. Modules in Roadmap: {coldTopN}</label>
                  <input
                    type="range"
                    min="4"
                    max="8"
                    value={coldTopN}
                    onChange={(e) => setColdTopN(parseInt(e.target.value))}
                    style={{ width: '100%', accentColor: 'var(--cyan)', cursor: 'pointer' }}
                  />
                </div>
              </div>
            </div>

            {coldRoadmap && coldRoadmap.milestones && (
              <div>
                {Object.entries(coldRoadmap.milestones).map(([milestoneTitle, modules]) => (
                  <div key={milestoneTitle} className="milestone-group">
                    <div className="milestone-banner" style={{ borderLeftColor: 'var(--cyan)' }}>
                      <h3 className="milestone-title">{milestoneTitle}</h3>
                      <span className="milestone-badge" style={{ color: 'var(--cyan)' }}>{modules.length} Modules</span>
                    </div>

                    <div className="cards-grid">
                      {modules.map((m) => (
                        <div key={m.module_id} className="course-card">
                          <div>
                            <div className="card-top">
                              <span className="course-code">STEP {m.step_order} • {m.module_id}</span>
                              {getDifficultyBadge(m.difficulty_level)}
                            </div>
                            <h4 className="course-name">{m.title}</h4>
                            <p className="course-desc">{m.description}</p>
                            <div className="skills-container">
                              {m.skills.map((s, idx) => (
                                <span key={idx} className="skill-pill">{s}</span>
                              ))}
                            </div>
                          </div>
                          <div className="card-bottom">
                            <span style={{ color: '#94a3b8' }}>⏱️ {m.duration_hours} hrs</span>
                            <span>
                              {m.prerequisites && m.prerequisites.length > 0 ? (
                                <span className="prereq-badge">⛓️ {m.prerequisites.join(', ')}</span>
                              ) : (
                                <span className="direct-entry-badge">✓ Direct Entry</span>
                              )}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 3: ML PERFORMANCE & LATENT SPACE ANALYTICS           */}
        {/* ======================================================== */}
        {activeTab === 'analytics' && metricsData && (
          <div>
            <div className="glass-box">
              <span style={{ fontSize: '0.75rem', fontWeight: 800, color: 'var(--primary)', textTransform: 'uppercase', letterSpacing: '1px' }}>
                Performance Evaluation
              </span>
              <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-display)', marginTop: '0.25rem' }}>
                SVD Matrix Factorization vs NMF Baseline
              </h2>
              <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                Quantitative benchmarks on a held-out 20% test split across 600 interns and 10,800+ rating interactions.
              </p>

              <div className="kpi-row">
                <div className="kpi-box">
                  <div className="kpi-value" style={{ color: 'var(--primary)' }}>
                    {metricsData.benchmarks['SVD (Proposed)']['RMSE']}
                  </div>
                  <div className="kpi-label">SVD RMSE (Error)</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--emerald)', marginTop: '4px' }}>70.1% Lower vs Baseline</div>
                </div>

                <div className="kpi-box">
                  <div className="kpi-value" style={{ color: 'var(--cyan)' }}>
                    {metricsData.benchmarks['SVD (Proposed)']['MAE']}
                  </div>
                  <div className="kpi-label">SVD MAE</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--emerald)', marginTop: '4px' }}>Mean Absolute Error</div>
                </div>

                <div className="kpi-box">
                  <div className="kpi-value" style={{ color: 'var(--emerald)' }}>
                    {(metricsData.benchmarks['SVD (Proposed)']['Recall@5'] * 100).toFixed(1)}%
                  </div>
                  <div className="kpi-label">Recall@5</div>
                  <div style={{ fontSize: '0.7rem', color: '#94a3b8', marginTop: '4px' }}>Top-5 Relevant Coverage</div>
                </div>

                <div className="kpi-box">
                  <div className="kpi-value" style={{ color: 'var(--purple)' }}>
                    {metricsData.benchmarks['SVD (Proposed)']['NDCG@5']}
                  </div>
                  <div className="kpi-label">NDCG@5 (Ranking)</div>
                  <div style={{ fontSize: '0.7rem', color: 'var(--purple)', marginTop: '4px' }}>High Ranking Quality</div>
                </div>
              </div>

              <div className="table-wrapper">
                <table className="styled-table">
                  <thead>
                    <tr>
                      <th>Model Architecture</th>
                      <th>RMSE (↓)</th>
                      <th>MAE (↓)</th>
                      <th>Precision@5 (↑)</th>
                      <th>Recall@5 (↑)</th>
                      <th>NDCG@5 (↑)</th>
                    </tr>
                  </thead>
                  <tbody>
                    <tr style={{ background: 'rgba(99, 102, 241, 0.1)' }}>
                      <td style={{ fontWeight: 'bold', color: '#a5b4fc' }}>
                        ★ SVD Matrix Factorization (Proposed)
                      </td>
                      <td style={{ fontFamily: 'monospace', color: 'var(--emerald)', fontWeight: 'bold' }}>{metricsData.benchmarks['SVD (Proposed)']['RMSE']}</td>
                      <td style={{ fontFamily: 'monospace', color: 'var(--emerald)' }}>{metricsData.benchmarks['SVD (Proposed)']['MAE']}</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['SVD (Proposed)']['Precision@5']}</td>
                      <td style={{ fontFamily: 'monospace', color: 'var(--emerald)', fontWeight: 'bold' }}>{metricsData.benchmarks['SVD (Proposed)']['Recall@5']}</td>
                      <td style={{ fontFamily: 'monospace', color: 'var(--purple)', fontWeight: 'bold' }}>{metricsData.benchmarks['SVD (Proposed)']['NDCG@5']}</td>
                    </tr>
                    <tr style={{ color: '#94a3b8' }}>
                      <td>Non-Negative Matrix Factorization (Baseline NMF)</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['NMF (Baseline)']['RMSE']}</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['NMF (Baseline)']['MAE']}</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['NMF (Baseline)']['Precision@5']}</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['NMF (Baseline)']['Recall@5']}</td>
                      <td style={{ fontFamily: 'monospace' }}>{metricsData.benchmarks['NMF (Baseline)']['NDCG@5']}</td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>

            {/* Latent Space 2D PCA Projections */}
            <div className="glass-box">
              <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-display)' }}>
                🌌 SVD Course Latent Embeddings (PCA 2D Projection)
              </h3>
              <p style={{ fontSize: '0.8rem', color: '#94a3b8', marginTop: '0.25rem', marginBottom: '1rem' }}>
                Shows how SVD automatically clusters similar modules in latent space without supervision.
              </p>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(180px, 1fr))', gap: '0.75rem' }}>
                {metricsData.latent_space.map((p) => (
                  <div 
                    key={p.module_id}
                    style={{ background: 'rgba(15, 23, 42, 0.8)', border: '1px solid var(--border-subtle)', borderRadius: '10px', padding: '0.75rem' }}
                  >
                    <div style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--cyan)', fontSize: '0.8rem' }}>{p.module_id}</div>
                    <div style={{ fontSize: '0.75rem', color: '#cbd5e1', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis', marginTop: '2px' }} title={p.title}>
                      {p.title}
                    </div>
                    <div style={{ fontSize: '0.7rem', color: '#64748b', fontFamily: 'monospace', marginTop: '0.5rem' }}>
                      ({p.x}, {p.y})
                    </div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        )}

        {/* ======================================================== */}
        {/* TAB 4: COURSE & PREREQUISITE CATALOG                     */}
        {/* ======================================================== */}
        {activeTab === 'catalog' && (
          <div>
            <div className="glass-box" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', flexWrap: 'wrap', gap: '1rem' }}>
              <div>
                <h2 style={{ fontSize: '1.5rem', fontWeight: 800, color: '#ffffff', fontFamily: 'var(--font-display)' }}>
                  Course Catalog & Prerequisite Knowledge Graph
                </h2>
                <p style={{ fontSize: '0.85rem', color: '#94a3b8', marginTop: '0.25rem' }}>
                  Curriculum of 37 structured modules across 6 technical domains.
                </p>
              </div>

              <div>
                <select
                  value={courseDomainFilter}
                  onChange={(e) => setCourseDomainFilter(e.target.value)}
                  className="input-control"
                  style={{ width: 'auto', minWidth: '220px' }}
                >
                  <option value="All">All Tracks (6 Domains)</option>
                  <option value="AI & Machine Learning">AI & Machine Learning</option>
                  <option value="Data Science & Analytics">Data Science & Analytics</option>
                  <option value="Full-Stack Web Development">Full-Stack Web Development</option>
                  <option value="Mobile Application Development">Mobile App Development</option>
                  <option value="Cloud Computing & DevOps">Cloud Computing & DevOps</option>
                  <option value="Cybersecurity & Ethical Hacking">Cybersecurity</option>
                </select>
              </div>
            </div>

            <div className="glass-box" style={{ padding: 0, overflow: 'hidden' }}>
              <div className="table-wrapper" style={{ margin: 0, border: 'none' }}>
                <table className="styled-table">
                  <thead>
                    <tr>
                      <th>Code</th>
                      <th>Module Title</th>
                      <th>Domain Track</th>
                      <th>Level</th>
                      <th>Duration</th>
                      <th>Prerequisites</th>
                      <th>Skills Covered</th>
                    </tr>
                  </thead>
                  <tbody>
                    {courses
                      .filter(c => courseDomainFilter === 'All' || c.domain === courseDomainFilter)
                      .map((c) => (
                        <tr key={c.module_id}>
                          <td style={{ fontFamily: 'monospace', fontWeight: 'bold', color: 'var(--cyan)' }}>{c.module_id}</td>
                          <td style={{ fontWeight: 'bold', color: '#ffffff' }}>{c.title}</td>
                          <td style={{ color: '#94a3b8', fontSize: '0.8rem' }}>{c.domain}</td>
                          <td>{getDifficultyBadge(c.difficulty_level)}</td>
                          <td style={{ fontFamily: 'monospace', color: '#94a3b8' }}>{c.duration_hours}h</td>
                          <td>
                            {c.prerequisites && c.prerequisites !== 'None' ? (
                              <span className="prereq-badge">{c.prerequisites}</span>
                            ) : (
                              <span className="direct-entry-badge">None</span>
                            )}
                          </td>
                          <td style={{ color: '#cbd5e1', fontSize: '0.75rem', maxWidth: '280px', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }} title={c.skills}>
                            {c.skills}
                          </td>
                        </tr>
                      ))}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        )}
      </main>

      {/* ----------------- INTERN HISTORY MODAL ----------------- */}
      {showHistoryModal && roadmap && (
        <div className="modal-overlay" onClick={() => setShowHistoryModal(false)}>
          <div className="modal-content" onClick={(e) => e.stopPropagation()}>
            <div className="modal-header">
              <div>
                <h3 style={{ fontSize: '1.15rem', fontWeight: 800, color: '#ffffff' }}>
                  Completed History: {roadmap.intern_profile.name} ({roadmap.intern_profile.intern_id})
                </h3>
                <p style={{ fontSize: '0.75rem', color: '#94a3b8', marginTop: '2px' }}>
                  Track: {roadmap.intern_profile.primary_track} • Total {roadmap.history.length} Course Records
                </p>
              </div>
              <button
                onClick={() => setShowHistoryModal(false)}
                className="modal-close-btn"
              >
                ✕
              </button>
            </div>

            <div style={{ display: 'flex', flexDirection: 'column', gap: '0.5rem' }}>
              {roadmap.history.map((h, idx) => (
                <div 
                  key={idx} 
                  style={{ background: '#1e293b', padding: '0.75rem 1rem', borderRadius: '10px', border: '1px solid var(--border-subtle)', display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}
                >
                  <div>
                    <div style={{ fontFamily: 'monospace', color: 'var(--cyan)', fontWeight: 'bold', fontSize: '0.75rem' }}>{h.module_id}</div>
                    <div style={{ color: '#f8fafc', fontWeight: 600, fontSize: '0.85rem' }}>{h.title}</div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', fontSize: '0.75rem', fontFamily: 'monospace' }}>
                    <span style={{ color: 'var(--amber)' }}>★ {h.rating} / 5.0</span>
                    <span style={{ color: '#94a3b8' }}>{h.completion_percentage}%</span>
                    <span className={h.status === 'Completed' ? 'direct-entry-badge' : 'badge-intermediate'}>
                      {h.status}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
