# Intern Skill Gap Analysis & Industry Demand Alignment

An end-to-end Machine Learning and Natural Language Processing (**TF-IDF + K-Means Clustering**) system built to analyze intern skill sets, compare them against industry job demands, quantify readiness gaps, and generate personalized upskilling roadmaps.

---

## 🌟 Key Features

1. **Synthetic & Realistic Multi-Domain Datasets**:
   - `job_postings.csv`: 550 industry postings across 6 tech domains.
   - `intern_skills.csv`: 160 intern profiles with target career paths.
   - `training_catalog.csv`: 50+ curated courses, project labs, and certifications.
2. **NLP Text Preprocessing & TF-IDF Vectorization**:
   - Preserves compound technical terms (e.g., `scikit-learn`, `ci/cd`, `deep_learning`, `node.js`).
   - Sublinear term frequency scaling and bi-gram n-grams $(1, 2)$.
3. **K-Means Clustering ($K=6$)**:
   - Unsupervised grouping of job postings into natural industry domains.
   - Computes cluster centroids and extracts top characteristic TF-IDF keywords.
4. **Skill Gap Quantification & Cosine Similarity**:
   - Computes vector Cosine Similarity against domain centroids.
   - Categorizes skills into **Acquired Strengths**, **Critical High-Demand Gaps**, and **Secondary Gaps**.
   - Computes an overall **Job Readiness Score ($0-100\%$)**.
5. **Personalized Upskilling Recommender**:
   - Automatically maps missing skills to step-by-step multi-week learning roadmaps.
6. **Interactive Glassmorphism Web App (`app.py`)**:
   - Live cluster scatter visualization (PCA 2D projection).
   - Cohort search, domain filtering, and deep-dive drawer.
   - Real-time custom resume & skill set analyzer.

---

## 📐 Mathematical Formulation

### 1. Vector Cosine Similarity
$$\text{Cosine Similarity}(\vec{v}_{\text{intern}}, \vec{v}_{\text{domain}}) = \frac{\vec{v}_{\text{intern}} \cdot \vec{v}_{\text{domain}}}{\|\vec{v}_{\text{intern}}\| \|\vec{v}_{\text{domain}}\|}$$

### 2. Composite Job Readiness Score
$$\text{Readiness Score} = \left( 0.40 \times \text{Cosine Sim} + 0.60 \times \frac{|\text{Matched Skills}|}{|\text{Total Critical Skills}|} \right) \times 100$$

---

## 📂 Project Structure

```
d:/Internee.pk/Task 5/
├── data/
│   ├── intern_skills.csv          # 160 intern profiles
│   ├── job_postings.csv           # 550 industry job postings
│   └── training_catalog.csv       # Curated upskilling courses & projects
├── src/
│   ├── data_generator.py          # Generates realistic datasets
│   ├── preprocessor.py            # NLP cleaning & tech term preservation
│   ├── nlp_clustering.py          # TF-IDF & K-Means clustering model
│   ├── skill_gap_analyzer.py      # Cosine similarity & gap quantification
│   ├── recommender.py             # Phased roadmap & training recommender
│   └── visualizer.py              # Generates charts and PCA 2D figures
├── static/
│   ├── css/style.css              # Dark mode glassmorphism UI styles
│   └── js/app.js                  # Frontend Chart.js and search logic
├── templates/
│   └── index.html                 # Main dashboard template
├── notebooks/
│   └── skill_gap_analysis.ipynb   # Complete documented submission notebook
├── reports/
│   ├── figures/                   # Generated PNG plots
│   ├── analysis_summary.json      # Metric statistics & cluster profiles
│   ├── analyzed_interns_summary.csv
│   └── cluster_model.joblib       # Serialized model artifact
├── app.py                         # Interactive Flask Web Server
├── main.py                        # Complete CLI Pipeline runner
├── requirements.txt
└── README.md
```

---

## 🚀 How to Run

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Run Full End-to-End Pipeline & Generate Reports
```bash
python main.py
```

### 3. Launch Interactive Web Dashboard
```bash
python app.py
```
Open your browser and navigate to `http://localhost:5000`.

---

## 📊 Summary Metrics

- **Job Postings Analyzed:** 550
- **Intern Profiles Evaluated:** 160
- **Optimal Clusters:** 6
- **Average Silhouette Score:** 0.2050
- **Cohort Average Readiness Score:** 41.4%
- **Cohort Average Cosine Similarity:** 0.3669
