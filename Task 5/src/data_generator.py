"""
Data Generator for Intern Skill Gap Analysis & Industry Demand Alignment.
Generates:
1. data/job_postings.csv (500+ tech job postings across 6 major domains)
2. data/intern_skills.csv (150+ realistic intern profiles)
3. data/training_catalog.csv (curated courses, projects, and certifications per skill)
"""

import os
import random
import pandas as pd
import numpy as np

# Set seed for reproducibility
random.seed(42)
np.random.seed(42)

# Domains and their rich skill pools, typical job titles, and job description templates
DOMAINS = {
    "Data Science & Analytics": {
        "titles": [
            "Data Scientist", "Junior Data Scientist", "Data Analyst", 
            "BI Analyst", "Quantitative Analyst", "Machine Learning Analyst"
        ],
        "core_skills": [
            "Python", "SQL", "Pandas", "NumPy", "Scikit-Learn", "Data Visualization",
            "Tableau", "Power BI", "Exploratory Data Analysis", "Statistical Modeling",
            "Hypothesis Testing", "Feature Engineering", "Matplotlib", "Seaborn", "Git"
        ],
        "advanced_skills": [
            "BigQuery", "Snowflake", "Spark", "A/B Testing", "Time Series Forecasting",
            "XGBoost", "Data Storytelling", "SQL Optimization", "Airflow"
        ],
        "desc_templates": [
            "We are seeking a {title} with strong analytical abilities. You will extract actionable insights from large datasets, build predictive models using {skills}, and build dashboards in {tool} for stakeholders.",
            "Looking for a motivated {title} to join our analytics team. Key responsibilities include statistical modeling, data cleaning with {skills}, and translating data into strategic recommendations.",
            "As a {title}, you will design ML pipelines using {skills}, optimize database queries, and present findings using {tool} to executive leadership."
        ],
        "tools": ["Tableau", "Power BI", "Metabase", "Looker"]
    },
    "AI & Machine Learning": {
        "titles": [
            "Machine Learning Engineer", "AI Research Intern", "NLP Engineer",
            "Computer Vision Engineer", "Deep Learning Specialist", "LLM Applications Engineer"
        ],
        "core_skills": [
            "Python", "PyTorch", "TensorFlow", "Deep Learning", "Natural Language Processing",
            "Transformers", "Computer Vision", "Scikit-Learn", "NumPy", "Mathematics & Linear Algebra",
            "Git", "REST APIs"
        ],
        "advanced_skills": [
            "HuggingFace", "MLOps", "Model Optimization", "LangChain", "Vector Databases",
            "ONNX", "Docker", "Kubernetes", "CUDA", "MLflow", "Fine-Tuning"
        ],
        "desc_templates": [
            "Join our frontier AI team as an {title}. You will design, train, and deploy state-of-the-art neural networks using {skills} to solve complex computer perception and NLP tasks.",
            "Seeking an innovative {title} to build Generative AI and deep learning workflows. Must have experience with {skills} and deploying models via {tool}.",
            "We are hiring a {title} to scale our ML infrastructure. Responsibilities include training vision and language models using {skills} and continuous MLOps pipelines."
        ],
        "tools": ["MLflow", "Docker", "FastAPI", "Triton Inference Server"]
    },
    "Full Stack & Web Development": {
        "titles": [
            "Full Stack Developer", "Frontend Developer", "Backend Developer",
            "React / Node.js Developer", "Software Engineer", "Web Applications Engineer"
        ],
        "core_skills": [
            "JavaScript", "TypeScript", "React", "Node.js", "Express.js",
            "HTML5", "CSS3", "RESTful APIs", "Git", "SQL", "MongoDB", "PostgreSQL"
        ],
        "advanced_skills": [
            "Next.js", "GraphQL", "Tailwind CSS", "Redux", "Docker", "Jest",
            "Microservices Architecture", "Redis", "WebSockets", "CI/CD"
        ],
        "desc_templates": [
            "We are seeking a talented {title} to build responsive, robust web applications using {skills}. You will design REST APIs and craft smooth user interfaces with modern frameworks.",
            "Looking for a {title} skilled in modern web stacks. You will collaborate with product designers, implement state management using {tool}, and develop backend microservices with {skills}.",
            "Join our agile development team as a {title}. You will write clean modular code using {skills}, write automated tests, and deploy scalable web apps."
        ],
        "tools": ["Redux Toolkit", "Next.js", "Tailwind CSS", "Docker"]
    },
    "Cloud Computing & DevOps": {
        "titles": [
            "Cloud Engineer", "DevOps Engineer", "Site Reliability Engineer (SRE)",
            "Cloud Infrastructure Analyst", "Platform Engineer", "DevSecOps Associate"
        ],
        "core_skills": [
            "AWS", "Linux", "Docker", "Kubernetes", "CI/CD Pipelines",
            "Git", "Bash Scripting", "Terraform", "Infrastructure as Code", "Networking Basics"
        ],
        "advanced_skills": [
            "Azure", "GCP", "Ansible", "Prometheus", "Grafana", "Helm",
            "Cloud Security", "Jenkins", "GitHub Actions", "ArgoCD"
        ],
        "desc_templates": [
            "Looking for a high-performing {title} to automate deployment lifecycles, manage container orchestration using {skills}, and ensure 99.9% cloud infrastructure uptime.",
            "As our {title}, you will architect scalable cloud environments using {skills}, maintain observability with {tool}, and enforce infrastructure security.",
            "We are seeking a {title} passionate about automation. You will implement CI/CD pipelines, configure cloud services with {skills}, and streamline developer workflows."
        ],
        "tools": ["Prometheus & Grafana", "GitHub Actions", "Terraform", "Kubernetes"]
    },
    "Cybersecurity & Information Security": {
        "titles": [
            "Cybersecurity Analyst", "Information Security Specialist", "SOC Analyst",
            "Penetration Tester", "Network Security Associate", "Threat Intelligence Analyst"
        ],
        "core_skills": [
            "Network Security", "Linux", "Ethical Hacking", "Vulnerability Assessment",
            "Wireshark", "SIEM Tools", "Cryptography Basics", "TCP/IP & Firewalls", "Python Scripting"
        ],
        "advanced_skills": [
            "Splunk", "Metasploit", "Burp Suite", "Incident Response", "OWASP Top 10",
            "Malware Analysis", "Security Compliance (ISO/NIST)", "Cloud Security Auditing"
        ],
        "desc_templates": [
            "We are hiring a vigilant {title} to monitor security operations, analyze intrusion alerts using {skills}, and perform vulnerability scans across enterprise systems.",
            "Seeking an energetic {title} to conduct threat hunting and pen-testing. Key responsibilities include identifying software vulnerabilities using {skills} and {tool}.",
            "Join our SecOps team as a {title}. You will safeguard critical digital assets, investigate security breaches, and write automated detection scripts with {skills}."
        ],
        "tools": ["Splunk", "Burp Suite", "Wireshark", "Metasploit"]
    },
    "Mobile Application Development": {
        "titles": [
            "Mobile App Developer", "Flutter Developer", "React Native Developer",
            "Android Developer (Kotlin)", "iOS Developer (Swift)", "Cross-Platform Mobile Engineer"
        ],
        "core_skills": [
            "Flutter", "Dart", "React Native", "JavaScript", "Mobile UI/UX Design",
            "REST APIs", "Git", "Firebase", "State Management (Provider/Bloc/Redux)", "Mobile Architecture"
        ],
        "advanced_skills": [
            "Kotlin", "Swift", "Native Modules", "App Store / Play Store Deployment",
            "Push Notifications", "Offline Storage (SQLite/Hive)", "GraphQL", "CI/CD for Mobile"
        ],
        "desc_templates": [
            "We are seeking a creative {title} to build high-performance mobile applications using {skills}. You will integrate backend REST APIs and ensure seamless 60fps animations.",
            "Looking for a {title} to lead cross-platform app initiatives. You will develop modern interactive UI layouts with {skills} and manage local caching with {tool}.",
            "Join our mobile engineering team as a {title}. You will design scalable client apps, publish apps to app stores, and implement offline features using {skills}."
        ],
        "tools": ["Bloc State Management", "Firebase Cloud Messaging", "Hive DB", "Fastlane"]
    }
}

FIRST_NAMES = [
    "Ahmad", "Fatima", "Ali", "Zainab", "Bilal", "Ayesha", "Hamza", "Mariam", "Usman", "Sana",
    "Omar", "Hira", "Tariq", "Khadija", "Hassan", "Mahnoor", "Saad", "Laiba", "Zubair", "Iqra",
    "Mustafa", "Anum", "Danish", "Rabia", "Farhan", "Sara", "Adnan", "Noor", "Waqas", "Bushra"
]

LAST_NAMES = [
    "Khan", "Ahmed", "Malik", "Sheikh", "Chaudhry", "Raza", "Bhatti", "Siddiqui", "Qureshi", "Ansari",
    "Shah", "Mirza", "Abbasi", "Farooq", "Akram", "Hussain", "Javed", "Nawaz", "Iqbal", "Butt"
]

COMPANIES = [
    "DevTech Innovations", "Alpha Cloud Systems", "NexGen AI Labs", "Synergy Global", "DataSphere Analytics",
    "CyberGuard Solutions", "Pulse Software Studio", "ByteCraft Technologies", "Apex FinTech", "Quantum Digital",
    "Vanguard Systems", "Krypton Security", "InnoWave Solutions", "Orbital HealthTech", "Starlight Media Labs"
]

EXPERIENCE_LEVELS = ["Entry Level (0-1 yrs)", "Associate (1-2 yrs)", "Mid Level (2-3 yrs)"]
EDUCATION_LEVELS = ["Bachelor of Science in Computer Science", "BS Software Engineering", "BS Data Science", "BS Information Technology", "BS Artificial Intelligence"]

def generate_job_postings(num_records=550):
    records = []
    domains_list = list(DOMAINS.keys())
    
    for i in range(1, num_records + 1):
        domain = random.choice(domains_list)
        dom_info = DOMAINS[domain]
        
        title = random.choice(dom_info["titles"])
        company = random.choice(COMPANIES)
        exp = random.choice(EXPERIENCE_LEVELS)
        location = random.choice(["Remote", "Hybrid", "Islamabad, PK", "Lahore, PK", "Karachi, PK", "Dubai, UAE", "London, UK"])
        
        # Pick 5 to 8 skills (mix of core and advanced)
        num_core = random.randint(4, min(7, len(dom_info["core_skills"])))
        num_adv = random.randint(1, min(4, len(dom_info["advanced_skills"])))
        
        chosen_core = random.sample(dom_info["core_skills"], num_core)
        chosen_adv = random.sample(dom_info["advanced_skills"], num_adv)
        all_skills = chosen_core + chosen_adv
        random.shuffle(all_skills)
        
        skills_str = ", ".join(all_skills)
        
        template = random.choice(dom_info["desc_templates"])
        tool = random.choice(dom_info["tools"])
        desc_text = template.format(
            title=title,
            skills=", ".join(all_skills[:4]),
            tool=tool
        )
        
        # Append rich context to description
        full_desc = f"{desc_text} Must have strong hands-on proficiency in {skills_str}. Experience with {exp} in agile environments. Key responsibilities include collaborative coding, unit testing, and continuous deployment."
        
        records.append({
            "job_id": f"JOB-{i:04d}",
            "job_title": title,
            "company": company,
            "domain": domain,
            "location": location,
            "experience_required": exp,
            "required_skills": skills_str,
            "job_description": full_desc
        })
        
    df = pd.DataFrame(records)
    return df

def generate_intern_skills(num_records=160):
    records = []
    domains_list = list(DOMAINS.keys())
    
    for i in range(1, num_records + 1):
        name = f"{random.choice(FIRST_NAMES)} {random.choice(LAST_NAMES)}"
        target_domain = random.choice(domains_list)
        dom_info = DOMAINS[target_domain]
        target_role = random.choice(dom_info["titles"])
        education = random.choice(EDUCATION_LEVELS)
        gpa = round(random.uniform(2.85, 3.95), 2)
        
        # Interns have a subset of core skills, maybe 1 advanced skill, plus common foundational skills
        # This creates realistic gaps!
        known_core_count = random.randint(2, min(5, len(dom_info["core_skills"])))
        known_core = random.sample(dom_info["core_skills"], known_core_count)
        
        has_adv = random.random() > 0.65
        known_adv = random.sample(dom_info["advanced_skills"], 1) if has_adv else []
        
        # Some general baseline skills
        baseline = ["Git", "Problem Solving", "Team Collaboration"]
        known_baseline = random.sample(baseline, random.randint(1, 2))
        
        # Merge skills uniquely
        current_skills = list(dict.fromkeys(known_core + known_adv + known_baseline))
        
        # Add a short self-summary
        skills_str = ", ".join(current_skills)
        summary = f"Motivated {education} student aiming for a career as a {target_role} in {target_domain}. Proficient in {skills_str}. Eager to bridge skill gaps and contribute to real-world industrial projects."
        
        records.append({
            "intern_id": f"INT-{i:04d}",
            "name": name,
            "target_domain": target_domain,
            "target_role": target_role,
            "education": education,
            "gpa": gpa,
            "current_skills": skills_str,
            "profile_summary": summary
        })
        
    df = pd.DataFrame(records)
    return df

def generate_training_catalog():
    courses = [
        # Data Science & Analytics
        {"skill": "Pandas", "course_name": "Data Analysis with Python and Pandas", "platform": "Coursera / IBM", "duration_weeks": 4, "difficulty": "Beginner", "project_task": "Analyze exploratory sales datasets and clean messy real-world survey data."},
        {"skill": "Scikit-Learn", "course_name": "Applied Machine Learning with Scikit-Learn", "platform": "Coursera / UMich", "duration_weeks": 5, "difficulty": "Intermediate", "project_task": "Build classification & regression pipelines with hyperparameter tuning."},
        {"skill": "Tableau", "course_name": "Tableau for Business Intelligence & Visual Analytics", "platform": "Udemy", "duration_weeks": 3, "difficulty": "Beginner", "project_task": "Design interactive KPI dashboards with dynamic filters and drilldowns."},
        {"skill": "Power BI", "course_name": "Microsoft Power BI Desktop for Business Intelligence", "platform": "Coursera / Microsoft", "duration_weeks": 4, "difficulty": "Beginner", "project_task": "Model relational schemas and publish executive reporting dashboards."},
        {"skill": "Statistical Modeling", "course_name": "Statistics and Probability for Data Science", "platform": "edX / HarvardX", "duration_weeks": 6, "difficulty": "Intermediate", "project_task": "Perform ANOVA, linear regression diagnostics, and hypothesis tests."},
        {"skill": "Feature Engineering", "course_name": "Feature Engineering & Data Preprocessing Mastery", "platform": "DataCamp", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Construct polynomial features, target encodings, and scaling pipelines."},
        {"skill": "SQL Optimization", "course_name": "Advanced SQL Query Optimization & Window Functions", "platform": "Udacity", "duration_weeks": 4, "difficulty": "Advanced", "project_task": "Optimize indexing, execution plans, and write complex nested aggregations."},
        {"skill": "BigQuery", "course_name": "Serverless Data Warehousing with Google BigQuery", "platform": "Google Cloud Training", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Process multi-gigabyte analytical queries with partitioning and clustering."},
        {"skill": "Spark", "course_name": "Distributed Big Data Processing with Apache Spark & PySpark", "platform": "edX", "duration_weeks": 6, "difficulty": "Advanced", "project_task": "Implement Spark DataFrame transformations and streaming pipelines."},
        {"skill": "Time Series Forecasting", "course_name": "Time Series Analysis & Forecasting with ARIMA & Prophet", "platform": "Coursera", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Forecast 12-month product demand using seasonal decomposition and Prophet."},
        {"skill": "XGBoost", "course_name": "Extreme Gradient Boosting (XGBoost) Masterclass", "platform": "Kaggle Learn", "duration_weeks": 2, "difficulty": "Intermediate", "project_task": "Tune gradient boosting trees to achieve top performance on tabular datasets."},
        {"skill": "Airflow", "course_name": "Data Pipeline Automation with Apache Airflow", "platform": "Udemy", "duration_weeks": 4, "difficulty": "Advanced", "project_task": "Construct modular DAGs for ETL workflows with automated retry policies."},

        # AI & Machine Learning
        {"skill": "PyTorch", "course_name": "Deep Learning with PyTorch: Zero to GANs", "platform": "freeCodeCamp / Jovian", "duration_weeks": 6, "difficulty": "Intermediate", "project_task": "Implement custom neural network modules, autograd training loops, and tensor operations."},
        {"skill": "TensorFlow", "course_name": "DeepLearning.AI TensorFlow Developer Certificate", "platform": "Coursera / DeepLearning.AI", "duration_weeks": 8, "difficulty": "Intermediate", "project_task": "Build CNNs and recurrent models for image and text classification."},
        {"skill": "Transformers", "course_name": "Hugging Face Transformers & Modern NLP Course", "platform": "Hugging Face Academy", "duration_weeks": 5, "difficulty": "Advanced", "project_task": "Fine-tune BERT and RoBERTa models for sentiment analysis and token classification."},
        {"skill": "Natural Language Processing", "course_name": "Natural Language Processing Specialization", "platform": "Coursera / DeepLearning.AI", "duration_weeks": 8, "difficulty": "Intermediate", "project_task": "Implement tokenizers, word embeddings (Word2Vec), and seq2seq models."},
        {"skill": "Computer Vision", "course_name": "Computer Vision Deep Dive: Object Detection & Segmentation", "platform": "Coursera", "duration_weeks": 6, "difficulty": "Advanced", "project_task": "Build YOLO object detection and semantic segmentation pipelines."},
        {"skill": "MLOps", "course_name": "Machine Learning Operations (MLOps) Specialization", "platform": "Coursera / DeepLearning.AI", "duration_weeks": 6, "difficulty": "Advanced", "project_task": "Automate continuous model training, versioning with DVC, and deployment with CI/CD."},
        {"skill": "LangChain", "course_name": "Building LLM Applications with LangChain & Vector Stores", "platform": "DeepLearning.AI", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Construct a retrieval-augmented generation (RAG) agent over internal documentation."},
        {"skill": "Vector Databases", "course_name": "Vector Search and Embeddings with Pinecone & Chroma", "platform": "Pinecone Learning Center", "duration_weeks": 2, "difficulty": "Intermediate", "project_task": "Embed semantic documents and implement fast k-NN vector queries."},
        {"skill": "MLflow", "course_name": "Model Tracking and Experiment Management with MLflow", "platform": "Databricks Academy", "duration_weeks": 2, "difficulty": "Beginner", "project_task": "Track hyperparameters, artifacts, and register production models."},

        # Full Stack & Web Development
        {"skill": "React", "course_name": "Modern React with Redux Toolkit", "platform": "Udemy / Stephen Grider", "duration_weeks": 6, "difficulty": "Intermediate", "project_task": "Build a responsive web application with custom hooks and centralized state."},
        {"skill": "Node.js", "course_name": "Node.js, Express, MongoDB & More: The Complete Bootcamp", "platform": "Udemy / Jonas Schmedtmann", "duration_weeks": 7, "difficulty": "Intermediate", "project_task": "Develop a production REST API with authentication and security middleware."},
        {"skill": "TypeScript", "course_name": "Understanding TypeScript - 2026 Edition", "platform": "Udemy / Maximilian Schwarzmüller", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Refactor a JavaScript codebase to strictly typed TypeScript interfaces and generics."},
        {"skill": "Next.js", "course_name": "Next.js App Router & Server Components Complete Guide", "platform": "Vercel Learn / YouTube", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Create a full-stack blog/e-commerce site with SSR, SSG, and Server Actions."},
        {"skill": "GraphQL", "course_name": "GraphQL with Node.js & Apollo Server", "platform": "Coursera", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Design schemas, resolvers, and queries with Apollo Client integration."},
        {"skill": "MongoDB", "course_name": "MongoDB Basics & Aggregation Pipeline Mastery", "platform": "MongoDB University", "duration_weeks": 3, "difficulty": "Beginner", "project_task": "Implement complex multi-stage aggregation queries and schema validation."},
        {"skill": "PostgreSQL", "course_name": "The Complete SQL & PostgreSQL Mastery Bootcamp", "platform": "Udemy", "duration_weeks": 4, "difficulty": "Beginner", "project_task": "Design 3NF relational schemas, foreign keys, and perform transactional joins."},
        {"skill": "Tailwind CSS", "course_name": "Tailwind CSS From Scratch & Modern UI Layouts", "platform": "freeCodeCamp", "duration_weeks": 2, "difficulty": "Beginner", "project_task": "Build clean responsive landing pages with dark mode support."},
        {"skill": "Redis", "course_name": "Redis for High-Performance Caching & Pub/Sub", "platform": "Redis University", "duration_weeks": 2, "difficulty": "Intermediate", "project_task": "Implement API caching layers and session stores using Redis."},

        # Cloud Computing & DevOps
        {"skill": "Docker", "course_name": "Docker & Containerization Practical Crash Course", "platform": "Coursera / Udemy", "duration_weeks": 3, "difficulty": "Beginner", "project_task": "Containerize multi-container microservices with docker-compose."},
        {"skill": "Kubernetes", "course_name": "Certified Kubernetes Administrator (CKA) Training", "platform": "KodeKloud / Linux Foundation", "duration_weeks": 6, "difficulty": "Advanced", "project_task": "Deploy Pods, Deployments, Services, Ingress, and ConfigMaps to a cluster."},
        {"skill": "AWS", "course_name": "AWS Certified Solutions Architect Associate Prep", "platform": "Coursera / AWS", "duration_weeks": 8, "difficulty": "Intermediate", "project_task": "Provision VPCs, EC2, S3, RDS, Lambda, and IAM security roles."},
        {"skill": "CI/CD Pipelines", "course_name": "Automated CI/CD with GitHub Actions & GitLab CI", "platform": "Udacity", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Construct build-test-deploy automated workflow scripts for GitHub repos."},
        {"skill": "Terraform", "course_name": "HashiCorp Certified: Terraform Associate Bootcamp", "platform": "Udemy", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Write modular Infrastructure as Code (IaC) to spin up multi-region cloud resources."},
        {"skill": "Linux", "course_name": "Linux Command Line & Shell Scripting Mastery", "platform": "edX / Linux Foundation", "duration_weeks": 4, "difficulty": "Beginner", "project_task": "Automate server maintenance with cron jobs, grep, awk, and bash scripts."},
        {"skill": "Prometheus", "course_name": "Cloud Monitoring with Prometheus & Alertmanager", "platform": "Udemy", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Scrape node metrics, configure alerts, and route notifications."},
        {"skill": "Grafana", "course_name": "Interactive Metrics & Log Visualization in Grafana", "platform": "Grafana Labs", "duration_weeks": 2, "difficulty": "Beginner", "project_task": "Build live telemetry dashboards with custom PromQL queries."},

        # Cybersecurity & Information Security
        {"skill": "Network Security", "course_name": "Network Security Fundamentals & Defense Strategies", "platform": "Coursera / Cisco", "duration_weeks": 5, "difficulty": "Intermediate", "project_task": "Configure firewalls, IDS/IPS rules, and analyze subnet traffic."},
        {"skill": "Wireshark", "course_name": "Network Packet Analysis with Wireshark", "platform": "Pluralsight", "duration_weeks": 2, "difficulty": "Beginner", "project_task": "Capture and inspect TCP handshakes, DNS packets, and malicious payloads."},
        {"skill": "Ethical Hacking", "course_name": "Practical Ethical Hacking - Complete Course", "platform": "TCM Security Academy", "duration_weeks": 8, "difficulty": "Intermediate", "project_task": "Perform reconnaissance, vulnerability scanning, and privilege escalation labs."},
        {"skill": "SIEM Tools", "course_name": "SIEM & SOC Operations with Splunk", "platform": "Splunk Training", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Ingest server logs, create threat alerts, and investigate breach simulations."},
        {"skill": "OWASP Top 10", "course_name": "Web Application Security & OWASP Top 10 Exploits", "platform": "Coursera", "duration_weeks": 4, "difficulty": "Intermediate", "project_task": "Identify and patch SQL injection, XSS, CSRF, and SSRF flaws in test web apps."},
        {"skill": "Burp Suite", "course_name": "Web Pentesting with Burp Suite Professional", "platform": "PortSwigger Web Security Academy", "duration_weeks": 3, "difficulty": "Intermediate", "project_task": "Intercept HTTP requests, fuzz parameter endpoints, and exploit auth bypasses."},

        # Mobile Application Development
        {"skill": "Flutter", "course_name": "Flutter & Dart - The Complete Guide (2026)", "platform": "Udemy / Academind", "duration_weeks": 7, "difficulty": "Intermediate", "project_task": "Build a cross-platform mobile application with responsive widgets and navigation."},
        {"skill": "Dart", "course_name": "Dart Programming Language Essentials", "platform": "Dart.dev / freeCodeCamp", "duration_weeks": 2, "difficulty": "Beginner", "project_task": "Master object-oriented patterns, async/await streams, and functional Dart."},
        {"skill": "React Native", "course_name": "React Native - The Practical Guide", "platform": "Udemy", "duration_weeks": 6, "difficulty": "Intermediate", "project_task": "Develop an iOS & Android app with React Navigation and native device features."},
        {"skill": "Firebase", "course_name": "Firebase for Mobile: Firestore, Auth & Cloud Functions", "platform": "Google Developers", "duration_weeks": 3, "difficulty": "Beginner", "project_task": "Implement realtime database sync, OAuth user login, and push notifications."},
        {"skill": "Kotlin", "course_name": "Android App Development with Kotlin Bootcamp", "platform": "Coursera / Google", "duration_weeks": 7, "difficulty": "Intermediate", "project_task": "Build modern Android apps using Jetpack Compose, Room DB, and ViewModel."},
        {"skill": "Swift", "course_name": "iOS 18 & Swift Development Bootcamp", "platform": "Udemy / Angela Yu", "duration_weeks": 8, "difficulty": "Intermediate", "project_task": "Create SwiftUI apps with CoreData storage and Apple design guidelines."}
    ]
    df = pd.DataFrame(courses)
    return df

def generate_all_datasets(output_dir="data"):
    os.makedirs(output_dir, exist_ok=True)
    
    print("Generating Job Postings Dataset...")
    jobs_df = generate_job_postings(num_records=550)
    jobs_path = os.path.join(output_dir, "job_postings.csv")
    jobs_df.to_csv(jobs_path, index=False)
    print(f"Saved {len(jobs_df)} job postings to {jobs_path}")
    
    print("Generating Intern Skills Dataset...")
    interns_df = generate_intern_skills(num_records=160)
    interns_path = os.path.join(output_dir, "intern_skills.csv")
    interns_df.to_csv(interns_path, index=False)
    print(f"Saved {len(interns_df)} intern profiles to {interns_path}")
    
    print("Generating Training & Course Catalog...")
    catalog_df = generate_training_catalog()
    catalog_path = os.path.join(output_dir, "training_catalog.csv")
    catalog_df.to_csv(catalog_path, index=False)
    print(f"Saved {len(catalog_df)} course modules to {catalog_path}")
    
    return jobs_df, interns_df, catalog_df

if __name__ == "__main__":
    generate_all_datasets()
