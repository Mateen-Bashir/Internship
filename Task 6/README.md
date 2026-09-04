# AI Chatbot for Intern Query Support - Internee.pk (Task 6)

An intelligent, real-time AI Chatbot and Support Management system built specifically for **Internee.pk** to automate responses to intern queries, provide 24/7 technical guidance, and streamline support ticket escalations.

---

## Key Features

1. **Dual NLP & Semantic Retrieval Engine**:
   - Indexed knowledge base of **FAQ documents** (task submissions, deadlines, grading rubric, certificate policies, exam freeze leave, mentorship).
   - Embedded corpus of **historical support tickets** to quickly resolve common technical pitfalls (403 Forbidden, Git LFS, Discord invite expiration, certificate re-issuance).
   - High-performance semantic similarity scoring with TF-IDF sublinear n-grams and cosine distance.
   - Smart intent classification across key domains: *Task Submission*, *Certificates & Verification*, *Account & Portal*, *Mentorship & Community*, *Technical Setup*, and *General Policies*.

2. **Automated Escalation & Fallback System**:
   - Dynamic confidence thresholding:
     - **High Confidence**: Instant resolution with step-by-step guidance and official portal links.
     - **Medium Confidence**: Helpful answer with clarification prompts.
     - **Low / Out-of-domain**: Contextual fallback with one-click support ticket escalation.

3. **Modern Glassmorphic Web Interface**:
   - **Live AI Chat**: Real-time messaging, typing indicators, quick prompt chips, markdown formatting, copy-to-clipboard, and feedback ratings.
   - **Knowledge Base Explorer**: Categorized FAQ cards with real-time text filter and category pills.
   - **Support Ticket Desk**: Interactive table of intern tickets with priority badges, status controls, and resolution toggles.
   - **Coordinator AI Intelligence Hub**: Live query activity feed, resolution percentage metrics, and ticket volume breakdown by topic.

4. **FastAPI High-Performance Backend**:
   - REST API endpoints for chat completions, dynamic suggestion generation, ticket creation, status updates, and session analytics.

---

## System Architecture

```
d:\Internee.pk\Task 6\
│
├── data/
│   ├── faq_data.json             # Curated FAQ documents with keywords & answers
│   ├── historical_tickets.json   # Resolved historical support ticket corpus
│   └── active_tickets.json       # Live ticket tracking store
│
├── src/
│   ├── app.py                    # FastAPI server & static file host
│   ├── nlp_engine.py             # NLP semantic search, intent classifier & fallback logic
│   └── ticket_manager.py         # Ticket lifecycle management & analytics generator
│
├── static/
│   ├── index.html                # Modern single-page web app layout
│   ├── style.css                 # Glassmorphic dark theme & animations
│   └── app.js                    # Reactive frontend controller & API client
│
├── tests/
│   └── test_nlp.py               # Unit tests for NLP matching and ticket flows
│
└── README.md                     # Project documentation
```

---

## API Reference

| Endpoint | Method | Description |
|---|---|---|
| `/api/chat` | `POST` | Processes intern query, computes similarity & returns automated response |
| `/api/suggestions` | `GET` | Returns curated prompt chips for common queries |
| `/api/faqs` | `GET` | Returns all categorized FAQ documents |
| `/api/tickets` | `GET` / `POST` | Lists all support tickets or creates a new escalated ticket |
| `/api/tickets/update` | `POST` | Updates ticket status (Open, In Progress, Resolved) |
| `/api/analytics` | `GET` | Fetches coordinator metrics, resolution rate, and activity feed |
| `/api/health` | `GET` | System health and indexed document counters |

---

## Quickstart & Local Execution

### 1. Requirements
Ensure Python 3.10+ is installed with dependencies:
```bash
pip install fastapi uvicorn scikit-learn numpy pydantic
```

### 2. Run the Unit Tests
```bash
python -m unittest tests/test_nlp.py
```

### 3. Launch the Server
```bash
uvicorn src.app:app --host 127.0.0.1 --port 8000
```
Open your browser and navigate to: **`http://127.0.0.1:8000`**

---

## Verification & Test Results
- **Unit Tests**: Passed 5/5 automated test suites covering submission query intent, certificate queries, historical ticket matches, fallback triggers, and ticket creation.
- **Integration Tests**: Validated live query resolution, ticket creation (`TCK-1009`), and real-time coordinator analytics updates.
