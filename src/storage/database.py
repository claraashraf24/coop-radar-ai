import sqlite3
from pathlib import Path

DB_PATH = Path("data/jobs.db")


def get_connection():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    return sqlite3.connect(DB_PATH)


def create_jobs_table():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS jobs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            company TEXT,
            location TEXT,
            province TEXT,
            country TEXT,
            remote_type TEXT,
            job_url TEXT UNIQUE,
            source TEXT,
            description TEXT,
            posted_date TEXT,
            detected_season TEXT,
            detected_year TEXT,
            is_coop INTEGER,
            is_fall_2026 INTEGER,
            category TEXT,
            skills_detected TEXT,
            match_score INTEGER,
            date_found TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    conn.close()


def insert_job(job):
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        INSERT OR IGNORE INTO jobs (
            title,
            company,
            location,
            province,
            country,
            remote_type,
            job_url,
            source,
            description,
            posted_date,
            detected_season,
            detected_year,
            is_coop,
            is_fall_2026,
            category,
            skills_detected,
            match_score
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        job.get("title"),
        job.get("company"),
        job.get("location"),
        job.get("province"),
        job.get("country"),
        job.get("remote_type"),
        job.get("job_url"),
        job.get("source"),
        job.get("description"),
        job.get("posted_date"),
        job.get("detected_season"),
        job.get("detected_year"),
        job.get("is_coop"),
        job.get("is_fall_2026"),
        job.get("category"),
        job.get("skills_detected"),
        job.get("match_score"),
    ))

    conn.commit()
    conn.close()


def get_all_jobs():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT * FROM jobs ORDER BY date_found DESC")
    jobs = cursor.fetchall()

    conn.close()
    return jobs