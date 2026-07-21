# 🌐 Professional Deployment Guide

This guide provides step-by-step instructions for deploying the **AI-Based Job Recommendation System** to cloud hosting platforms so that anyone (recruiters, students, career counselors) can access it online.

---

## ☁️ Option 1: Streamlit Community Cloud (Recommended & Free)

Streamlit Community Cloud allows you to deploy Python Streamlit applications for free directly from a GitHub repository in under 2 minutes.

### Step 1: Initialize Git Repository & Push to GitHub
1. Open your terminal in the project directory:
   ```bash
   cd "c:\Users\Admin\OneDrive\Desktop\Job Reecommendation_systeb"
   ```
2. Initialize git and commit your files:
   ```bash
   git init
   git add .
   git commit -m "Initial commit of AI Job Recommendation System"
   ```
3. Push your code to a new public repository on [GitHub](https://github.com):
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/job-recommendation-system.git
   git branch -M main
   git push -u origin main
   ```

### Step 2: Deploy on Streamlit Cloud
1. Go to [share.streamlit.io](https://share.streamlit.io) and log in with your GitHub account.
2. Click **"New App"**.
3. Select your repository (`job-recommendation-system`), set branch to `main`, and set **Main file path** to `app.py`.
4. Click **"Deploy!"**.
5. Your live app URL will be generated (e.g. `https://job-recommendation-system.streamlit.app`).

---

## 🐳 Option 2: Docker Deployment

If you want to deploy to AWS, Azure, GCP, or Render using Docker, use the following `Dockerfile`.

### `Dockerfile`
Create a file named `Dockerfile` in the root directory:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8501

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
```

### Build & Run Container Locally
```bash
docker build -t job-recommender-app .
docker run -p 8501:8501 job-recommender-app
```

---

## 📋 Pre-Deployment Checklist

- [x] `requirements.txt` specifies `streamlit`, `pandas`, `scikit-learn`, `numpy`, `altair`.
- [x] `.streamlit/config.toml` configures corporate dark theme.
- [x] `jobs.csv` dataset present in root directory.
- [x] `recommender.py` and `app.py` tested with zero syntax errors.
