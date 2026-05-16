def detect_fall_2026(job):
    text = f"""
    {job.get("title", "")}
    {job.get("description", "")}
    {job.get("location", "")}
    """.lower()

    fall_2026_terms = [
        "fall 2026",
        "september 2026",
        "sept 2026",
        "sep 2026",
        "2026 fall"
    ]

    for term in fall_2026_terms:
        if term in text:
            job["is_fall_2026"] = 1
            job["detected_season"] = "Fall"
            job["detected_year"] = "2026"
            return job

    job["is_fall_2026"] = 0
    return job