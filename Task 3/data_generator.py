"""
Data Generator for Personalized Learning Path Recommendation System
Internee.pk - Task 3

Generates:
1. courses_metadata.csv: Curated courses across 6 tech tracks with prerequisite DAGs.
2. intern_profiles.csv: 600+ intern profiles with assigned domain tracks and skill baselines.
3. intern_interactions.csv: 12,000+ realistic ratings (1-5), completion %, and quiz scores.
"""

import os
import random
import numpy as np
import pandas as pd

# Set random seeds for reproducibility
SEED = 42
random.seed(SEED)
np.random.seed(SEED)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)

# ----------------------------------------------------------------------
# 1. CURATED COURSE CATALOG & PREREQUISITE GRAPH
# ----------------------------------------------------------------------
COURSES_DATA = [
    # --- Track 1: AI & Machine Learning ---
    {
        "module_id": "AIML_101",
        "title": "Python for Artificial Intelligence & ML",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 18,
        "skills": "Python, OOP, NumPy, Vectorization",
        "rating_avg": 4.8,
        "description": "Foundational Python programming tailored for data manipulation and AI workflows."
    },
    {
        "module_id": "AIML_102",
        "title": "Linear Algebra & Calculus for ML",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 15,
        "skills": "Matrices, Eigenvalues, Gradient Descent, Derivatives",
        "rating_avg": 4.6,
        "description": "Essential mathematical foundations powering modern machine learning algorithms."
    },
    {
        "module_id": "AIML_201",
        "title": "Supervised & Unsupervised Machine Learning",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Intermediate",
        "prerequisites": ["AIML_101", "AIML_102"],
        "duration_hours": 28,
        "skills": "Scikit-Learn, Regression, Classification, Clustering, PCA",
        "rating_avg": 4.9,
        "description": "End-to-end predictive modeling using classical machine learning algorithms."
    },
    {
        "module_id": "AIML_202",
        "title": "Feature Engineering & Model Validation",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Intermediate",
        "prerequisites": ["AIML_201"],
        "duration_hours": 16,
        "skills": "Cross-Validation, Imputation, Encoders, Hyperparameter Tuning",
        "rating_avg": 4.7,
        "description": "Techniques for preprocessing tabular data and avoiding data leakage."
    },
    {
        "module_id": "AIML_301",
        "title": "Deep Learning & Neural Networks with PyTorch",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Advanced",
        "prerequisites": ["AIML_201"],
        "duration_hours": 35,
        "skills": "PyTorch, Backpropagation, CNN, RNN, Loss Functions",
        "rating_avg": 4.9,
        "description": "Deep neural architecture design, GPU training, and computer vision models."
    },
    {
        "module_id": "AIML_302",
        "title": "Natural Language Processing & Transformers",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Advanced",
        "prerequisites": ["AIML_301"],
        "duration_hours": 30,
        "skills": "Transformers, BERT, Attention Mechanisms, HuggingFace, LLMs",
        "rating_avg": 4.8,
        "description": "Modern sequence modeling, attention mechanisms, and fine-tuning transformer models."
    },
    {
        "module_id": "AIML_303",
        "title": "MLOps: Deploying AI Models to Production",
        "domain": "AI & Machine Learning",
        "difficulty_level": "Advanced",
        "prerequisites": ["AIML_201"],
        "duration_hours": 22,
        "skills": "Docker, MLflow, FastAPI, Model Monitoring, CI/CD for ML",
        "rating_avg": 4.7,
        "description": "Productionizing machine learning models with APIs, artifact tracking, and monitoring."
    },

    # --- Track 2: Data Science & Analytics ---
    {
        "module_id": "DS_101",
        "title": "Data Analysis with Python & Pandas",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 20,
        "skills": "Pandas, NumPy, Data Wrangling, Cleaning",
        "rating_avg": 4.8,
        "description": "Master tabular data structures, aggregations, merges, and data cleaning."
    },
    {
        "module_id": "DS_102",
        "title": "Exploratory Data Analysis & Visualization",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Beginner",
        "prerequisites": ["DS_101"],
        "duration_hours": 14,
        "skills": "Matplotlib, Seaborn, Plotly, Storytelling",
        "rating_avg": 4.7,
        "description": "Visual exploration of distributions, correlations, and executive charting."
    },
    {
        "module_id": "DS_103",
        "title": "SQL for Data Science & Relational Databases",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 16,
        "skills": "SQL, PostgreSQL, Joins, Window Functions, CTEs",
        "rating_avg": 4.9,
        "description": "Complex relational querying, data aggregation, and database design."
    },
    {
        "module_id": "DS_201",
        "title": "Applied Statistical Inference & Hypothesis Testing",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Intermediate",
        "prerequisites": ["DS_101", "DS_103"],
        "duration_hours": 22,
        "skills": "A/B Testing, p-values, Confidence Intervals, ANOVA, SciPy",
        "rating_avg": 4.6,
        "description": "Rigorous statistical analysis for business decision-making and experiment design."
    },
    {
        "module_id": "DS_202",
        "title": "Time Series Analysis & Forecasting",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Intermediate",
        "prerequisites": ["DS_101", "DS_201"],
        "duration_hours": 20,
        "skills": "ARIMA, Prophet, Trend Decomposition, Seasonality",
        "rating_avg": 4.5,
        "description": "Forecasting temporal data such as sales, user traffic, and financial indices."
    },
    {
        "module_id": "DS_301",
        "title": "Big Data Analytics with Apache Spark & PySpark",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Advanced",
        "prerequisites": ["DS_101", "DS_103"],
        "duration_hours": 32,
        "skills": "PySpark, RDDs, Spark SQL, Distributed Computing",
        "rating_avg": 4.8,
        "description": "Distributed data processing pipelines for multi-gigabyte and terabyte datasets."
    },
    {
        "module_id": "DS_302",
        "title": "Interactive BI Dashboards with Power BI & Tableau",
        "domain": "Data Science & Analytics",
        "difficulty_level": "Intermediate",
        "prerequisites": ["DS_103"],
        "duration_hours": 18,
        "skills": "Power BI, DAX, Tableau, KPI Dashboards",
        "rating_avg": 4.7,
        "description": "Designing high-impact stakeholder dashboards and automated KPI tracking."
    },

    # --- Track 3: Full-Stack Web Development ---
    {
        "module_id": "WEB_101",
        "title": "Modern HTML5, Semantic CSS3 & Responsive Design",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 16,
        "skills": "HTML5, CSS3, Flexbox, CSS Grid, Responsive Design",
        "rating_avg": 4.8,
        "description": "Core building blocks of modern, accessible, and responsive user interfaces."
    },
    {
        "module_id": "WEB_102",
        "title": "JavaScript ES6+ & DOM Manipulation",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Beginner",
        "prerequisites": ["WEB_101"],
        "duration_hours": 24,
        "skills": "Async/Await, Promises, Closures, DOM, Fetch API",
        "rating_avg": 4.9,
        "description": "Dynamic web scripting, asynchronous data fetching, and browser events."
    },
    {
        "module_id": "WEB_201",
        "title": "Frontend Development with React.js",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["WEB_102"],
        "duration_hours": 30,
        "skills": "React, Hooks, Component State, Context API, TailwindCSS",
        "rating_avg": 4.9,
        "description": "Single-page application architecture, state management, and component reusability."
    },
    {
        "module_id": "WEB_202",
        "title": "Backend Engineering with Node.js & Express",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["WEB_102"],
        "duration_hours": 26,
        "skills": "Node.js, Express, REST APIs, JWT Auth, Middleware",
        "rating_avg": 4.8,
        "description": "Scalable RESTful API development, authentication mechanisms, and server routing."
    },
    {
        "module_id": "WEB_203",
        "title": "Database Integration with MongoDB & Prisma ORM",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["WEB_202"],
        "duration_hours": 20,
        "skills": "MongoDB, Mongoose, Prisma, Schema Design, Indexing",
        "rating_avg": 4.7,
        "description": "NoSQL and SQL database persistence, schema validation, and aggregation pipelines."
    },
    {
        "module_id": "WEB_301",
        "title": "Full-Stack Next.js 14 App Router & Server Components",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Advanced",
        "prerequisites": ["WEB_201", "WEB_202"],
        "duration_hours": 32,
        "skills": "Next.js, SSR, SSG, Server Actions, TypeScript",
        "rating_avg": 4.9,
        "description": "Production full-stack Next.js applications with hybrid rendering and SEO optimization."
    },
    {
        "module_id": "WEB_302",
        "title": "Web Security, OAuth2 & GraphQL APIs",
        "domain": "Full-Stack Web Development",
        "difficulty_level": "Advanced",
        "prerequisites": ["WEB_202", "WEB_203"],
        "duration_hours": 22,
        "skills": "GraphQL, Apollo, OAuth2, CORS, XSS Prevention, CSRF",
        "rating_avg": 4.8,
        "description": "Hardening web apps against vulnerabilities and building flexible GraphQL query interfaces."
    },

    # --- Track 4: Mobile Application Development ---
    {
        "module_id": "MOB_101",
        "title": "Dart Programming & Mobile Architecture",
        "domain": "Mobile Application Development",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 16,
        "skills": "Dart, OOP, Null Safety, Collections, Asynchronous Dart",
        "rating_avg": 4.7,
        "description": "Language foundations for cross-platform Flutter application development."
    },
    {
        "module_id": "MOB_201",
        "title": "Flutter UI Foundations & Widget Trees",
        "domain": "Mobile Application Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["MOB_101"],
        "duration_hours": 28,
        "skills": "Flutter, Stateless/Stateful Widgets, Custom Animations, Navigation",
        "rating_avg": 4.9,
        "description": "Building pixel-perfect iOS and Android user interfaces with Flutter widgets."
    },
    {
        "module_id": "MOB_202",
        "title": "State Management in Flutter (Bloc & Riverpod)",
        "domain": "Mobile Application Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["MOB_201"],
        "duration_hours": 24,
        "skills": "Bloc, Riverpod, Provider, Reactive State, StreamControllers",
        "rating_avg": 4.8,
        "description": "Clean state separation, architectural patterns, and reactive UI updates."
    },
    {
        "module_id": "MOB_301",
        "title": "Mobile Backend Integration & Firebase Cloud",
        "domain": "Mobile Application Development",
        "difficulty_level": "Intermediate",
        "prerequisites": ["MOB_201"],
        "duration_hours": 22,
        "skills": "Firebase Auth, Firestore, Cloud Functions, Push Notifications",
        "rating_avg": 4.8,
        "description": "Realtime synchronization, push notifications, and cloud database integration."
    },
    {
        "module_id": "MOB_302",
        "title": "Native Device APIs & App Store Deployment",
        "domain": "Mobile Application Development",
        "difficulty_level": "Advanced",
        "prerequisites": ["MOB_202", "MOB_301"],
        "duration_hours": 20,
        "skills": "Camera API, GPS, Local Storage (Hive/SQLite), Play Store, App Store",
        "rating_avg": 4.6,
        "description": "Accessing hardware sensors, offline caching, and release management on app stores."
    },

    # --- Track 5: Cloud Computing & DevOps ---
    {
        "module_id": "CLD_101",
        "title": "Linux Systems Administration & Shell Scripting",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 16,
        "skills": "Linux, Bash, Permissions, SSH, Process Management",
        "rating_avg": 4.8,
        "description": "Mastering the terminal, shell automation, and operating system fundamentals."
    },
    {
        "module_id": "CLD_102",
        "title": "Networking Fundamentals & Protocols",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 14,
        "skills": "TCP/IP, DNS, HTTP/HTTPS, Subnetting, Firewalls",
        "rating_avg": 4.7,
        "description": "Core computer networking principles for cloud architects and sysadmins."
    },
    {
        "module_id": "CLD_201",
        "title": "Containerization with Docker & Multi-Stage Builds",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Intermediate",
        "prerequisites": ["CLD_101"],
        "duration_hours": 20,
        "skills": "Docker, Docker Compose, Images, Volumes, Multi-stage builds",
        "rating_avg": 4.9,
        "description": "Packaging applications into lightweight, reproducible container environments."
    },
    {
        "module_id": "CLD_202",
        "title": "AWS Cloud Foundations & Core Services",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Intermediate",
        "prerequisites": ["CLD_102", "CLD_201"],
        "duration_hours": 28,
        "skills": "AWS EC2, S3, RDS, IAM, VPC, CloudWatch",
        "rating_avg": 4.9,
        "description": "Architecting resilient and cost-effective infrastructure on Amazon Web Services."
    },
    {
        "module_id": "CLD_301",
        "title": "Container Orchestration with Kubernetes (K8s)",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Advanced",
        "prerequisites": ["CLD_201", "CLD_202"],
        "duration_hours": 32,
        "skills": "Kubernetes, Pods, Deployments, Services, Helm, Ingress",
        "rating_avg": 4.8,
        "description": "Managing container clusters at enterprise scale with automated scaling and self-healing."
    },
    {
        "module_id": "CLD_302",
        "title": "Infrastructure as Code (Terraform) & CI/CD Pipelines",
        "domain": "Cloud Computing & DevOps",
        "difficulty_level": "Advanced",
        "prerequisites": ["CLD_202"],
        "duration_hours": 26,
        "skills": "Terraform, GitHub Actions, GitLab CI, Pipeline Automation",
        "rating_avg": 4.9,
        "description": "Automating infrastructure provisioning and continuous delivery pipelines."
    },

    # --- Track 6: Cybersecurity & Ethical Hacking ---
    {
        "module_id": "SEC_101",
        "title": "Cybersecurity Fundamentals & Threat Landscape",
        "domain": "Cybersecurity & Ethical Hacking",
        "difficulty_level": "Beginner",
        "prerequisites": [],
        "duration_hours": 16,
        "skills": "CIA Triad, Malware Types, Phishing, Security Policies",
        "rating_avg": 4.7,
        "description": "Introduction to information security principles, threat modeling, and defense strategies."
    },
    {
        "module_id": "SEC_201",
        "title": "Network Security & Packet Analysis with Wireshark",
        "domain": "Cybersecurity & Ethical Hacking",
        "difficulty_level": "Intermediate",
        "prerequisites": ["SEC_101", "CLD_102"],
        "duration_hours": 22,
        "skills": "Wireshark, Nmap, Packet Inspection, IDS/IPS, Snort",
        "rating_avg": 4.8,
        "description": "Deep-dive network traffic analysis, port scanning, and intrusion detection systems."
    },
    {
        "module_id": "SEC_202",
        "title": "Web Application Penetration Testing (OWASP Top 10)",
        "domain": "Cybersecurity & Ethical Hacking",
        "difficulty_level": "Intermediate",
        "prerequisites": ["SEC_101", "WEB_102"],
        "duration_hours": 28,
        "skills": "Burp Suite, SQL Injection, XSS, CSRF, IDOR, SSRF",
        "rating_avg": 4.9,
        "description": "Hands-on vulnerability assessment and exploitation of web application vulnerabilities."
    },
    {
        "module_id": "SEC_301",
        "title": "Applied Cryptography & Public Key Infrastructure",
        "domain": "Cybersecurity & Ethical Hacking",
        "difficulty_level": "Advanced",
        "prerequisites": ["SEC_101"],
        "duration_hours": 20,
        "skills": "AES, RSA, ECC, Hash Functions, Digital Signatures, PKI",
        "rating_avg": 4.6,
        "description": "Mathematical principles of modern encryption algorithms, hashing, and key exchange."
    },
    {
        "module_id": "SEC_302",
        "title": "Digital Forensics & Incident Response (DFIR)",
        "domain": "Cybersecurity & Ethical Hacking",
        "difficulty_level": "Advanced",
        "prerequisites": ["SEC_201", "CLD_101"],
        "duration_hours": 26,
        "skills": "Memory Forensics, Volatility, Log Analysis, SIEM (Splunk)",
        "rating_avg": 4.8,
        "description": "Investigating active security breaches, analyzing memory artifacts, and threat hunting."
    }
]

# ----------------------------------------------------------------------
# 2. GENERATE INTERN PROFILES
# ----------------------------------------------------------------------
FIRST_NAMES = [
    "Ahmad", "Fatima", "Ali", "Zainab", "Bilal", "Ayesha", "Hamza", "Mariam", "Usman", "Sana",
    "Omar", "Hira", "Hassan", "Khadija", "Tariq", "Amna", "Zubair", "Mahnoor", "Saad", "Laiba",
    "Daniyal", "Noor", "Mustafa", "Anum", "Farhan", "Iqra", "Waqas", "Rabia", "Rehan", "Nimra"
]

LAST_NAMES = [
    "Khan", "Ahmed", "Malik", "Chaudhry", "Shah", "Siddiqui", "Qureshi", "Raza", "Bhatti", "Mirza",
    "Akhtar", "Sheikh", "Abbasi", "Farooq", "Rehman", "Iqbal", "Javed", "Nawaz", "Aziz", "Hashmi"
]

DOMAINS = [
    "AI & Machine Learning",
    "Data Science & Analytics",
    "Full-Stack Web Development",
    "Mobile Application Development",
    "Cloud Computing & DevOps",
    "Cybersecurity & Ethical Hacking"
]

EXPERIENCE_LEVELS = ["Beginner", "Intermediate", "Advanced"]
LEARNING_PACES = ["Standard (10 hrs/wk)", "Intensive (20 hrs/wk)", "Part-Time (5 hrs/wk)"]

def generate_intern_profiles(num_interns=600):
    profiles = []
    for i in range(1, num_interns + 1):
        intern_id = f"INT_{i:04d}"
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        primary_track = random.choice(DOMAINS)
        
        # 30% have a secondary interest track
        secondary_track = random.choice([d for d in DOMAINS if d != primary_track]) if random.random() < 0.3 else None
        
        exp_level = np.random.choice(EXPERIENCE_LEVELS, p=[0.55, 0.35, 0.10])
        pace = random.choice(LEARNING_PACES)
        
        profiles.append({
            "intern_id": intern_id,
            "name": name,
            "primary_track": primary_track,
            "secondary_track": secondary_track if secondary_track else "None",
            "experience_level": exp_level,
            "learning_pace": pace
        })
    return pd.DataFrame(profiles)

# ----------------------------------------------------------------------
# 3. GENERATE REALISTIC INTERACTION MATRIX
# ----------------------------------------------------------------------
def generate_intern_interactions(profiles_df, courses_df, min_interactions=12, max_interactions=24):
    interactions = []
    course_dict = {row["module_id"]: row for _, row in courses_df.iterrows()}
    all_module_ids = list(course_dict.keys())
    
    for _, intern in profiles_df.iterrows():
        intern_id = intern["intern_id"]
        primary_track = intern["primary_track"]
        secondary_track = intern["secondary_track"]
        exp_level = intern["experience_level"]
        
        # Filter courses by track
        primary_courses = [c["module_id"] for c in COURSES_DATA if c["domain"] == primary_track]
        secondary_courses = [c["module_id"] for c in COURSES_DATA if c["domain"] == secondary_track] if secondary_track != "None" else []
        other_courses = [c["module_id"] for c in COURSES_DATA if c["domain"] not in [primary_track, secondary_track]]
        
        # Decide how many courses this intern interacted with
        num_courses = random.randint(min_interactions, max_interactions)
        
        # Select modules according to realistic track affinity weights
        selected_modules = set()
        
        # Sample primary
        k_primary = min(len(primary_courses), int(num_courses * 0.65) + 1)
        selected_modules.update(random.sample(primary_courses, k_primary))
        
        # Sample secondary
        if secondary_courses:
            k_secondary = min(len(secondary_courses), int(num_courses * 0.20) + 1)
            selected_modules.update(random.sample(secondary_courses, k_secondary))
            
        # Fill remaining with other courses for cross-domain sparsity
        remaining = num_courses - len(selected_modules)
        if remaining > 0 and other_courses:
            k_other = min(len(other_courses), remaining)
            selected_modules.update(random.sample(other_courses, k_other))
            
        # Simulate ratings, quiz scores, and completion percentage
        for module_id in selected_modules:
            module = course_dict[module_id]
            is_primary = (module["domain"] == primary_track)
            
            # Base preference higher if in primary track
            if is_primary:
                mean_rating = 4.4 if exp_level != "Beginner" else 4.2
                mean_completion = 90
            else:
                mean_rating = 3.6
                mean_completion = 65
                
            # Add difficulty alignment factor
            if exp_level == "Beginner" and module["difficulty_level"] == "Advanced":
                mean_rating -= 0.8
                mean_completion -= 25
            elif exp_level == "Advanced" and module["difficulty_level"] == "Beginner":
                mean_rating += 0.2
                mean_completion += 10
                
            # Sample realistic rating bounded in [1.0, 5.0]
            rating = np.clip(np.random.normal(loc=mean_rating, scale=0.6), 1.0, 5.0)
            rating = round(rating * 2) / 2 # Snap to 0.5 increments (e.g. 4.0, 4.5, 5.0)
            
            completion_pct = int(np.clip(np.random.normal(loc=mean_completion, scale=12), 20, 100))
            quiz_score = int(np.clip(completion_pct + np.random.normal(0, 5), 40, 100))
            time_spent = round(module["duration_hours"] * (completion_pct / 100) * np.random.uniform(0.9, 1.3), 1)
            
            status = "Completed" if completion_pct >= 85 else ("In-Progress" if completion_pct >= 40 else "Dropped")
            
            interactions.append({
                "intern_id": intern_id,
                "module_id": module_id,
                "rating": rating,
                "completion_percentage": completion_pct,
                "quiz_score": quiz_score,
                "time_spent_hours": time_spent,
                "status": status
            })
            
    return pd.DataFrame(interactions)

# ----------------------------------------------------------------------
# 4. MAIN PIPELINE EXECUTION
# ----------------------------------------------------------------------
def main():
    print("=========================================================")
    print("  INTERNEE.PK - TASK 3: SYNTHETIC DATASET GENERATION     ")
    print("=========================================================")
    
    # 1. Save Courses Metadata
    courses_df = pd.DataFrame(COURSES_DATA)
    courses_df_export = courses_df.copy()
    courses_df_export["prerequisites"] = courses_df_export["prerequisites"].apply(lambda p: ",".join(p) if p else "None")
    courses_path = os.path.join(DATA_DIR, "courses_metadata.csv")
    courses_df_export.to_csv(courses_path, index=False)
    print(f"[+] Generated {len(courses_df)} courses across {len(DOMAINS)} tracks -> {courses_path}")
    
    # 2. Save Intern Profiles
    profiles_df = generate_intern_profiles(num_interns=600)
    profiles_path = os.path.join(DATA_DIR, "intern_profiles.csv")
    profiles_df.to_csv(profiles_path, index=False)
    print(f"[+] Generated {len(profiles_df)} intern profiles -> {profiles_path}")
    
    # 3. Save Interactions
    interactions_df = generate_intern_interactions(profiles_df, courses_df)
    interactions_path = os.path.join(DATA_DIR, "intern_interactions.csv")
    interactions_df.to_csv(interactions_path, index=False)
    print(f"[+] Generated {len(interactions_df)} intern-course interactions -> {interactions_path}")
    
    # Calculate matrix sparsity
    num_users = profiles_df["intern_id"].nunique()
    num_items = courses_df["module_id"].nunique()
    total_possible = num_users * num_items
    actual_interactions = len(interactions_df)
    sparsity = (1 - (actual_interactions / total_possible)) * 100
    
    print("\n--- Dataset Summary Statistics ---")
    print(f"* Total Interns (Users): {num_users}")
    print(f"* Total Modules (Items): {num_items}")
    print(f"* Total Interaction Records: {actual_interactions}")
    print(f"* User-Item Matrix Sparsity: {sparsity:.2f}% (Realistic CF Sparsity)")
    print(f"* Average Ratings per Intern: {actual_interactions / num_users:.1f}")
    print("=========================================================\n")

if __name__ == "__main__":
    main()
