from src.collectors.adzuna_collector import fetch_adzuna_jobs

jobs = fetch_adzuna_jobs("software developer intern")

print("Jobs returned:", len(jobs))

for job in jobs[:10]:
    print(job["title"], "-", job["company"], "-", job["location"])