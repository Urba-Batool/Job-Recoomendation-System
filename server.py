"""FastAPI backend for the AI Job Recommendation System."""

import os
from typing import Optional

import pandas as pd
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel

from recommender import JobRecommender

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "jobs.csv")

app = FastAPI(title="AI Job Recommendation System", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

engine = JobRecommender(dataset_path=DATASET_PATH)


class RecommendRequest(BaseModel):
    user_skills: list[str]
    top_n: int = 5
    category_filter: Optional[str] = "All Categories"
    exp_filter: Optional[str] = "All Experience Levels"
    location_filter: Optional[str] = "All Locations"
    min_score: float = 0.0


def _serialize_results(df: pd.DataFrame) -> list[dict]:
    if df.empty:
        return []
    records = df.to_dict(orient="records")
    for row in records:
        row["job_id"] = int(row["job_id"])
        row["match_percentage"] = float(row["match_percentage"])
    return records


@app.get("/api/filters")
def get_filters():
    return {
        "categories": engine.get_categories(),
        "experience_levels": engine.get_experience_levels(),
        "locations": engine.get_locations(),
        "skills": engine.all_unique_skills,
    }


@app.get("/api/jobs")
def get_all_jobs():
    cols = [
        "job_id", "job_title", "category", "experience_level",
        "location", "required_skills", "job_description",
    ]
    return engine.df[cols].to_dict(orient="records")


@app.post("/api/recommend")
def recommend(req: RecommendRequest):
    skills_blob = ", ".join(s.strip().lower() for s in req.user_skills if s.strip())
    if not skills_blob:
        raise HTTPException(status_code=400, detail="At least one skill is required.")

    location = req.location_filter
    if location == "All Locations":
        location = None

    results = engine.recommend(
        user_skills=skills_blob,
        top_n=req.top_n,
        category_filter=req.category_filter,
        exp_filter=req.exp_filter,
        location_filter=location,
        min_score=req.min_score,
    )

    output_cols = [
        "job_id", "job_title", "category", "experience_level",
        "location", "required_skills", "job_description",
        "match_percentage", "matched_skills", "missing_skills",
    ]
    return {"results": _serialize_results(results[output_cols]), "total": len(results)}


@app.post("/api/upload-resume")
async def upload_resume(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported.")

    content = await file.read()
    import io
    pdf_buffer = io.BytesIO(content)

    _, extracted = engine.extract_skills_from_pdf(pdf_buffer)
    return {"skills": extracted, "count": len(extracted)}


static_dir = os.path.join(BASE_DIR, "static")
if os.path.isdir(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/")
def serve_index():
    index_path = os.path.join(static_dir, "index.html")
    if os.path.isfile(index_path):
        return FileResponse(index_path)
    return {"message": "AI Job Recommendation API is running. Place index.html in /static."}


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 56)
    print("  AI Job Recommendation System is starting...")
    print("  Open in your browser: http://localhost:8000")
    print("  Press Ctrl+C to stop the server")
    print("=" * 56 + "\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
