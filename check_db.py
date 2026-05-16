import sqlite3

conn = sqlite3.connect("data/jobs.db")
cursor = conn.cursor()

cursor.execute("""
    SELECT title, company, location, match_score, job_url
    FROM jobs
    ORDER BY match_score DESC
    LIMIT 10
""")

rows = cursor.fetchall()

for row in rows:
    print(row)

conn.close()