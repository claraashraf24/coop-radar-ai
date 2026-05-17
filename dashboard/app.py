import sys
from pathlib import Path

import pandas as pd
import plotly.express as px
import streamlit as st

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT_DIR))

from src.matching.resume_matcher import (
    analyze_skill_gap,
    calculate_resume_similarity,
    extract_resume_text,
)

st.set_page_config(
    page_title="CoopRadar AI",
    page_icon="🎯",
    layout="wide",
)

CSV_PATH = Path("data/exports/jobs_export.csv")


@st.cache_data
def load_data():
    if not CSV_PATH.exists():
        return pd.DataFrame()

    df = pd.read_csv(CSV_PATH)

    df["match_score"] = pd.to_numeric(df["match_score"], errors="coerce").fillna(0)
    df["is_fall_2026"] = pd.to_numeric(df["is_fall_2026"], errors="coerce").fillna(0)
    df["is_coop"] = pd.to_numeric(df["is_coop"], errors="coerce").fillna(0)

    if "job_category" not in df.columns:
        df["job_category"] = "Other"

    if "skills_detected" not in df.columns:
        df["skills_detected"] = ""

    return df


st.title("🎯 CoopRadar AI")
st.caption(
    "Automated Canadian Fall 2026 Co-op Job Tracker for AI, Software, Data, and MLOps roles."
)

st.info(
    "Upload your resume to personalize job rankings based on your skills and experience. "
    "Always verify the official job posting before applying."
)

uploaded_resume = st.file_uploader(
    "Upload your resume PDF for personalized matching",
    type=["pdf"],
)

resume_text = None
resume_matching_enabled = False

if uploaded_resume is not None:
    with st.spinner("Analyzing resume..."):
        resume_text = extract_resume_text(uploaded_resume)
        resume_matching_enabled = True

    st.success("Resume uploaded successfully. Personalized match scores are now enabled.")

df = load_data()

if df.empty:
    st.warning("No jobs found yet. Run `python src/main.py` first to generate the CSV.")
    st.stop()

df["job_text"] = (
    df["title"].fillna("")
    + " "
    + df["company"].fillna("")
    + " "
    + df["location"].fillna("")
    + " "
    + df["job_category"].fillna("")
    + " "
    + df["skills_detected"].fillna("")
)

if resume_matching_enabled and resume_text:
    df["resume_match_score"] = df["job_text"].apply(
        lambda text: calculate_resume_similarity(resume_text, text)
    )

    skill_analysis = df["job_text"].apply(
        lambda text: analyze_skill_gap(resume_text, text)
    )

    df["matched_skills"] = skill_analysis.apply(
        lambda x: ", ".join(x[0]) if x[0] else "None"
    )
    df["missing_skills"] = skill_analysis.apply(
        lambda x: ", ".join(x[1]) if x[1] else "None"
    )
else:
    df["resume_match_score"] = 0
    df["matched_skills"] = "Upload resume"
    df["missing_skills"] = "Upload resume"

# Sidebar
st.sidebar.header("Filters")

min_score = st.sidebar.slider(
    "Minimum Job Match Score",
    min_value=0,
    max_value=100,
    value=70,
)

if resume_matching_enabled:
    min_resume_score = st.sidebar.slider(
        "Minimum Resume Match %",
        min_value=0,
        max_value=100,
        value=5,
    )
else:
    min_resume_score = 0

sort_options = ["Job Match Score", "Fall 2026 First", "Company"]

if resume_matching_enabled:
    sort_options.insert(1, "Resume Match Score")

sort_option = st.sidebar.selectbox("Sort by", sort_options)

fall_only = st.sidebar.checkbox("Fall 2026 only", value=False)
coop_only = st.sidebar.checkbox("Co-op / Internship only", value=True)
ontario_only = st.sidebar.checkbox("Ontario only", value=False)

companies = sorted(df["company"].dropna().unique())
selected_companies = st.sidebar.multiselect("Company", companies)

sources = sorted(df["source"].dropna().unique())
selected_sources = st.sidebar.multiselect("Source", sources)

categories = sorted(df["job_category"].dropna().unique())
selected_categories = st.sidebar.multiselect("Job Category", categories)

search_text = st.sidebar.text_input("Search title / skills / company")

filtered_df = df.copy()

filtered_df = filtered_df[filtered_df["match_score"] >= min_score]

if resume_matching_enabled:
    filtered_df = filtered_df[filtered_df["resume_match_score"] >= min_resume_score]

if fall_only:
    filtered_df = filtered_df[filtered_df["is_fall_2026"] == 1]

if coop_only:
    filtered_df = filtered_df[filtered_df["is_coop"] == 1]

if ontario_only:
    filtered_df = filtered_df[
        filtered_df["location"]
        .fillna("")
        .str.contains(
            "Ontario|Toronto|Ottawa|Waterloo|Mississauga|Oakville|Milton",
            case=False,
        )
    ]

if selected_companies:
    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

if selected_sources:
    filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]

if selected_categories:
    filtered_df = filtered_df[filtered_df["job_category"].isin(selected_categories)]

if search_text:
    search_text = search_text.lower()
    filtered_df = filtered_df[
        filtered_df["title"].fillna("").str.lower().str.contains(search_text)
        | filtered_df["company"].fillna("").str.lower().str.contains(search_text)
        | filtered_df["skills_detected"].fillna("").str.lower().str.contains(search_text)
        | filtered_df["job_category"].fillna("").str.lower().str.contains(search_text)
    ]

if sort_option == "Resume Match Score" and resume_matching_enabled:
    filtered_df = filtered_df.sort_values(
        by=["resume_match_score", "match_score"],
        ascending=[False, False],
    )
elif sort_option == "Fall 2026 First":
    filtered_df = filtered_df.sort_values(
        by=["is_fall_2026", "match_score"],
        ascending=[False, False],
    )
elif sort_option == "Company":
    filtered_df = filtered_df.sort_values(by="company", ascending=True)
else:
    filtered_df = filtered_df.sort_values(by="match_score", ascending=False)

# Metrics
metric_cols = st.columns(5 if resume_matching_enabled else 4)

with metric_cols[0]:
    st.metric("Total Jobs", len(df))

with metric_cols[1]:
    st.metric("Filtered Jobs", len(filtered_df))

with metric_cols[2]:
    st.metric("Fall 2026 Jobs", int(df["is_fall_2026"].sum()))

with metric_cols[3]:
    ontario_count = (
        df["location"]
        .fillna("")
        .str.contains(
            "Ontario|Toronto|Ottawa|Waterloo|Mississauga|Oakville|Milton",
            case=False,
        )
        .sum()
    )
    st.metric("Ontario Jobs", int(ontario_count))

if resume_matching_enabled:
    with metric_cols[4]:
        top_resume_match = (
            filtered_df["resume_match_score"].max() if not filtered_df.empty else 0
        )
        st.metric("Top Resume Match", f"{top_resume_match:.1f}%")

st.divider()

# Charts
chart_col1, chart_col2 = st.columns(2)

with chart_col1:
    top_companies = filtered_df["company"].value_counts().head(10).reset_index()
    top_companies.columns = ["company", "count"]

    if not top_companies.empty:
        fig = px.bar(
            top_companies,
            x="company",
            y="count",
            title="Top Companies",
        )
        st.plotly_chart(fig, use_container_width=True)

with chart_col2:
    source_counts = filtered_df["source"].value_counts().reset_index()
    source_counts.columns = ["source", "count"]

    if not source_counts.empty:
        fig = px.pie(
            source_counts,
            names="source",
            values="count",
            title="Jobs by Source",
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top Matching Jobs")

display_columns = [
    "title",
    "company",
    "location",
    "job_category",
    "source",
    "skills_detected",
    "match_score",
    "resume_match_score",
    "matched_skills",
    "missing_skills",
    "is_fall_2026",
    "job_url",
]

table_df = filtered_df[display_columns].copy()

table_df = table_df.rename(
    columns={
        "title": "Title",
        "company": "Company",
        "location": "Location",
        "job_category": "Category",
        "source": "Source",
        "skills_detected": "Skills Detected",
        "match_score": "Job Score",
        "resume_match_score": "Resume Match %",
        "matched_skills": "Matched Skills",
        "missing_skills": "Missing Skills",
        "is_fall_2026": "Fall 2026",
        "job_url": "Apply Link",
        "matched_skills": "Matched Resume Skills",
        "missing_skills": "Missing / Suggested Skills",
    }
)

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Apply Link": st.column_config.LinkColumn("Apply Link"),
        "Job Score": st.column_config.ProgressColumn(
            "Job Score",
            min_value=0,
            max_value=100,
        ),
        "Resume Match %": st.column_config.ProgressColumn(
            "Resume Match %",
            min_value=0,
            max_value=100,
        ),
        "Fall 2026": st.column_config.CheckboxColumn("Fall 2026"),
    },
)

st.divider()
st.subheader("Job Cards")

for _, job in filtered_df.head(20).iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### {job['title']}")
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Category:** {job.get('job_category', 'Other')}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Source:** {job['source']}")
            st.write(f"**Skills:** {job.get('skills_detected', 'N/A')}")
            st.write(f"**Job Score:** {job['match_score']}/100")

            if resume_matching_enabled:
                st.write(f"**Resume Match:** {job['resume_match_score']}%")
                matched = job["matched_skills"]
                missing = job["missing_skills"]

                st.write("**Matched Skills:**")
                if matched and matched != "None":
                    st.success(matched)
                else:
                    st.info("No direct matched skills detected yet.")

                st.write("**Missing / Suggested Skills to Improve:**")
                if missing and missing != "None":
                    st.warning(missing)
                else:
                    st.success("No major missing skills detected.")

            if job["is_fall_2026"] == 1:
                st.success("Fall 2026 Match")
            else:
                st.info("Potential co-op / internship match")

        with col2:
            st.link_button("Apply", job["job_url"])

st.download_button(
    label="Download filtered jobs as CSV",
    data=filtered_df.to_csv(index=False),
    file_name="filtered_coop_jobs.csv",
    mime="text/csv",
)