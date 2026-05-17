import re
from PyPDF2 import PdfReader
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

TARGET_SKILLS = [
    # Programming
    "python",
    "sql",
    "r",
    "bash",
    "java",
    "c++",
    "javascript",
    "typescript",

    # Data / ML
    "machine learning",
    "deep learning",
    "data science",
    "data analysis",
    "data analytics",
    "artificial intelligence",
    "ai",
    "ml",
    "nlp",
    "natural language processing",
    "llm",
    "generative ai",
    "computer vision",
    "statistics",
    "predictive modeling",

    # ML frameworks
    "pandas",
    "numpy",
    "scikit-learn",
    "tensorflow",
    "keras",
    "pytorch",
    "hugging face",
    "opencv",
    "mlflow",
    "dvc",

    # Data engineering
    "etl",
    "elt",
    "data pipeline",
    "data pipelines",
    "data validation",
    "data transformation",
    "data ingestion",
    "databricks",
    "spark",
    "pyspark",
    "airflow",

    # Databases
    "postgresql",
    "mysql",
    "mongodb",
    "sqlite",
    "nosql",
    "snowflake",
    "bigquery",

    # Cloud / DevOps / MLOps
    "aws",
    "azure",
    "gcp",
    "docker",
    "kubernetes",
    "terraform",
    "linux",
    "unix",
    "git",
    "github actions",
    "ci/cd",
    "devops",
    "mlops",
    "monitoring",
    "observability",

    # Web / API
    "fastapi",
    "flask",
    "django",
    "react",
    "node.js",
    "rest api",
    "api",

    # BI / Analyst tools
    "excel",
    "power bi",
    "tableau",
    "looker",
    "dashboard",
    "dashboards",

    # QA / Automation
    "automation",
    "testing",
    "unit testing",
    "test automation",
    "selenium",

    # Soft/product keywords
    "agile",
    "jira",
    "business analysis",
    "requirements gathering",
    "stakeholder",
]

SKILL_ALIASES = {
    "artificial intelligence": "AI",
    "ai": "AI",
    "machine learning": "Machine Learning",
    "ml": "Machine Learning",
    "natural language processing": "NLP",
    "nlp": "NLP",
    "llm": "LLM",
    "generative ai": "Generative AI",
    "data science": "Data Science",
    "data analysis": "Data Analysis",
    "data analytics": "Data Analytics",
    "data pipeline": "Data Pipelines",
    "data pipelines": "Data Pipelines",
    "ci/cd": "CI/CD",
    "github actions": "GitHub Actions",
    "rest api": "REST API",
    "api": "API",
    "power bi": "Power BI",
    "node.js": "Node.js",
    "pyspark": "PySpark",
    "scikit-learn": "scikit-learn",
    "mlflow": "MLflow",
    "dvc": "DVC",
    "opencv": "OpenCV",
    "fastapi": "FastAPI",
    "postgresql": "PostgreSQL",
    "mysql": "MySQL",
    "mongodb": "MongoDB",
    "sqlite": "SQLite",
    "aws": "AWS",
    "azure": "Azure",
    "gcp": "GCP",
    "mlops": "MLOps",
    "devops": "DevOps",
}


def extract_resume_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    text = ""

    for page in reader.pages:
        page_text = page.extract_text()
        if page_text:
            text += page_text + "\n"

    return clean_text(text)


def clean_text(text):
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^a-z0-9+#./\-\s]", " ", text)
    return text.strip()


def calculate_resume_similarity(resume_text, job_text):
    if not resume_text or not job_text:
        return 0

    resume_text_clean = clean_text(resume_text)
    job_text_clean = clean_text(job_text)

    # 1. TF-IDF text similarity
    documents = [resume_text_clean, job_text_clean]

    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1, 2),
        max_features=5000
    )

    tfidf_matrix = vectorizer.fit_transform(documents)
    text_similarity = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0] * 100

    # 2. Skill overlap score
    resume_skills = set(extract_skills_from_text(resume_text_clean))
    job_skills = set(extract_skills_from_text(job_text_clean))

    if job_skills:
        skill_score = (len(resume_skills.intersection(job_skills)) / len(job_skills)) * 100
    else:
        skill_score = 40  # neutral fallback because job text may be short

    # 3. Category/profile relevance boost
    category_score = 0

    if any(term in job_text_clean for term in ["machine learning", "ai", "data science", "data analyst", "software engineer", "software developer"]):
        category_score += 40

    if any(term in resume_text_clean for term in ["machine learning", "python", "sql", "pytorch", "tensorflow", "data pipeline", "mlflow", "spark"]):
        category_score += 40

    if any(term in job_text_clean for term in ["intern", "co-op", "fall 2026"]):
        category_score += 20

    category_score = min(category_score, 100)

    final_score = (
        0.50 * skill_score +
        0.30 * category_score +
        0.20 * text_similarity
    )

    return round(final_score, 2)

def normalize_skill_name(skill):
    skill = skill.lower().strip()
    return SKILL_ALIASES.get(skill, skill.title())


def extract_skills_from_text(text):
    text = clean_text(text)
    found_skills = []

    for skill in TARGET_SKILLS:
        skill_clean = skill.lower()

        # For short skills like AI, ML, R, use safer matching
        if skill_clean in ["ai", "ml", "r"]:
            pattern = rf"\b{re.escape(skill_clean)}\b"
            if re.search(pattern, text):
                found_skills.append(normalize_skill_name(skill_clean))
        else:
            if skill_clean in text:
                found_skills.append(normalize_skill_name(skill_clean))

    return sorted(set(found_skills))


def analyze_skill_gap(resume_text, job_text):
    resume_skills = set(extract_skills_from_text(resume_text))
    job_skills = set(extract_skills_from_text(job_text))

    inferred_skills = infer_expected_skills_from_category(job_text)
    job_skills = job_skills.union(inferred_skills)

    matched_skills = sorted(resume_skills.intersection(job_skills))
    missing_skills = sorted(job_skills.difference(resume_skills))

    missing_skills = missing_skills[:8]

    return matched_skills, missing_skills

def infer_expected_skills_from_category(job_text):
    job_text = clean_text(job_text)

    expected_skills = set()

    if any(term in job_text for term in ["data science", "data scientist", "machine learning", "ai", "ml"]):
        expected_skills.update([
            "Python",
            "SQL",
            "Machine Learning",
            "Pandas",
            "NumPy",
            "scikit-learn",
        ])

    if any(term in job_text for term in ["software engineer", "software developer", "backend", "full stack"]):
        expected_skills.update([
            "Python",
            "Git",
            "REST API",
            "SQL",
            "Docker",
        ])

    if any(term in job_text for term in ["data analyst", "business intelligence", "analytics"]):
        expected_skills.update([
            "SQL",
            "Excel",
            "Power BI",
            "Data Analysis",
            "Dashboard",
        ])

    if any(term in job_text for term in ["devops", "mlops", "cloud", "automation"]):
        expected_skills.update([
            "Docker",
            "CI/CD",
            "GitHub Actions",
            "Linux",
            "AWS",
            "Azure",
        ])

    return expected_skills