# AI-Based Job Recommendation System

An AI-powered **web application** built with **FastAPI**, **Scikit-learn**, and **Pandas** that recommends suitable job roles to candidates based on their skill set.

The system utilizes **TF-IDF (Term Frequency - Inverse Document Frequency) Vectorization** and **Cosine Similarity** to compute match percentage scores between user skills and job profiles while performing missing skill gap analysis.

---

## Key Features

* **AI-Powered Skill Matching**: Uses TF-IDF vectorization and Cosine Similarity for intelligent text representation and ranking.
* **Match Percentage Score**: Displays precision similarity scores (0% to 100%) for each job profile.
* **Missing Skill Gap Analysis**: Dynamically identifies skills required by a job role that are absent from the user's current profile.
* **PDF Resume Upload**: Extracts skills automatically from uploaded PDF resumes.
* **Preset Candidate Personas**: Pre-filled profile templates (Data Scientist, Frontend Dev, DevOps Engineer, Security Analyst).
* **Interactive Skill Selector**: Multi-select dropdown combined with custom free-text input.
* **Interactive Filters**: Filter by Job Category, Experience Level, Location, Top N count, and Minimum Similarity Threshold.
* **Analytics & Visualizations**: Interactive Chart.js charts for match scores and missing skill frequency.
* **Full Dataset Explorer**: Searchable table of all available job listings.
* **Saved Jobs**: Bookmark jobs with persistent local storage.

---

## System Architecture

```
┌─────────────────────────────────────────────────────────┐
│                    Browser (Frontend)                    │
│  HTML + CSS + JavaScript  │  Chart.js  │  localStorage   │
└───────────────────────────┬─────────────────────────────┘
                            │ REST API
┌───────────────────────────▼─────────────────────────────┐
│                   FastAPI Backend (server.py)            │
│  /api/filters  /api/recommend  /api/upload-resume        │
└───────────────────────────┬─────────────────────────────┘
                            │
┌───────────────────────────▼─────────────────────────────┐
│              JobRecommender Engine (recommender.py)    │
│  TF-IDF Vectorizer  │  Cosine Similarity  │  PDF Parse  │
└───────────────────────────┬─────────────────────────────┘
                            │
                    ┌───────▼───────┐
                    │   jobs.csv    │
                    └───────────────┘
```

---

## Directory Structure

```
├── server.py              # FastAPI backend & REST API
├── recommender.py         # Core AI engine (TF-IDF, Cosine Similarity)
├── jobs.csv               # Job profile dataset (25 roles)
├── requirements.txt       # Python dependencies
├── static/
│   ├── index.html         # Main web page
│   ├── css/style.css      # Dark theme styling
│   └── js/app.js          # Frontend application logic
└── README.md
```

---

## Installation & Setup

### Prerequisites
* **Python 3.8+** installed on your system.

### Step 1: Navigate to Project Directory
```bash
cd "Job Reecommendation_systeb"
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Run the Web Application

**Windows (easiest):** Double-click `run.bat` in the project folder.

**Or from terminal:**
```bash
python server.py
```

Or using uvicorn directly:
```bash
uvicorn server:app --reload --host 0.0.0.0 --port 8000
```

Open your browser at **http://localhost:8000**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/` | Serve the web frontend |
| GET | `/api/filters` | Get categories, locations, experience levels, and skills |
| GET | `/api/jobs` | Get the full job dataset |
| POST | `/api/recommend` | Generate job recommendations |
| POST | `/api/upload-resume` | Upload PDF resume and extract skills |

---

## Example Test Personas

Try selecting these preset profiles in the sidebar:

1. **Data Science & AI**: `python, sql, machine learning, pandas, numpy, scikit-learn, statistics`
2. **Frontend Developer**: `javascript, react, html, css, typescript, git`
3. **DevOps Engineer**: `docker, kubernetes, aws, linux, terraform, ci/cd`
4. **Cybersecurity Analyst**: `network security, linux, python, wireshark, siem, incident response`

---

## Legacy Streamlit Version

The original Streamlit app (`app.py`) is still available. To run it:
```bash
pip install streamlit altair
streamlit run app.py
```
