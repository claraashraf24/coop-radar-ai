def contains_any(text, keywords):
    if not text:
        return False

    text = text.lower()

    for keyword in keywords:
        if keyword.lower() in text:
            return True

    return False


def get_combined_text(job):
    return f"""
    {job.get("title", "")}
    {job.get("description", "")}
    {job.get("location", "")}
    """.lower()


def is_canada_related(job):
    text = get_combined_text(job)

    canada_terms = [
        "canada",
        "ontario",
        "toronto",
        "mississauga",
        "waterloo",
        "ottawa",
        "kitchener",
        "milton",
        "oakville",
        "remote canada",
        "canadian"
    ]

    return any(term in text for term in canada_terms)


def is_student_or_coop_role(job, coop_keywords):
    text = get_combined_text(job)
    return any(keyword.lower() in text for keyword in coop_keywords)


def is_excluded_senior_role(job, exclude_keywords):
    text = get_combined_text(job)
    return any(keyword.lower() in text for keyword in exclude_keywords)


def is_relevant_entry_level_role(job, role_keywords):
    text = get_combined_text(job)
    return any(keyword.lower() in text for keyword in role_keywords)