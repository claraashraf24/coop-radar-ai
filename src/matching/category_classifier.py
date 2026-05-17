def classify_job_category(job):
    text = f"""
    {job.get("title", "")}
    {job.get("description", "")}
    {job.get("skills_detected", "")}
    """.lower()

    if any(word in text for word in ["machine learning", "ml", "artificial intelligence", " ai ", "deep learning", "nlp", "llm"]):
        return "AI / Machine Learning"

    if any(word in text for word in ["data science", "data scientist"]):
        return "Data Science"

    if any(word in text for word in ["data analyst", "analytics", "business intelligence", "bi "]):
        return "Data / Analytics"

    if any(word in text for word in ["software developer", "software engineer", "full stack", "backend", "frontend", "web developer"]):
        return "Software Engineering"

    if any(word in text for word in ["devops", "sre", "site reliability", "kubernetes", "docker", "ci/cd"]):
        return "DevOps / MLOps"

    if any(word in text for word in ["cloud", "aws", "azure", "gcp"]):
        return "Cloud Engineering"

    if any(word in text for word in ["automation", "test automation", "qa automation"]):
        return "Automation / QA"

    if any(word in text for word in ["business analyst", "program enablement", "product analyst"]):
        return "Business / Product"

    return "Other"