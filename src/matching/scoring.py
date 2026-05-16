def calculate_match_score(job, role_keywords, coop_keywords, ontario_keywords):
    text = f"""
    {job.get("title", "")}
    {job.get("description", "")}
    {job.get("location", "")}
    """.lower()

    score = 0

    for keyword in role_keywords:
        if keyword.lower() in text:
            score += 5

    for keyword in coop_keywords:
        if keyword.lower() in text:
            score += 15
            job["is_coop"] = 1
            break

    for keyword in ontario_keywords:
        if keyword.lower() in text:
            score += 20
            job["province"] = "Ontario"
            break

    if job.get("is_fall_2026") == 1:
        score += 30

    if "canada" in text:
        score += 10
        job["country"] = "Canada"

    job["match_score"] = min(score, 100)
    return job