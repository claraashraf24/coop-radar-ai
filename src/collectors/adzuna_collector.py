import os
import requests
from dotenv import load_dotenv

load_dotenv()

ADZUNA_APP_ID = os.getenv("ADZUNA_APP_ID")
ADZUNA_APP_KEY = os.getenv("ADZUNA_APP_KEY")


def fetch_adzuna_jobs(search_term, country="ca", page=1):
    if not ADZUNA_APP_ID or not ADZUNA_APP_KEY:
        print("Adzuna API keys missing. Skipping Adzuna.")
        return []

    url = f"https://api.adzuna.com/v1/api/jobs/{country}/search/{page}"

    params = {
        "app_id": ADZUNA_APP_ID,
        "app_key": ADZUNA_APP_KEY,
        "what": search_term,
        "where": "Canada",
        "results_per_page": 50,
        "content-type": "application/json",
    }

    response = requests.get(url, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    jobs = data.get("results", [])

    normalized_jobs = []

    for job in jobs:
        location_data = job.get("location", {}) or {}
        area = location_data.get("area", [])

        location = ", ".join(area) if area else None
        description = job.get("description", "")

        normalized_jobs.append({
            "title": job.get("title"),
            "company": (job.get("company") or {}).get("display_name"),
            "location": location,
            "province": area[1] if len(area) > 1 else None,
            "country": "Canada",
            "remote_type": "Remote" if "remote" in f"{job.get('title', '')} {description}".lower() else "On-site/Hybrid",
            "job_url": job.get("redirect_url"),
            "source": "Adzuna",
            "description": description,
            "posted_date": job.get("created"),
            "detected_season": None,
            "detected_year": None,
            "is_coop": 0,
            "is_fall_2026": 0,
            "category": (job.get("category") or {}).get("label"),
            "skills_detected": None,
            "match_score": 0,
        })

    return normalized_jobs