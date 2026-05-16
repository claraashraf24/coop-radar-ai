import yaml

from collectors.remotive_collector import fetch_remotive_jobs
from storage.database import create_jobs_table, insert_job
from processing.filters import (
    is_canada_related,
    is_student_or_coop_role,
    is_excluded_senior_role,
    is_relevant_entry_level_role,
)
from processing.fall2026_detector import detect_fall_2026
from matching.keyword_matcher import detect_keywords
from matching.scoring import calculate_match_score
from collectors.adzuna_collector import fetch_adzuna_jobs
from storage.exporter import export_jobs_to_csv


def load_yaml(path):
    with open(path, "r") as file:
        return yaml.safe_load(file)


def main():
    print("Starting CoopRadar AI job scan...")

    create_jobs_table()

    search_config = load_yaml("config/search_queries.yml")
    keyword_config = load_yaml("config/keywords.yml")

    queries = search_config["queries"]

    role_keywords = keyword_config["role_keywords"]
    coop_keywords = keyword_config["coop_keywords"]
    ontario_keywords = keyword_config["ontario_keywords"]
    exclude_keywords = keyword_config["exclude_keywords"]

    total_found = 0
    total_saved = 0
    skipped_not_canada = 0
    skipped_not_coop = 0
    skipped_senior = 0
    skipped_not_relevant = 0

    for query in queries:
        print(f"\nSearching for: {query}")

        remotive_jobs = fetch_remotive_jobs(query)
        adzuna_jobs = fetch_adzuna_jobs(query)

        print(f"Remotive returned: {len(remotive_jobs)} jobs")
        print(f"Adzuna returned: {len(adzuna_jobs)} jobs")

        jobs = []
        jobs.extend(remotive_jobs)
        jobs.extend(adzuna_jobs)

        total_found += len(jobs)

        for job in jobs:
            if not is_canada_related(job):
                skipped_not_canada += 1
                continue

            if is_excluded_senior_role(job, exclude_keywords):
                skipped_senior += 1
                continue

            if not is_student_or_coop_role(job, coop_keywords):
                skipped_not_coop += 1
                continue

            if not is_relevant_entry_level_role(job, role_keywords):
                skipped_not_relevant += 1
                continue

            job = detect_fall_2026(job)

            detected_skills = detect_keywords(job, role_keywords)
            job["skills_detected"] = ", ".join(detected_skills)

            job = calculate_match_score(
                job,
                role_keywords,
                coop_keywords,
                ontario_keywords
            )

            insert_job(job)
            total_saved += 1

    export_jobs_to_csv()
    print("\nScan complete.")
    print(f"Total jobs found: {total_found}")
    print(f"Saved jobs: {total_saved}")
    print(f"Skipped not Canada-related: {skipped_not_canada}")
    print(f"Skipped senior/lead roles: {skipped_senior}")
    print(f"Skipped not co-op/intern/student: {skipped_not_coop}")
    print(f"Skipped not AI/software relevant: {skipped_not_relevant}")


if __name__ == "__main__":
    main()