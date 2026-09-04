"""
Data Generator for AI Interview Question Generation System
Generates structured datasets for:
1. Question Bank (Technical, Behavioral STAR, Coding, Architecture across 8 tracks)
2. Intern Profiles (Realistic candidate resumes with skills, projects, experience)
3. Job Descriptions (Internship roles with required & preferred tech stacks)
4. Competency Framework (STAR behavioral rubrics and behavioral indicators)
"""

import json
import csv
import os
import random
from typing import List, Dict, Any

os.makedirs("data", exist_ok=True)
os.makedirs("exports", exist_ok=True)

# -------------------------------------------------------------
# 1. QUESTION BANK GENERATION (8 Tracks, Diverse Difficulties)
# -------------------------------------------------------------
TRACKS = [
    "AI & Machine Learning",
    "Data Science & Analytics",
    "Full-Stack Web Development",
    "Backend Engineering (Python / Java / Go)",
    "Frontend Engineering (React / Next.js / Vue)",
    "Cloud & DevOps Engineering",
    "Cybersecurity & Information Assurance",
    "Mobile App Development (Flutter / Android / iOS)"
]

# High-quality question base templates
TECH_QUESTIONS_POOL = {
    "AI & Machine Learning": [
        {
            "topic": "Neural Networks & Backpropagation",
            "skill": "Deep Learning",
            "difficulty": "Easy",
            "question": "Can you explain how backpropagation and gradient descent work together during neural network training?",
            "expected_answer_points": [
                "Forward pass calculates predictions and loss",
                "Chain rule calculates gradients of loss with respect to weights",
                "Gradient descent updates weights in opposite direction of gradient",
                "Learning rate controls step size"
            ],
            "rubric_5": "Clear articulation of forward vs backward pass, mathematical intuition of chain rule, and role of learning rate with potential pitfalls (exploding/vanishing gradients).",
            "follow_up": "How would you diagnose if your neural network is suffering from vanishing gradients, and what architectural fixes would you apply?"
        },
        {
            "topic": "Overfitting & Regularization",
            "skill": "Machine Learning",
            "difficulty": "Easy",
            "question": "What is the difference between L1 (Lasso) and L2 (Ridge) regularization, and when would you choose one over the other?",
            "expected_answer_points": [
                "L1 penalizes absolute value of weights and induces sparsity (feature selection)",
                "L2 penalizes squared magnitude of weights, shrinking weights without zeroing them",
                "L1 is suitable when feature selection is desired; L2 when many collinear features are present"
            ],
            "rubric_5": "Accurately distinguishes L1 vs L2 mathematical penalties, sparsity mechanics, and provides realistic real-world selection criteria.",
            "follow_up": "What is ElasticNet and in what scenario does it outperform pure Lasso or Ridge?"
        },
        {
            "topic": "Transformers & Attention Mechanism",
            "skill": "NLP & Transformers",
            "difficulty": "Medium",
            "question": "How does the Self-Attention mechanism in Transformers solve the sequential bottleneck of RNNs and LSTMs?",
            "expected_answer_points": [
                "Self-attention allows direct comparison of all tokens simultaneously (O(1) sequential path)",
                "Enables massive parallelization across GPU cores during training",
                "Computes Query, Key, Value matrix projections and scaled dot-product attention",
                "Captures long-range dependencies without vanishing gradient across time steps"
            ],
            "rubric_5": "Explains Q, K, V math (Softmax(QK^T / sqrt(d_k)) * V), parallel computing benefits over recurrence, and positional encodings.",
            "follow_up": "Why is the dot-product divided by the square root of the key dimension (sqrt(d_k))?"
        },
        {
            "topic": "Model Evaluation & Imbalanced Data",
            "skill": "Data Modeling",
            "difficulty": "Medium",
            "question": "When working with an imbalanced classification problem (e.g., 99% negative, 1% positive), why is accuracy misleading, and what alternative metrics and techniques would you use?",
            "expected_answer_points": [
                "Accuracy paradox: predicting majority class yields 99% accuracy but 0 utility",
                "Use Precision, Recall, F1-Score, PR-AUC, ROC-AUC",
                "Sampling techniques: SMOTE, random undersampling/oversampling",
                "Class-weighted loss functions (Focal Loss, cost-sensitive learning)"
            ],
            "rubric_5": "Thoroughly explains precision-recall trade-offs, confusion matrix, threshold tuning, and data/loss-level mitigation strategies.",
            "follow_up": "If false negatives are significantly more costly than false positives (e.g., fraud detection), how would you adjust your decision threshold?"
        },
        {
            "topic": "LLMs & Retrieval-Augmented Generation (RAG)",
            "skill": "Generative AI",
            "difficulty": "Hard",
            "question": "Walk me through the architecture of a production-grade RAG pipeline. How do you handle chunking, embedding retrieval, re-ranking, and hallucination reduction?",
            "expected_answer_points": [
                "Document chunking strategies (semantic chunking, sliding window with overlap)",
                "Vector database indexing (HNSW, FAISS, Cosine/Dot similarity)",
                "Bi-encoder dense retrieval followed by Cross-Encoder re-ranking",
                "Prompt grounding with strict context injection and hallucination guardrails (e.g., citations, faithfulness check)"
            ],
            "rubric_5": "Demonstrates practical production knowledge: chunk overlap trade-offs, vector search limitations, hybrid lexical/semantic search, and hallucination mitigation.",
            "follow_up": "How would you measure the retrieval accuracy (hit rate / MRR) independently of the LLM generation quality?"
        },
        {
            "topic": "MLOps & Model Deployment",
            "skill": "MLOps",
            "difficulty": "Hard",
            "question": "How do you detect and mitigate Data Drift and Concept Drift in a deployed machine learning service?",
            "expected_answer_points": [
                "Data drift: P(X) changes while P(Y|X) remains same (e.g., Kolmogorov-Smirnov test, PSI)",
                "Concept drift: P(Y|X) changes (e.g., consumer behavior shifts)",
                "Monitoring metrics: feature distributions, prediction drift, ground truth latency",
                "Mitigation: automated retraining triggers, sliding window training, shadow deployment"
            ],
            "rubric_5": "Accurately contrasts data vs concept drift, mentions statistical tests (KS-test, Wasserstein distance), and outlines resilient retraining pipelines.",
            "follow_up": "What is the difference between blue/green deployment and canary deployment for a model inference microservice?"
        }
    ],
    "Full-Stack Web Development": [
        {
            "topic": "State Management & React Rendering",
            "skill": "React.js",
            "difficulty": "Easy",
            "question": "How does React's Virtual DOM work, and how does React determine when to re-render a component?",
            "expected_answer_points": [
                "Virtual DOM is an in-memory lightweight representation of actual DOM",
                "Reconciliation & Diffing algorithm compares virtual trees",
                "State or props change triggers re-render of component and its subtree",
                "Optimization using React.memo, useMemo, useCallback, and key props"
            ],
            "rubric_5": "Detailed explanation of reconciliation algorithm, batched updates, shallow comparison of props/state, and common re-render pitfalls.",
            "follow_up": "Why should you never use the array index as a 'key' prop when rendering dynamic lists?"
        },
        {
            "topic": "RESTful API Design & HTTP Protocols",
            "skill": "API Development",
            "difficulty": "Easy",
            "question": "What are the core principles of RESTful architecture, and what is the difference between PUT and PATCH methods?",
            "expected_answer_points": [
                "Statelessness, client-server separation, uniform interface, resource-based URIs",
                "PUT replaces the entire resource representation (idempotent)",
                "PATCH updates partial attributes of the resource",
                "Standard HTTP status codes (200, 201, 204, 400, 401, 404, 500)"
            ],
            "rubric_5": "Distinguishes idempotency, partial vs full updates, URI naming conventions, and proper status code usage.",
            "follow_up": "What makes an HTTP method 'idempotent', and why is POST not idempotent while PUT and DELETE are?"
        },
        {
            "topic": "Database Indexing & Query Optimization",
            "skill": "PostgreSQL / Databases",
            "difficulty": "Medium",
            "question": "How does a B-Tree index accelerate database queries, and what are the trade-offs of having too many indexes?",
            "expected_answer_points": [
                "B-Tree index allows logarithmic O(log N) lookup, range scans, and sorting",
                "Without index, database must perform full table scan O(N)",
                "Trade-off: slower write operations (INSERT, UPDATE, DELETE) due to index maintenance",
                "Trade-off: increased disk and memory (RAM buffer pool) consumption"
            ],
            "rubric_5": "Explains internal balanced tree traversal, write overhead trade-offs, composite index column ordering rule (leftmost prefix rule).",
            "follow_up": "What is an EXPLAIN ANALYZE query plan, and what key metrics do you inspect to find slow queries?"
        },
        {
            "topic": "Authentication & Session Security",
            "skill": "Web Security",
            "difficulty": "Medium",
            "question": "Explain how JWT (JSON Web Token) authentication works versus Server-Side Session authentication. Where should tokens be stored securely on the frontend?",
            "expected_answer_points": [
                "JWT is stateless, signed cryptographically (Header.Payload.Signature)",
                "Server sessions are stateful, stored in Redis/DB with session ID cookie",
                "JWT stored in localStorage is vulnerable to XSS attacks",
                "Best practice: httpOnly, Secure, SameSite cookies to protect against XSS and CSRF"
            ],
            "rubric_5": "Clear security trade-offs (XSS vs CSRF), token revocation challenges with stateless JWTs, and secure cookie storage best practices.",
            "follow_up": "If a JWT is stateless and valid for 1 hour, how can an administrator immediately revoke access if a user account is compromised?"
        },
        {
            "topic": "Full-Stack System Architecture & Caching",
            "skill": "System Architecture",
            "difficulty": "Hard",
            "question": "How would you design a caching strategy across the full stack (Browser, CDN, API Gateway, Redis, Database) for a high-traffic e-commerce product page?",
            "expected_answer_points": [
                "Browser: Cache-Control headers (stale-while-revalidate)",
                "CDN: Edge caching of static assets and public JSON responses",
                "Application/Redis: Cache-aside or write-through pattern for product details and inventory",
                "Cache invalidation strategy (TTL + event-driven invalidation on price/stock update)",
                "Handling Cache Stampede / Thundering Herd with mutex locks or probabilistic early expiration"
            ],
            "rubric_5": "Comprehensive multi-tier caching blueprint, explicit cache invalidation mechanisms, and handling concurrency/stampede issues.",
            "follow_up": "How does Cache-Aside differ from Write-Through and Write-Behind caching?"
        }
    ],
    "Data Science & Analytics": [
        {
            "topic": "Exploratory Data Analysis & Statistical Testing",
            "skill": "Statistics & EDA",
            "difficulty": "Easy",
            "question": "What is the Central Limit Theorem, and why is it fundamental to hypothesis testing in data science?",
            "expected_answer_points": [
                "Sampling distribution of the sample mean approaches normal distribution as sample size increases, regardless of population distribution shape",
                "Enables parametric tests (Z-test, t-test) and confidence intervals on sample data",
                "Requires independent and identically distributed (i.i.d.) samples and adequate sample size (n >= 30)"
            ],
            "rubric_5": "Articulates sampling distribution vs population distribution, conditions required, and direct application to A/B testing.",
            "follow_up": "When would you choose a non-parametric test (like Mann-Whitney U test) over a standard Student's t-test?"
        },
        {
            "topic": "Data Cleaning & Feature Engineering",
            "skill": "Pandas & Python",
            "difficulty": "Medium",
            "question": "How do you handle high-cardinality categorical variables (e.g., ZIP code, product category) without exploding dimensionality via One-Hot Encoding?",
            "expected_answer_points": [
                "Target Encoding (Mean Encoding) with smoothing / out-of-fold regularization to prevent data leakage",
                "Frequency / Count Encoding",
                "Entity Embeddings (Learned categorical embeddings via neural networks)",
                "Grouping rare categories into an 'Other' bucket"
            ],
            "rubric_5": "Mentions target leakage prevention (cross-validation smoothing, additive smoothing), embeddings, and tree-based native handling (CatBoost/LightGBM).",
            "follow_up": "Why is target encoding prone to overfitting on small categories, and how does Laplace smoothing resolve this?"
        },
        {
            "topic": "A/B Testing & Causal Inference",
            "skill": "Experimentation",
            "difficulty": "Hard",
            "question": "How do you calculate minimum sample size for an A/B test, and how do you guard against Type I (alpha) and Type II (beta) errors?",
            "expected_answer_points": [
                "Power analysis based on baseline conversion rate, Minimum Detectable Effect (MDE), significance level (alpha = 0.05), and statistical power (1 - beta = 0.80)",
                "Avoid peeking problem (continuous monitoring inflating Type I error) using sequential testing or fixed-horizon evaluation",
                "Guard against network effects / spillover bias in randomized assignment"
            ],
            "rubric_5": "Deep understanding of power calculation formula, p-hacking / peeking trap, Bonferroni correction for multiple variants, and variance reduction (CUPED).",
            "follow_up": "What is CUPED (Controlled-experiment Using Pre-Experiment Data) and how does it reduce sample size requirements?"
        }
    ],
    "Cloud & DevOps Engineering": [
        {
            "topic": "Containerization & Docker Fundamentals",
            "skill": "Docker",
            "difficulty": "Easy",
            "question": "What is the difference between a Docker Image and a Docker Container, and how does Docker's layered filesystem work?",
            "expected_answer_points": [
                "Image is a read-only blueprint/snapshot; container is a running runnable instance",
                "Docker uses UnionFS (Overlay2) where each Dockerfile instruction creates a cached layer",
                "Container adds a thin read-write layer on top of immutable image layers",
                "Multi-stage builds reduce final image size and attack surface"
            ],
            "rubric_5": "Explains layer caching, copy-on-write mechanism, multi-stage builds, and container isolation via cgroups and namespaces.",
            "follow_up": "How do Linux namespaces and cgroups provide isolation and resource limitation for Docker containers?"
        },
        {
            "topic": "CI/CD Pipeline Architecture",
            "skill": "CI/CD & GitHub Actions",
            "difficulty": "Medium",
            "question": "Design a secure, robust CI/CD pipeline from code commit to production deployment. What stages and security gates would you include?",
            "expected_answer_points": [
                "Trigger on pull request / main branch merge",
                "Linting, Static Code Analysis (SonarQube), Unit & Integration Tests",
                "Security scans: SAST, Dependency vulnerability scan (Snyk/Trivy), Secret scanning",
                "Container build & artifact signing, push to registry",
                "Staging deployment -> E2E smoke tests -> Manual/Automated canary release to production with rollback triggers"
            ],
            "rubric_5": "Covers shift-left security, automated test gates, environment promotion, artifact immutability, and automated rollback strategies.",
            "follow_up": "How do you securely manage secrets (API keys, DB credentials) within CI/CD runners without exposing them in logs?"
        },
        {
            "topic": "Kubernetes & Infrastructure as Code",
            "skill": "Kubernetes & Terraform",
            "difficulty": "Hard",
            "question": "How does Kubernetes reconcile the Desired State versus Current State, and how do Deployments, ReplicaSets, and Pods interact during a zero-downtime rolling update?",
            "expected_answer_points": [
                "Control plane (kube-controller-manager) runs continuous control loops (reconciliation)",
                "Deployment manages ReplicaSets; rolling update creates a new ReplicaSet and incrementally scales up new pods while scaling down old pods",
                "Readiness and Liveness probes ensure traffic only routes to healthy pods via kube-proxy / CoreDNS",
                "Terraform manages declarative infrastructure state with state locks in remote storage (S3 + DynamoDB)"
            ],
            "rubric_5": "Detailed insight into controller loop, Pod lifecycle, readiness vs liveness probe nuances, and state management in Terraform.",
            "follow_up": "What happens if a pod's liveness probe fails versus when its readiness probe fails?"
        }
    ],
    "Cybersecurity & Information Assurance": [
        {
            "topic": "OWASP Top 10 & Web Vulnerabilities",
            "skill": "Application Security",
            "difficulty": "Easy",
            "question": "What is SQL Injection (SQLi), how does it occur, and what is the primary defensive coding practice to prevent it?",
            "expected_answer_points": [
                "Untrusted user input concatenated directly into dynamic SQL queries",
                "Allows attacker to bypass auth, extract confidential data, or execute arbitrary SQL commands",
                "Defense: Parameterized queries / Prepared statements",
                "Additional defense: ORM usage, input validation, least privilege database user roles"
            ],
            "rubric_5": "Clear explanation of syntax manipulation, why string escaping is fragile, and proper implementation of parameterized queries.",
            "follow_up": "Can SQL injection still occur when using an ORM? If so, give an example scenario."
        },
        {
            "topic": "Cryptography & Public Key Infrastructure",
            "skill": "Cryptography",
            "difficulty": "Medium",
            "question": "Explain the TLS/HTTPS handshake process. How are asymmetric and symmetric encryption combined to establish a secure channel?",
            "expected_answer_points": [
                "ClientHello and ServerHello negotiate cipher suites and TLS version",
                "Server presents digital certificate signed by trusted Certificate Authority (CA)",
                "Asymmetric encryption (RSA or Diffie-Hellman key exchange) securely derives a shared symmetric session key",
                "Symmetric encryption (e.g., AES-GCM) is used for bulk data transfer due to computational efficiency"
            ],
            "rubric_5": "Thorough walk-through of TLS handshake, certificate validation chain, session key derivation, and why symmetric encryption handles data transfer.",
            "follow_up": "What is Perfect Forward Secrecy (PFS), and how does Ephemeral Diffie-Hellman achieve it?"
        }
    ],
    "Mobile App Development (Flutter / Android / iOS)": [
        {
            "topic": "Mobile State Management & Lifecycle",
            "skill": "Flutter / React Native",
            "difficulty": "Easy",
            "question": "Explain the Flutter Widget lifecycle (Stateless vs Stateful) and how state management solutions (like Provider or Bloc) prevent unnecessary rebuilds.",
            "expected_answer_points": [
                "StatelessWidget is immutable; StatefulWidget creates State object persisting across rebuilds",
                "Lifecycle: createState -> initState -> didChangeDependencies -> build -> dispose",
                "setState rebuilds the whole subtree; scoped state (Bloc/Provider/Riverpod) isolates updates to subscribed leaf widgets"
            ],
            "rubric_5": "Accurate lifecycle method ordering, resource disposal practices (controllers/streams), and granular widget rebuilding.",
            "follow_up": "Why is it dangerous to perform async operations or API calls inside the build() method?"
        },
        {
            "topic": "Offline-First Mobile Architecture",
            "skill": "Mobile Architecture",
            "difficulty": "Medium",
            "question": "How do you design an offline-first mobile application that synchronizes local changes (SQLite / Hive / Room) with a remote backend when connectivity resumes?",
            "expected_answer_points": [
                "Local-first repository pattern: UI observes local database reactive streams",
                "Sync manager / background worker queues outgoing mutations with timestamps and UUIDs",
                "Conflict resolution strategy: Last-Write-Wins (LWW), CRDTs, or server-side reconciliation",
                "Network connectivity listener and exponential backoff retry mechanism"
            ],
            "rubric_5": "Explains optimistic UI updates, background sync queues, conflict resolution policies, and handling intermittent network drops.",
            "follow_up": "How would you handle merge conflicts if two users edit the same document offline simultaneously?"
        }
    ],
    "Backend Engineering (Python / Java / Go)": [
        {
            "topic": "Concurrency vs Parallelism & Async I/O",
            "skill": "Async Programming",
            "difficulty": "Medium",
            "question": "What is the difference between Concurrency and Parallelism? How does Python's asyncio event loop handle thousands of concurrent I/O operations despite the GIL?",
            "expected_answer_points": [
                "Concurrency is dealing with lots of things at once (structure); Parallelism is doing lots of things at once (hardware execution)",
                "Python GIL prevents multiple OS threads from executing Python bytecode simultaneously",
                "asyncio uses non-blocking I/O and an event loop with epoll/kqueue to yield control during socket/disk waits",
                "Single thread can manage thousands of concurrent I/O bound tasks efficiently without thread context-switching overhead"
            ],
            "rubric_5": "Articulates event loop mechanics, coroutines/tasks, OS multiplexing (epoll), and contrasts I/O bound vs CPU bound workloads.",
            "follow_up": "When would you use multiprocessing or Celery workers instead of asyncio in Python?"
        },
        {
            "topic": "Message Queues & Distributed Systems",
            "skill": "Distributed Systems",
            "difficulty": "Hard",
            "question": "When would you choose an asynchronous message broker (like RabbitMQ or Apache Kafka) over direct REST HTTP communication between microservices?",
            "expected_answer_points": [
                "Decoupling producer and consumer lifecycles and rates of processing (backpressure & buffering)",
                "Fault tolerance: messages persist in broker queue even if downstream consumer is down",
                "Fan-out / Pub-Sub pattern for 1-to-many event notifications",
                "Kafka: distributed append-only commit log with high throughput and event replay capability"
            ],
            "rubric_5": "Compares synchronous coupling vs asynchronous resilience, explains at-least-once delivery semantics, and idempotent consumer design.",
            "follow_up": "How do you guarantee that a message is processed idempotently if the consumer crashes after processing but before acknowledging?"
        }
    ],
    "Frontend Engineering (React / Next.js / Vue)": [
        {
            "topic": "Web Performance & Core Web Vitals",
            "skill": "Performance Optimization",
            "difficulty": "Medium",
            "question": "What are the three Core Web Vitals (LCP, INP / FID, CLS), and what specific frontend engineering techniques do you use to optimize each?",
            "expected_answer_points": [
                "LCP (Largest Contentful Paint): Optimize image formats (WebP/AVIF), priority hints, preloading key fonts, CDN delivery",
                "INP (Interaction to Next Paint): Break up long JavaScript tasks using Web Workers or requestIdleCallback / scheduler.yield()",
                "CLS (Cumulative Layout Shift): Set explicit width/height on images and video embeds, reserve space for dynamic ads/banners"
            ],
            "rubric_5": "Accurately defines all 3 metrics with thresholds, diagnostic tools (Lighthouse/Chrome DevTools), and actionable code-level fixes.",
            "follow_up": "What is Server-Side Rendering (SSR) vs Static Site Generation (SSG) vs Incremental Static Regeneration (ISR) in Next.js?"
        }
    ]
}

# Behavioral Competencies & STAR Questions Pool
BEHAVIORAL_QUESTIONS_POOL = [
    {
        "competency": "Problem Solving & Technical Agility",
        "description": "Ability to dissect complex, unfamiliar engineering problems and learn rapidly.",
        "difficulty": "Medium",
        "question": "Tell me about a time when you encountered an unexpected bug or roadblock during a project that you had no prior experience with. How did you diagnose and resolve it?",
        "star_framework": {
            "situation": "Context of the challenging technical roadblock or unfamiliar tech stack.",
            "task": "Specific goal or deliverable that was threatened by the issue.",
            "action": "Methodical debugging steps, research, documentation lookup, experimentation, or seeking mentorship.",
            "result": "Resolution outcome, metric improvement, and key takeaways learned."
        },
        "green_flags": [
            "Systematic debugging approach rather than random trial-and-error",
            "Willingness to read source code, official docs, and logs",
            "Proactive knowledge sharing with teammates after fixing"
        ],
        "red_flags": [
            "Blaming tools or teammates",
            "Gave up or waited passively for someone else to fix it",
            "Cannot explain root cause of the issue"
        ],
        "follow_up": "What preventative measures did you put in place (e.g., unit test, linter, validation) to ensure this bug wouldn't happen again?"
    },
    {
        "competency": "Collaboration & Team Communication",
        "description": "Working effectively in cross-functional teams, handling disagreements constructively.",
        "difficulty": "Easy",
        "question": "Describe a situation in a group project or previous role where you had a technical disagreement with a team member. How did you navigate the conversation to reach a consensus?",
        "star_framework": {
            "situation": "Context of the technical conflict or architectural disagreement.",
            "task": "Need to choose an engineering direction without stalling team velocity.",
            "action": "Active listening, objective benchmark comparison / proof-of-concept, finding common ground.",
            "result": "Agreed path forward, healthy team dynamic maintained, successful project delivery."
        },
        "green_flags": [
            "Focuses on data, benchmarks, and project goals rather than personal ego",
            "Listens actively and acknowledges merit in counterpart's perspective",
            "Supports team consensus once decided even if initially differing"
        ],
        "red_flags": [
            "Personalized hostility or stubborn rigidity",
            "Passive-aggressive compliance or disengagement",
            "Unable to articulate why the team chose the ultimate solution"
        ],
        "follow_up": "If the chosen solution later ran into unexpected performance bottlenecks, how did you and your team handle the pivot?"
    },
    {
        "competency": "Ownership & Time Management",
        "description": "Taking initiative, meeting deadlines under constraints, and delivering end-to-end quality.",
        "difficulty": "Medium",
        "question": "Can you share an example of a project where you had to manage tight deadlines with competing priorities? How did you prioritize your tasks and ensure quality delivery?",
        "star_framework": {
            "situation": "High-pressure timeline with multiple deliverables or academic/work overlap.",
            "task": "Delivering high-priority features on time without sacrificing core stability.",
            "action": "Work breakdown structure, MVP scoping, clear communication with stakeholders, ruthless prioritization.",
            "result": "On-time delivery, stakeholder satisfaction, manageable stress."
        },
        "green_flags": [
            "Communicates early when deadlines are at risk",
            "Identifies high-impact Minimum Viable Product (MVP) scope",
            "Demonstrates self-discipline and organized task tracking (Kanban, Jira, Trello)"
        ],
        "red_flags": [
            "Waited until deadline passed to inform stakeholders of delays",
            "Cut corners on security, tests, or documentation without agreement",
            "Lacks systematic prioritization framework"
        ],
        "follow_up": "If a stakeholder requested an urgent last-minute feature 24 hours before release, how would you respond?"
    },
    {
        "competency": "Learning Agility & Curiosity",
        "description": "Eagerness to explore modern technologies, self-directed learning, and staying current.",
        "difficulty": "Easy",
        "question": "What is a new technology, framework, or concept you decided to learn entirely on your own recently? What motivated you and how did you apply it?",
        "star_framework": {
            "situation": "Identifying a knowledge gap or exciting new paradigm in tech.",
            "task": "Self-learning goal and structuring personal learning curve.",
            "action": "Building hands-on sandbox projects, reading documentation, contributing or experimenting.",
            "result": "Applied knowledge in a tangible portfolio project or open-source contribution."
        },
        "green_flags": [
            "Intrinsic passion for computing and continuous self-improvement",
            "Builds practical hands-on projects rather than just passively watching tutorials",
            "Reflects on strengths and trade-offs of the newly learned technology"
        ],
        "red_flags": [
            "Only learns what is strictly mandated by exams or assignments",
            "Superficial buzzword knowledge without hands-on depth",
            "Reluctance to step outside comfortable tech stack"
        ],
        "follow_up": "What was the most surprising nuance or limitation you discovered about that technology while building with it?"
    },
    {
        "competency": "Adaptability & Resilience",
        "description": "Handling shifting requirements, ambiguous specifications, and recovering from failures.",
        "difficulty": "Hard",
        "question": "Tell me about a time when project requirements changed drastically mid-way through development. How did you adapt your architecture and mindset?",
        "star_framework": {
            "situation": "Sudden pivot in client requirements, API specification change, or scope shift.",
            "task": "Refactoring existing code and redesigning components without losing momentum.",
            "action": "Modular architectural design, decoupling components, embracing agile iteration.",
            "result": "Smooth transition, reusable modular components preserved, successful delivery."
        },
        "green_flags": [
            "Embraces change positively as part of software engineering reality",
            "Designs modular, loosely coupled code that facilitates easy refactoring",
            "Maintains constructive attitude during pivots"
        ],
        "red_flags": [
            "Resistant to necessary product changes",
            "Complete emotional collapse or complaints about leadership/clients",
            "Tightly coupled code that required 100% complete rewrite from scratch"
        ],
        "follow_up": "How did that experience change how you design system interfaces and abstractions today?"
    }
]

# -------------------------------------------------------------
# 2. INTERN PROFILES GENERATION (60 Realistic Resumes)
# -------------------------------------------------------------
UNIVERSITIES = [
    "National University of Sciences & Technology (NUST)",
    "FAST National University of Computer & Emerging Sciences",
    "Ghulam Ishaq Khan Institute (GIKI)",
    "Lahore University of Management Sciences (LUMS)",
    "COMSATS University Islamabad",
    "NED University of Engineering & Technology",
    "University of Engineering & Technology (UET) Lahore",
    "Information Technology University (ITU) Lahore",
    "Quaid-i-Azam University",
    "Institute of Business Administration (IBA) Karachi"
]

SKILL_SETS_BY_TRACK = {
    "AI & Machine Learning": [
        ["Python", "PyTorch", "Scikit-Learn", "OpenCV", "Pandas", "NumPy", "TensorFlow", "Transformers", "FastAPI"],
        ["Python", "Machine Learning", "Data Analysis", "Matplotlib", "Seaborn", "XGBoost", "Git", "SQL"],
        ["Python", "Deep Learning", "CNNs", "RNNs", "PyTorch", "Docker", "HuggingFace", "LangChain", "Vector DBs"]
    ],
    "Data Science & Analytics": [
        ["Python", "Pandas", "SQL", "Tableau", "PowerBI", "Statistical Modeling", "A/B Testing", "Scikit-Learn"],
        ["Python", "R", "SQL", "BigQuery", "Data Wrangling", "Machine Learning", "Seaborn", "Excel Analytics"],
        ["Python", "PostgreSQL", "Spark", "PySpark", "Data Pipelines", "Snowflake", "dbt", "Data Modeling"]
    ],
    "Full-Stack Web Development": [
        ["JavaScript", "TypeScript", "React.js", "Node.js", "Express.js", "MongoDB", "TailwindCSS", "REST APIs", "Git"],
        ["Next.js", "React.js", "TypeScript", "PostgreSQL", "Prisma ORM", "Docker", "TailwindCSS", "Redis"],
        ["HTML5/CSS3", "JavaScript", "Python", "Django", "PostgreSQL", "Bootstrap", "REST Framework", "AWS S3"]
    ],
    "Backend Engineering (Python / Java / Go)": [
        ["Python", "FastAPI", "PostgreSQL", "Redis", "Docker", "Celery", "SQLAlchemy", "Pytest", "Git"],
        ["Java", "Spring Boot", "Hibernate", "MySQL", "Microservices", "Kafka", "Docker", "JUnit"],
        ["Go (Golang)", "gRPC", "PostgreSQL", "Docker", "Kubernetes", "Redis", "Goroutines", "REST APIs"]
    ],
    "Frontend Engineering (React / Next.js / Vue)": [
        ["JavaScript (ES6+)", "TypeScript", "React.js", "Next.js", "Tailwind CSS", "Redux Toolkit", "Figma", "Jest"],
        ["Vue.js", "Nuxt.js", "JavaScript", "Pinia", "CSS3 / SASS", "HTML5", "Axios", "Responsive Design"],
        ["React.js", "TypeScript", "Zustand", "Styled Components", "GraphQL", "Storybook", "Webpack / Vite"]
    ],
    "Cloud & DevOps Engineering": [
        ["Linux", "Bash Scripting", "Docker", "Kubernetes", "Terraform", "AWS (EC2, S3, IAM)", "GitHub Actions", "CI/CD"],
        ["Python", "Docker", "Ansible", "Terraform", "Azure", "Prometheus", "Grafana", "GitLab CI"],
        ["Linux", "Kubernetes", "Helm", "GCP", "CI/CD Pipelines", "Docker", "Nginx", "Shell Scripting"]
    ],
    "Cybersecurity & Information Assurance": [
        ["Network Security", "Wireshark", "Linux Administration", "Python Scripting", "OWASP Top 10", "Burp Suite", "Nmap"],
        ["Ethical Hacking", "Metasploit", "Vulnerability Assessment", "Cryptography", "Reverse Engineering", "SIEM (Splunk)"],
        ["Application Security", "SAST / DAST", "SOC Operations", "Penetration Testing", "Security Auditing", "Git"]
    ],
    "Mobile App Development (Flutter / Android / iOS)": [
        ["Flutter", "Dart", "Firebase", "REST APIs", "State Management (Bloc/Provider)", "Git", "SQLite", "UI/UX"],
        ["Kotlin", "Android SDK", "Jetpack Compose", "Coroutines", "Room DB", "Retrofit", "MVVM Architecture"],
        ["Swift", "iOS SDK", "SwiftUI", "Combine", "CoreData", "URLSession", "Xcode", "App Store Deployment"]
    ]
}

PROJECTS_POOL = {
    "AI & Machine Learning": [
        {
            "title": "Medical Imaging Pneumonia Detector with PyTorch",
            "desc": "Fine-tuned ResNet-50 and Vision Transformer architectures on 5,800+ chest X-ray scans with 94.2% sensitivity and Grad-CAM explainability.",
            "tech": ["PyTorch", "Torchvision", "FastAPI", "OpenCV", "Docker"]
        },
        {
            "title": "RAG-Powered Academic Document Assistant",
            "desc": "Built an end-to-end question-answering assistant over 500+ research papers utilizing LangChain, ChromaDB embeddings, and LLaMA-3.",
            "tech": ["Python", "LangChain", "ChromaDB", "HuggingFace", "Streamlit"]
        },
        {
            "title": "Real-time Autonomous Drone Navigation Simulator",
            "desc": "Trained a Deep Q-Network (DQN) reinforcement learning agent in AirSim for obstacle avoidance in cluttered 3D environments.",
            "tech": ["Python", "PyTorch", "Gymnasium", "NumPy", "Matplotlib"]
        }
    ],
    "Full-Stack Web Development": [
        {
            "title": "Collaborative Real-Time Whiteboard & Code Editor",
            "desc": "Architected a multi-user collaborative workspace with WebSocket synchronization, operational transforms, and Monaco editor integration.",
            "tech": ["React.js", "TypeScript", "Node.js", "Socket.io", "Redis", "Docker"]
        },
        {
            "title": "FinTech Micro-Investment & Budgeting Web App",
            "desc": "Engineered full-stack personal finance application with Plaid API integration, automated expense categorization, and JWT authentication.",
            "tech": ["Next.js", "PostgreSQL", "Prisma", "TailwindCSS", "Chart.js", "Jest"]
        },
        {
            "title": "E-Commerce Multi-Vendor Marketplace with Payment Gateways",
            "desc": "Developed complete multi-tenant marketplace platform with Stripe checkout, inventory management, and Redis caching.",
            "tech": ["React", "Express.js", "MongoDB", "Redis", "Stripe API", "AWS S3"]
        }
    ],
    "Data Science & Analytics": [
        {
            "title": "Customer Churn Prediction & Retention Dashboard",
            "desc": "Built predictive XGBoost pipeline predicting telecom subscriber churn (ROC-AUC 0.89) with automated Tableau dashboard.",
            "tech": ["Python", "Pandas", "Scikit-Learn", "XGBoost", "Tableau", "SQL"]
        },
        {
            "title": "Algorithmic Crypto Sentiment & Trading Backtester",
            "desc": "Scraped 2M+ Reddit and Twitter posts with VADER and RoBERTa NLP models to backtest sentiment-driven trading strategies.",
            "tech": ["Python", "HuggingFace", "Pandas", "Statsmodels", "Plotly", "PostgreSQL"]
        }
    ],
    "Cloud & DevOps Engineering": [
        {
            "title": "Multi-Region Kubernetes Microservice Deployment via Terraform",
            "desc": "Provisioned high-availability AWS EKS cluster with Terraform, automated ingress routing via Traefik, and Prometheus monitoring.",
            "tech": ["Terraform", "AWS", "Kubernetes", "Helm", "Prometheus", "GitHub Actions"]
        },
        {
            "title": "GitOps Automated CI/CD Pipeline with ArgoCD",
            "desc": "Designed zero-downtime canary deployment pipeline for 8 microservices with automated security scanning using Trivy.",
            "tech": ["GitHub Actions", "ArgoCD", "Kubernetes", "Docker", "Trivy", "Bash"]
        }
    ],
    "Cybersecurity & Information Assurance": [
        {
            "title": "Automated Network Threat Detection & Honeypot System",
            "desc": "Deployed Cowrie honeypots in AWS to capture and analyze 50,000+ brute-force attempts with automated ELK stack alerting.",
            "tech": ["Python", "ELK Stack", "Suricata", "Wireshark", "Bash", "Linux"]
        }
    ],
    "Mobile App Development (Flutter / Android / iOS)": [
        {
            "title": "Campus Community & Event Management App",
            "desc": "Cross-platform Flutter application for 15,000+ university students with real-time push notifications, QR ticketing, and offline sync.",
            "tech": ["Flutter", "Dart", "Firebase", "Bloc", "Cloud Functions", "SQLite"]
        }
    ],
    "Backend Engineering (Python / Java / Go)": [
        {
            "title": "High-Throughput Asynchronous Task Processing Engine",
            "desc": "Designed a distributed background task engine in Go with Redis queue backend handling 10,000 jobs/sec with graceful shutdown.",
            "tech": ["Go (Golang)", "Redis", "Docker", "PostgreSQL", "Prometheus"]
        }
    ],
    "Frontend Engineering (React / Next.js / Vue)": [
        {
            "title": "Accessible Design System & Component Library",
            "desc": "Created WCAG 2.1 AA compliant UI library with 40+ modular components, Storybook documentation, and automated visual regression testing.",
            "tech": ["React", "TypeScript", "Tailwind CSS", "Storybook", "Jest", "Framer Motion"]
        }
    ]
}

def generate_intern_profiles(num_profiles=60) -> List[Dict[str, Any]]:
    first_names = ["Hamza", "Ayesha", "Bilal", "Zainab", "Ali", "Fatima", "Usman", "Maham", "Saad", "Hira", "Omer", "Maryam", "Ahmed", "Sara", "Hassan", "Khadija", "Mustafa", "Noor", "Daniyal", "Laiba", "Zubair", "Eman", "Farhan", "Rida", "Taha", "Sana", "Waleed", "Anum", "Talha", "Kinza"]
    last_names = ["Khan", "Ahmed", "Malik", "Sheikh", "Chaudhry", "Raza", "Siddiqui", "Farooq", "Baig", "Iqbal", "Bhatti", "Ansari", "Mirza", "Shah", "Abbasi", "Qureshi", "Akram", "Hussain", "Javed", "Nawaz"]
    
    random.seed(42)
    profiles = []
    for i in range(1, num_profiles + 1):
        track = TRACKS[(i - 1) % len(TRACKS)]
        name = f"{random.choice(first_names)} {random.choice(last_names)}"
        uni = random.choice(UNIVERSITIES)
        degree = random.choice(["BS Computer Science", "BS Software Engineering", "BS Artificial Intelligence", "BS Data Science", "BS Cyber Security"])
        gpa = round(random.uniform(3.15, 3.98), 2)
        graduation_year = random.choice([2024, 2025, 2026])
        
        skill_options = SKILL_SETS_BY_TRACK.get(track, SKILL_SETS_BY_TRACK["AI & Machine Learning"])
        skills = random.choice(skill_options)
        # Add 1-2 cross-track skills for realism
        extra_skills = random.sample(["Git", "Linux", "REST APIs", "Agile / Scrum", "Docker", "Problem Solving", "Unit Testing"], k=2)
        all_skills = list(dict.fromkeys(skills + extra_skills))
        
        # Pick 2-3 projects
        track_projects = PROJECTS_POOL.get(track, PROJECTS_POOL["AI & Machine Learning"])
        selected_projects = random.sample(track_projects, k=min(len(track_projects), random.randint(1, 2)))
        
        experience_types = [
            "Final Year Student with 2 Hands-on Production Projects & Open Source Contributions",
            "Junior Developer with 6-Month Previous Web Internship Experience",
            "Undergraduate Researcher with 1 Published Workshop Paper & Kaggle Competitions",
            "Self-Taught Passionate Engineer with active GitHub Portfolio (15+ Repos)",
            "University Coding Club Lead with Hackathon 1st Place Winner experience"
        ]
        
        strengths_list = [
            f"Strong foundations in {track}",
            "Rapid prototyping and self-directed problem solving",
            "Clear technical communication and documentation",
            "Passionate about scalable architecture and clean code",
            "Eager to learn modern enterprise tech stacks"
        ]
        
        areas_to_probe = [
            "In-depth concurrency / memory management trade-offs",
            "Production debugging under high-load failure scenarios",
            "Test-Driven Development (TDD) coverage and CI/CD pipelines",
            "Security best practices and vulnerability mitigation"
        ]
        
        profile = {
            "id": f"INT-{i:03d}",
            "name": name,
            "track": track,
            "email": f"{name.lower().replace(' ', '.')}.{i}@internship.edu.pk",
            "university": uni,
            "degree": degree,
            "gpa": gpa,
            "graduation_year": graduation_year,
            "technical_skills": all_skills,
            "experience_summary": random.choice(experience_types),
            "projects": selected_projects,
            "strengths": random.sample(strengths_list, k=3),
            "areas_to_probe": random.sample(areas_to_probe, k=2),
            "bio": f"{degree} student at {uni} passionate about {track}. Built {len(selected_projects)} major technical projects using {', '.join(all_skills[:4])}."
        }
        profiles.append(profile)
    return profiles

# -------------------------------------------------------------
# 3. JOB DESCRIPTIONS GENERATION (Tech Internship Roles)
# -------------------------------------------------------------
def generate_job_descriptions() -> List[Dict[str, Any]]:
    jds = [
        {
            "id": "JD-AI-01",
            "title": "Machine Learning & AI Engineering Intern",
            "track": "AI & Machine Learning",
            "department": "Applied AI Research & Engineering",
            "experience_level": "Intern / Entry Level",
            "location": "Hybrid / On-site",
            "duration": "3 - 6 Months",
            "overview": "We are seeking a high-caliber ML Intern to join our AI team. You will build, fine-tune, and evaluate deep learning models, deploy RAG pipelines, and integrate state-of-the-art vision/NLP architectures into production microservices.",
            "required_skills": ["Python", "PyTorch", "Scikit-Learn", "FastAPI", "Pandas", "NumPy", "Git"],
            "preferred_skills": ["Transformers", "LangChain", "Vector DBs", "Docker", "MLOps", "OpenCV"],
            "responsibilities": [
                "Develop and benchmark machine learning models on structured and unstructured datasets.",
                "Implement retrieval-augmented generation (RAG) pipelines for enterprise knowledge search.",
                "Optimize model inference latency and package models inside Docker containers.",
                "Collaborate with backend engineers to integrate RESTful AI inference endpoints."
            ],
            "competency_focus": ["Problem Solving & Technical Agility", "Learning Agility & Curiosity", "Ownership & Time Management"]
        },
        {
            "id": "JD-FS-02",
            "title": "Full-Stack Web Development Intern (React + Node / Python)",
            "track": "Full-Stack Web Development",
            "department": "Platform Engineering",
            "experience_level": "Intern / Entry Level",
            "location": "Remote / Hybrid",
            "duration": "3 Months",
            "overview": "Join our fast-paced product engineering team to build scalable, responsive web applications. You will contribute to frontend React/Next.js interfaces, RESTful microservices, and database optimizations.",
            "required_skills": ["JavaScript", "TypeScript", "React.js", "Node.js", "PostgreSQL", "REST APIs", "Git"],
            "preferred_skills": ["Next.js", "Docker", "Redis", "TailwindCSS", "Prisma ORM", "GraphQL"],
            "responsibilities": [
                "Build reusable, accessible, and responsive UI components using React and modern CSS.",
                "Develop and maintain robust backend API endpoints with data validation and authentication.",
                "Design normalized relational database schemas and optimize SQL query performance.",
                "Write automated unit and integration tests to ensure high code quality."
            ],
            "competency_focus": ["Collaboration & Team Communication", "Ownership & Time Management", "Adaptability & Resilience"]
        },
        {
            "id": "JD-DS-03",
            "title": "Data Science & Analytics Intern",
            "track": "Data Science & Analytics",
            "department": "Business Intelligence & Data Insights",
            "experience_level": "Intern / Entry Level",
            "location": "On-site / Hybrid",
            "duration": "3 - 6 Months",
            "overview": "Looking for an analytical Data Science Intern to uncover actionable patterns from large-scale user datasets, build predictive churn/retention models, and create executive dashboards.",
            "required_skills": ["Python", "SQL", "Pandas", "Scikit-Learn", "Statistical Modeling", "Data Visualization"],
            "preferred_skills": ["Tableau", "PowerBI", "A/B Testing", "BigQuery", "XGBoost", "dbt"],
            "responsibilities": [
                "Extract, clean, and transform multi-source data using SQL and Pandas.",
                "Perform exploratory data analysis (EDA) and formulate testable statistical hypotheses.",
                "Build baseline machine learning models to forecast business KPIs and user behavior.",
                "Design intuitive visual dashboards in Tableau/PowerBI for cross-functional stakeholders."
            ],
            "competency_focus": ["Problem Solving & Technical Agility", "Collaboration & Team Communication"]
        },
        {
            "id": "JD-DO-04",
            "title": "Cloud & DevOps Engineering Intern",
            "track": "Cloud & DevOps Engineering",
            "department": "Infrastructure & Reliability",
            "experience_level": "Intern / Entry Level",
            "location": "Remote",
            "duration": "3 - 6 Months",
            "overview": "Accelerate our engineering velocity by automating CI/CD delivery pipelines, managing containerized Kubernetes clusters, and codifying cloud infrastructure using Terraform.",
            "required_skills": ["Linux", "Docker", "Bash Scripting", "Git", "CI/CD Pipelines", "Networking Fundamentals"],
            "preferred_skills": ["Kubernetes", "AWS (EC2, S3, IAM)", "Terraform", "Prometheus", "Helm", "GitHub Actions"],
            "responsibilities": [
                "Maintain and optimize automated GitHub Actions CI/CD workflows.",
                "Containerize microservices and write hardened multi-stage Dockerfiles.",
                "Assist in monitoring cluster health, uptime, and alerting configurations.",
                "Write Infrastructure as Code (IaC) templates for automated environment provisioning."
            ],
            "competency_focus": ["Adaptability & Resilience", "Problem Solving & Technical Agility", "Ownership & Time Management"]
        },
        {
            "id": "JD-BE-05",
            "title": "Backend Engineering Intern (FastAPI / Spring Boot / Go)",
            "track": "Backend Engineering (Python / Java / Go)",
            "department": "Core Systems & APIs",
            "experience_level": "Intern / Entry Level",
            "location": "Hybrid",
            "duration": "3 Months",
            "overview": "Build high-concurrency, fault-tolerant backend services that power our core platform. You will handle database transactions, message queues, and API gateways.",
            "required_skills": ["Python", "PostgreSQL", "REST APIs", "Docker", "Git", "Data Structures"],
            "preferred_skills": ["Redis", "FastAPI", "Kafka", "Pytest", "gRPC"],
            "responsibilities": [
                "Design and document secure, high-throughput REST and gRPC API endpoints.",
                "Implement asynchronous task processing and background worker queues.",
                "Optimize database queries, connection pooling, and multi-level caching.",
                "Conduct code reviews and follow strict test-driven development methodologies."
            ],
            "competency_focus": ["Problem Solving & Technical Agility", "Ownership & Time Management"]
        },
        {
            "id": "JD-FE-06",
            "title": "Frontend Engineering Intern (React / Next.js / Vue)",
            "track": "Frontend Engineering (React / Next.js / Vue)",
            "department": "User Experience & Web Applications",
            "experience_level": "Intern / Entry Level",
            "location": "Remote / Hybrid",
            "duration": "3 Months",
            "overview": "Craft delightful, lightning-fast user interfaces. You will translate Figma wireframes into pixel-perfect, accessible, and performant web applications.",
            "required_skills": ["JavaScript", "TypeScript", "React.js", "HTML5/CSS3", "Responsive Design", "Git"],
            "preferred_skills": ["Next.js", "Tailwind CSS", "Redux", "Web Vitals Optimization", "Storybook"],
            "responsibilities": [
                "Build stateful frontend components with responsive layout across all device screens.",
                "Optimize Core Web Vitals (LCP, CLS, INP) for peak rendering performance.",
                "Integrate with backend GraphQL and REST APIs with graceful error handling.",
                "Ensure WCAG 2.1 AA accessibility compliance across all UI components."
            ],
            "competency_focus": ["Collaboration & Team Communication", "Learning Agility & Curiosity"]
        },
        {
            "id": "JD-CY-07",
            "title": "Cybersecurity & Information Security Intern",
            "track": "Cybersecurity & Information Assurance",
            "department": "InfoSec & Compliance",
            "experience_level": "Intern / Entry Level",
            "location": "On-site",
            "duration": "3 - 6 Months",
            "overview": "Protect mission-critical infrastructure against emerging vulnerabilities. You will perform vulnerability scans, code audits, network traffic analysis, and assist in incident response.",
            "required_skills": ["Linux", "Network Security", "OWASP Top 10", "Python Scripting", "Wireshark"],
            "preferred_skills": ["Burp Suite", "SAST / DAST", "SOC Alerting", "Metasploit", "Cryptography"],
            "responsibilities": [
                "Execute automated and manual vulnerability assessments across web applications.",
                "Analyze network packets and security logs for anomalous threat behavior.",
                "Assist software engineers in remediating identified security vulnerabilities.",
                "Draft security incident documentation and employee awareness guidelines."
            ],
            "competency_focus": ["Problem Solving & Technical Agility", "Adaptability & Resilience"]
        },
        {
            "id": "JD-MO-08",
            "title": "Mobile App Development Intern (Flutter / Kotlin / Swift)",
            "track": "Mobile App Development (Flutter / Android / iOS)",
            "department": "Consumer Mobile Apps",
            "experience_level": "Intern / Entry Level",
            "location": "Hybrid",
            "duration": "3 Months",
            "overview": "Build intuitive, smooth mobile applications used by thousands of daily active users. You will write clean mobile code, implement state management, and integrate native device APIs.",
            "required_skills": ["Flutter", "Dart", "Mobile UI Design", "REST APIs", "Git", "SQLite"],
            "preferred_skills": ["Bloc", "Firebase", "Push Notifications", "App Store Deployment"],
            "responsibilities": [
                "Develop fluid mobile screens and animations adhering to Material Design / iOS Human Interface Guidelines.",
                "Implement offline-first data caching and robust synchronization mechanisms.",
                "Diagnose and fix mobile memory leaks, frame drops, and battery drain issues.",
                "Collaborate with backend engineers to integrate push notifications and real-time sockets."
            ],
            "competency_focus": ["Learning Agility & Curiosity", "Collaboration & Team Communication"]
        }
    ]
    return jds

def build_full_question_bank() -> List[Dict[str, Any]]:
    """Builds a rich bank of 1000+ questions by expanding base templates with parameterization."""
    bank = []
    q_id = 1
    
    # 1. Add handcrafted deep questions
    for track, q_list in TECH_QUESTIONS_POOL.items():
        for q in q_list:
            bank.append({
                "id": f"Q-TECH-{q_id:04d}",
                "type": "Technical",
                "track": track,
                "topic": q["topic"],
                "skill": q["skill"],
                "difficulty": q["difficulty"],
                "question": q["question"],
                "expected_answer_points": q["expected_answer_points"],
                "rubric_5": q["rubric_5"],
                "follow_up": q["follow_up"]
            })
            q_id += 1

    # 2. Add behavioral questions
    b_id = 1
    for bq in BEHAVIORAL_QUESTIONS_POOL:
        bank.append({
            "id": f"Q-BEH-{b_id:04d}",
            "type": "Behavioral",
            "track": "General Engineering / Cross-Track",
            "topic": bq["competency"],
            "skill": bq["competency"],
            "difficulty": bq["difficulty"],
            "question": bq["question"],
            "expected_answer_points": [
                f"Situation: {bq['star_framework']['situation']}",
                f"Task: {bq['star_framework']['task']}",
                f"Action: {bq['star_framework']['action']}",
                f"Result: {bq['star_framework']['result']}"
            ],
            "rubric_5": f"Full STAR alignment: demonstrates concrete actions taken, measurable impact, team reflection. Green flags: {', '.join(bq['green_flags'][:2])}",
            "follow_up": bq["follow_up"],
            "green_flags": bq["green_flags"],
            "red_flags": bq["red_flags"]
        })
        b_id += 1

    # 3. Add generated parameterized questions across subdomains to reach comprehensive bank depth (1000+ total)
    subtopics = {
        "AI & Machine Learning": [
            ("Convolutional Neural Networks", "Computer Vision", ["Feature maps", "Pooling layers", "Receptive field", "Filter kernels"]),
            ("Loss Functions", "Deep Learning", ["Cross-Entropy vs MSE", "Hinge Loss", "Focal Loss for imbalanced data", "Differentiability"]),
            ("Optimization Algorithms", "Deep Learning", ["Adam vs SGD with Momentum", "RMSprop", "Learning rate scheduling", "Weight decay"]),
            ("Recurrent Architectures", "NLP", ["Vanishing gradients in standard RNN", "LSTM forget gates", "GRU simplifications", "Hidden states"]),
            ("Vector Databases & Embeddings", "Generative AI", ["Cosine distance vs dot product", "HNSW indexing", "FAISS clustering", "Dimensionality"]),
            ("Model Quantization & Pruning", "Edge AI", ["FP16 vs INT8 quantization", "Weight pruning", "Inference speedup", "Perplexity trade-off"]),
            ("Hyperparameter Tuning", "Machine Learning", ["Grid Search vs Random Search", "Bayesian Optimization (Optuna)", "Cross-validation folds", "Early stopping"]),
            ("Feature Selection Techniques", "Data Modeling", ["Variance thresholding", "Mutual information", "Recursive feature elimination (RFE)", "Correlation matrices"]),
            ("Unsupervised Clustering", "Machine Learning", ["K-Means elbow method", "DBSCAN density parameters", "Hierarchical clustering", "Silhouette score"]),
            ("Transformer Positional Encodings", "NLP", ["Sinusoidal encodings", "Rotary Position Embeddings (RoPE)", "Context length extrapolation", "Attention mask"])
        ],
        "Full-Stack Web Development": [
            ("Async JavaScript & Event Loop", "JavaScript", ["Call stack", "Callback queue vs Microtask queue", "Promises vs async/await", "Non-blocking execution"]),
            ("React Hooks & Memory Leaks", "React.js", ["useEffect cleanup functions", "useRef for mutable references", "Stale closures", "Dependency array gotchas"]),
            ("Cross-Origin Resource Sharing (CORS)", "Web Security", ["Preflight OPTIONS requests", "Access-Control-Allow-Origin headers", "Credentials mode", "Same-origin policy"]),
            ("Server-Side Rendering (SSR) vs Hydration", "Next.js", ["HTML streaming", "Client hydration errors", "Static generation", "Bundle size impact"]),
            ("Database Normalization vs Denormalization", "SQL Databases", ["1NF, 2NF, 3NF forms", "Read vs Write performance", "Redundant columns", "Data integrity"]),
            ("WebSockets vs Server-Sent Events (SSE)", "Real-time Web", ["Bi-directional full duplex", "Uni-directional streaming", "Connection overhead", "Heartbeat mechanisms"]),
            ("GraphQL vs REST Architecture", "API Design", ["Over-fetching and under-fetching", "Schema definition language (SDL)", "N+1 query problem in resolvers", "Caching complexity"]),
            ("Micro-Frontends & Module Federation", "Frontend Architecture", ["Webpack 5 Module Federation", "Independent deployment", "Shared runtime dependencies", "CSS isolation"]),
            ("Content Delivery Networks & Edge Functions", "Web Infrastructure", ["Edge caching", "TTL headers", "Cloudflare Workers / Vercel Edge", "Latency reduction"]),
            ("Database Transaction Isolation Levels", "Databases", ["Read Uncommitted", "Read Committed", "Repeatable Read", "Serializable & Dirty/Phantom reads"])
        ],
        "Data Science & Analytics": [
            ("P-Values & Hypothesis Testing", "Statistics", ["Null hypothesis formulation", "Significance threshold (alpha)", "Confidence intervals", "Type I and Type II errors"]),
            ("Handling Missing Data", "Data Wrangling", ["MCAR, MAR, MNAR mechanisms", "Mean/Median imputation vs KNN/MICE", "Indicator flags", "Data leakage"]),
            ("Dimension Reduction (PCA & t-SNE)", "Unsupervised Learning", ["Eigenvectors & Eigenvalues", "Variance explained ratio", "Global vs Local manifold preservation", "Standardization necessity"]),
            ("Time Series Decomposition", "Time Series", ["Trend, Seasonality, Residuals", "Stationarity & ADF test", "ARIMA / SARIMA models", "Autocorrelation function (ACF)"]),
            ("SQL Window Functions", "SQL Analytics", ["ROW_NUMBER vs RANK vs DENSE_RANK", "PARTITION BY and ORDER BY", "LEAD and LAG for time shifts", "Running totals"]),
            ("Data Warehousing & Star Schema", "Data Engineering", ["Fact tables vs Dimension tables", "Slowly Changing Dimensions (SCD Type 1/2)", "Columnar storage", "OLAP vs OLTP"]),
            ("Model Explainability (SHAP & LIME)", "Explainable AI", ["Shapley values from game theory", "Local feature contributions", "Global feature importance", "Model debugging"]),
            ("Ensemble Methods (Bagging vs Boosting)", "Machine Learning", ["Random Forest variance reduction", "Gradient Boosting bias reduction", "Sequential vs Parallel training", "Learning rate shrinkage"]),
            ("Resampling & Bootstrap Methods", "Statistics", ["Bootstrapping confidence intervals", "Out-of-bag error estimation", "Stratified K-Fold CV", "Sampling with replacement"]),
            ("Data Pipeline Orchestration", "Data Ops", ["Directed Acyclic Graphs (DAGs)", "Idempotent tasks", "Backfilling historical data", "Airflow / Prefect basics"])
        ],
        "Cloud & DevOps Engineering": [
            ("Kubernetes Ingress & Services", "Kubernetes", ["ClusterIP vs NodePort vs LoadBalancer", "Ingress controllers (Nginx/Traefik)", "TLS termination", "Service discovery"]),
            ("Infrastructure as Code State Drift", "Terraform", ["terraform plan vs apply", "Remote state locking", "Importing existing resources", "Drift detection"]),
            ("Immutable Infrastructure vs Mutable", "Cloud Architecture", ["Golden AMI / Container images", "Configuration drift prevention", "Rollback reliability", "Blue-Green upgrades"]),
            ("Observability: Metrics, Logs & Traces", "Monitoring", ["OpenTelemetry standards", "Prometheus pull vs push model", "Distributed tracing (Jaeger)", "Structured JSON logging"]),
            ("Secrets Management in the Cloud", "Cloud Security", ["AWS Secrets Manager / HashiCorp Vault", "Dynamic ephemeral credentials", "KMS envelope encryption", "RBAC policies"]),
            ("Docker Multi-Stage Builds", "Docker", ["Build environment vs runtime environment", "Minimal base images (Alpine/Distroless)", "Layer caching order", "Attack surface reduction"]),
            ("Load Balancing Algorithms", "Networking", ["Round-Robin vs Least Connections", "IP Hash session persistence", "Health check probes", "Layer 4 vs Layer 7"]),
            ("Disaster Recovery & RPO / RTO", "Site Reliability", ["Recovery Point Objective (data loss limit)", "Recovery Time Objective (downtime limit)", "Multi-region backup replication", "Failover routing"]),
            ("GitOps Workflow with ArgoCD", "DevOps", ["Declarative cluster state in Git", "Automated synchronization", "Self-healing reconciliation", "Zero manual kubectl access"]),
            ("Linux Process & Memory Management", "Linux", ["Virtual memory & Swap", "OOM Killer mechanics", "signals (SIGTERM vs SIGKILL)", "top/htop diagnostics"])
        ],
        "Cybersecurity & Information Assurance": [
            ("Cross-Site Scripting (XSS)", "AppSec", ["Stored vs Reflected vs DOM-based XSS", "Content Security Policy (CSP)", "Contextual output encoding", "HttpOnly cookies"]),
            ("Cross-Site Request Forgery (CSRF)", "AppSec", ["CSRF token validation", "SameSite cookie attribute (Strict/Lax)", "Re-authentication for sensitive actions", "Origin/Referer headers"]),
            ("Zero Trust Security Architecture", "Security Architecture", ["Never trust, always verify", "Micro-segmentation", "Continuous identity verification", "Least-privilege access"]),
            ("Authentication Protocols (OAuth 2.0 & OIDC)", "Identity & Access", ["Authorization code flow with PKCE", "Access tokens vs ID tokens", "Scope authorization", "Token refresh lifecycle"]),
            ("Denial of Service (DDoS) Mitigation", "Network Security", ["SYN flood vs HTTP flood", "Rate limiting & IP throttling", "Cloudflare WAF / Anycast routing", "SYN cookies"]),
            ("Public Key Infrastructure & Certificate Revocation", "Cryptography", ["CRL (Certificate Revocation List)", "OCSP Stapling", "Certificate pinning", "Root of trust / Intermediate CAs"]),
            ("Security Information & Event Management (SIEM)", "SOC Operations", ["Log ingestion & normalization", "Correlation rules", "False positive reduction", "Incident response playbooks"]),
            ("Buffer Overflow & Memory Safety", "System Security", ["Stack smashing & return address overwrite", "ASLR and DEP / NX bit protections", "Memory-safe languages (Rust/Go)", "Canary values"])
        ],
        "Mobile App Development (Flutter / Android / iOS)": [
            ("Mobile App Memory Optimization", "Mobile Performance", ["Image caching & downsampling", "Retain cycles & memory leaks", "Profiler analysis", "Garbage collection in mobile runtimes"]),
            ("Push Notifications Architecture", "Mobile Engineering", ["APNs / FCM push payloads", "Background message handling", "Notification channels in Android", "Token registration"]),
            ("App Startup Time Optimization", "Mobile Performance", ["Cold start vs Warm start", "Deferred initialization", "App bundle size optimization", "Splash screen best practices"]),
            ("Mobile Deep Linking & Universal Links", "Mobile UX", ["Custom URI schemes vs App Links", "Routing parameter parsing", "Intent filters", "Fallback web routing"]),
            ("Secure Mobile Storage", "Mobile Security", ["Android EncryptedSharedPreferences / Keystore", "iOS Keychain Services", "Biometric authentication APIs", "Root/Jailbreak detection"]),
            ("Dependency Injection in Mobile Apps", "Architecture", ["Hilt / Dagger in Android", "GetIt / Injectable in Flutter", "Swinject in iOS", "Testability and decoupling"])
        ],
        "Backend Engineering (Python / Java / Go)": [
            ("Database Connection Pooling", "Backend Performance", ["Max connections vs active pool", "HikariCP / SQLAlchemy pool size", "Connection leak diagnosis", "Timeout configurations"]),
            ("Rate Limiting Algorithms", "API Design", ["Token Bucket vs Leaky Bucket", "Fixed Window vs Sliding Window Counter", "Distributed rate limiting with Redis", "HTTP 429 Too Many Requests"]),
            ("CAP Theorem & Distributed Databases", "Distributed Systems", ["Consistency vs Availability vs Partition Tolerance", "Eventual consistency", "PACELC theorem", "Cassandra vs PostgreSQL"]),
            ("Idempotency Keys in Payment APIs", "API Architecture", ["Unique idempotency key header", "Atomic DB insert/lock in Redis", "Returning cached response on replay", "Safe retry mechanisms"]),
            ("Database Read Replicas & CQRS", "Database Architecture", ["Master-slave replication lag", "Command Query Responsibility Segregation", "Read-heavy workload scaling", "Routing queries to replicas"]),
            ("Garbage Collection Tuning", "Runtime Internals", ["JVM Generational GC (G1GC / ZGC)", "Go non-generational concurrent GC", "Python reference counting + cycle detector", "Stop-the-world pauses"])
        ],
        "Frontend Engineering (React / Next.js / Vue)": [
            ("CSS Architecture & Specificity", "CSS/Styles", ["CSS Modules vs Styled Components vs Tailwind", "BEM naming convention", "Cascade specificity scoring", "Critical CSS inlining"]),
            ("Web Workers & Multithreading in Browser", "Performance", ["Offloading heavy computation from UI thread", "postMessage API communication", "SharedArrayBuffer", "Transferable objects"]),
            ("Client-Side Routing & Code Splitting", "Frontend Architecture", ["Dynamic import() and React.lazy", "Route-based vs Component-based splitting", "History API pushState", "Prefetching on hover"]),
            ("Internationalization (i18n) & Localization", "Frontend Engineering", ["RTL layout mirroring (dir=rtl)", "Pluralization & number formatting", "Dynamic locale bundle loading", "Accessibility labeling"])
        ]
    }

    diffs = ["Easy", "Medium", "Hard"]
    question_templates = [
        "How would you explain {topic} to a junior engineer, and what are its key architectural components ({pts})?",
        "In a high-scale production system, what common pitfalls arise when implementing {topic}, and how do you mitigate them?",
        "Can you compare {topic} with alternative approaches, detailing the specific performance and maintainability trade-offs?",
        "Walk me through how you would troubleshoot a performance bottleneck related to {topic} in an enterprise application.",
        "What key best practices and metrics should an engineering team monitor when deploying features utilizing {topic}?"
    ]

    for track, topic_tuples in subtopics.items():
        for topic_name, skill_name, points in topic_tuples:
            for d_idx, diff in enumerate(diffs):
                for t_idx, tmpl in enumerate(question_templates):
                    q_text = tmpl.format(topic=topic_name, pts=", ".join(points[:3]))
                    exp_pts = [f"Mastery of {p}" for p in points] + ["Clear trade-off reasoning", "Practical implementation awareness"]
                    rubric = f"Candidate articulates {topic_name} fundamentals, discusses {points[0]} and {points[1]}, and recognizes production constraints."
                    follow = f"If you had to scale or optimize {topic_name} under 10x traffic volume, what would be your first engineering step?"
                    
                    bank.append({
                        "id": f"Q-GEN-{q_id:04d}",
                        "type": "Technical",
                        "track": track,
                        "topic": topic_name,
                        "skill": skill_name,
                        "difficulty": diff,
                        "question": q_text,
                        "expected_answer_points": exp_pts,
                        "rubric_5": rubric,
                        "follow_up": follow
                    })
                    q_id += 1

    return bank

# -------------------------------------------------------------
# 4. COMPETENCY & SCORING FRAMEWORK
# -------------------------------------------------------------
COMPETENCY_FRAMEWORK = {
    "rubric_scale": {
        "1": "Unsatisfactory: Lacks basic conceptual understanding, cannot explain fundamental terms, offers incorrect or misleading explanations.",
        "2": "Basic / Developing: Superficial knowledge of terminology, struggles to apply concepts to practical scenarios, misses key constraints.",
        "3": "Competent / Solid: Solid grasp of core concepts, provides accurate explanations, demonstrates practical coding and debugging logic.",
        "4": "Advanced / Strong: Deep technical comprehension, discusses trade-offs proactively, references best practices and production edge cases.",
        "5": "Exceptional / Expert: Outstanding mastery, connects theory to high-scale architecture, articulates nuanced trade-offs, shows engineering leadership."
    },
    "behavioral_competencies": [
        {
            "name": "Problem Solving & Technical Agility",
            "definition": "Ability to dissect complex, ambiguous problems, debug methodically, and absorb unfamiliar technologies swiftly.",
            "star_guidelines": "Look for logical root-cause analysis, use of telemetry/logs, structured experimentation, and tangible lessons learned."
        },
        {
            "name": "Collaboration & Team Communication",
            "definition": "Working effectively with peers, resolving technical disagreements constructively, and communicating complex ideas clearly.",
            "star_guidelines": "Look for active listening, willingness to build consensus through data/benchmarks, and respect for teammates."
        },
        {
            "name": "Ownership & Accountability",
            "definition": "Taking end-to-end responsibility for deliverables, meeting commitments, and proactively unblocking blockers.",
            "star_guidelines": "Look for self-initiative, early communication of risks, and commitment to code quality and testing."
        },
        {
            "name": "Learning Agility & Curiosity",
            "definition": "Intrinsic drive to explore emerging tools, read documentation, and expand engineering horizons.",
            "star_guidelines": "Look for self-directed side projects, curiosity about inner mechanics, and rapid uptake of feedback."
        },
        {
            "name": "Adaptability & Resilience",
            "definition": "Gracefully pivoting when project requirements shift, handling constructive feedback, and recovering from failures.",
            "star_guidelines": "Look for calm problem re-scoping, modular code adaptability, and a growth mindset."
        }
    ]
}

def main():
    print("Generating comprehensive dataset for Task 4 Interview Question Generator...")
    
    # 1. Question Bank
    questions = build_full_question_bank()
    with open("data/question_banks.json", "w", encoding="utf-8") as f:
        json.dump(questions, f, indent=2)
    
    # CSV export of question bank
    with open("data/question_banks.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["id", "type", "track", "topic", "skill", "difficulty", "question", "expected_answer_points", "rubric_5", "follow_up"])
        for q in questions:
            writer.writerow([
                q.get("id", ""),
                q.get("type", ""),
                q.get("track", ""),
                q.get("topic", ""),
                q.get("skill", ""),
                q.get("difficulty", ""),
                q.get("question", ""),
                " | ".join(q.get("expected_answer_points", [])),
                q.get("rubric_5", ""),
                q.get("follow_up", "")
            ])
    print(f"Generated {len(questions)} categorized questions in 'data/question_banks.json' & 'data/question_banks.csv'.")
    
    # 2. Intern Profiles
    profiles = generate_intern_profiles(num_profiles=60)
    with open("data/intern_profiles.json", "w", encoding="utf-8") as f:
        json.dump(profiles, f, indent=2)
    print(f"Generated {len(profiles)} realistic intern profiles in 'data/intern_profiles.json'.")
    
    # 3. Job Descriptions
    jds = generate_job_descriptions()
    with open("data/job_descriptions.json", "w", encoding="utf-8") as f:
        json.dump(jds, f, indent=2)
    print(f"Generated {len(jds)} tech internship job descriptions in 'data/job_descriptions.json'.")
    
    # 4. Competency Framework
    with open("data/competency_framework.json", "w", encoding="utf-8") as f:
        json.dump(COMPETENCY_FRAMEWORK, f, indent=2)
    print("Saved competency and rubric framework in 'data/competency_framework.json'.")

if __name__ == "__main__":
    main()
