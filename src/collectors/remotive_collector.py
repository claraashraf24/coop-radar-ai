import requests


REMOTIVE_API_URL = "https://remotive.com/api/remote-jobs"


def fetch_remotive_jobs(search_term="software"):
    params = {
        "search": search_term
    }

    response = requests.get(REMOTIVE_API_URL, params=params, timeout=20)
    response.raise_for_status()

    data = response.json()
    jobs = data.get("jobs", [])

    normalized_jobs = []

    for job in jobs:
        normalized_jobs.append({
            "title": job.get("title"),
            "company": job.get("company_name"),
            "location": job.get("candidate_required_location"),
            "province": None,
            "country": "Canada" if "Canada" in str(job.get("candidate_required_location")) else None,
            "remote_type": "Remote",
            "job_url": job.get("url"),
            "source": "Remotive",
            "description": job.get("description"),
            "posted_date": job.get("publication_date"),
            "detected_season": None,
            "detected_year": None,
            "is_coop": 0,
            "is_fall_2026": 0,
            "category": job.get("category"),
            "skills_detected": None,
            "match_score": 0,
        })

    return normalized_jobs