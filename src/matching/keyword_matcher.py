def detect_keywords(job, keywords):
    text = f"""
    {job.get("title", "")}
    {job.get("description", "")}
    {job.get("location", "")}
    """.lower()

    detected = []

    for keyword in keywords:
        if keyword.lower() in text:
            detected.append(keyword)

    return detected