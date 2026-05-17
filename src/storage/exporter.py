import sqlite3
from pathlib import Path
import pandas as pd

DB_PATH = Path("data/jobs.db")
EXPORT_DIR = Path("data/exports")


def export_jobs_to_csv():
    EXPORT_DIR.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(DB_PATH)

    query = """
        SELECT
            title,
            company,
            location,
            province,
            country,
            remote_type,
            source,
            category,
            job_category,
            skills_detected,
            match_score,
            is_coop,
            is_fall_2026,
            detected_season,
            detected_year,
            posted_date,
            date_found,
            job_url
        FROM jobs
        ORDER BY match_score DESC, date_found DESC
    """

    df = pd.read_sql_query(query, conn)
    conn.close()

    output_path = EXPORT_DIR / "jobs_export.csv"
    df.to_csv(output_path, index=False)

    print(f"Exported {len(df)} jobs to {output_path}")