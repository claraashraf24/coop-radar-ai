import pandas as pd
import streamlit as st
import plotly.express as px
from pathlib import Path

st.set_page_config(
    page_title="CoopRadar AI",
    page_icon="🎯",
    layout="wide"
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

    return df


df = load_data()

st.title("🎯 CoopRadar AI")
st.caption("Automated Canadian Fall 2026 Co-op Job Tracker for AI, Software, Data, and MLOps roles.")

if df.empty:
    st.warning("No jobs found yet. Run `python src/main.py` first to generate the CSV.")
    st.stop()

# Sidebar
st.sidebar.header("Filters")

min_score = st.sidebar.slider(
    "Minimum Match Score",
    min_value=0,
    max_value=100,
    value=70
)

fall_only = st.sidebar.checkbox("Fall 2026 only", value=False)
coop_only = st.sidebar.checkbox("Co-op / Internship only", value=True)
ontario_only = st.sidebar.checkbox("Ontario only", value=False)

companies = sorted(df["company"].dropna().unique())
selected_companies = st.sidebar.multiselect("Company", companies)

sources = sorted(df["source"].dropna().unique())
selected_sources = st.sidebar.multiselect("Source", sources)

search_text = st.sidebar.text_input("Search title / skills / company")

filtered_df = df.copy()

filtered_df = filtered_df[filtered_df["match_score"] >= min_score]

if fall_only:
    filtered_df = filtered_df[filtered_df["is_fall_2026"] == 1]

if coop_only:
    filtered_df = filtered_df[filtered_df["is_coop"] == 1]

if ontario_only:
    filtered_df = filtered_df[
        filtered_df["location"].fillna("").str.contains("Ontario|Toronto|Ottawa|Waterloo|Mississauga|Oakville|Milton", case=False)
    ]

if selected_companies:
    filtered_df = filtered_df[filtered_df["company"].isin(selected_companies)]

if selected_sources:
    filtered_df = filtered_df[filtered_df["source"].isin(selected_sources)]

if search_text:
    search_text = search_text.lower()
    filtered_df = filtered_df[
        filtered_df["title"].fillna("").str.lower().str.contains(search_text)
        | filtered_df["company"].fillna("").str.lower().str.contains(search_text)
        | filtered_df["skills_detected"].fillna("").str.lower().str.contains(search_text)
    ]

filtered_df = filtered_df.sort_values(by="match_score", ascending=False)

# Metrics
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric("Total Jobs", len(df))

with col2:
    st.metric("Filtered Jobs", len(filtered_df))

with col3:
    st.metric("Fall 2026 Jobs", int(df["is_fall_2026"].sum()))

with col4:
    ontario_count = df["location"].fillna("").str.contains(
        "Ontario|Toronto|Ottawa|Waterloo|Mississauga|Oakville|Milton",
        case=False
    ).sum()
    st.metric("Ontario Jobs", int(ontario_count))

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
            title="Top Companies"
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
            title="Jobs by Source"
        )
        st.plotly_chart(fig, use_container_width=True)

st.divider()

st.subheader("Top Matching Jobs")

display_columns = [
    "title",
    "company",
    "location",
    "source",
    "skills_detected",
    "match_score",
    "is_fall_2026",
    "job_url"
]

table_df = filtered_df[display_columns].copy()

table_df = table_df.rename(columns={
    "title": "Title",
    "company": "Company",
    "location": "Location",
    "source": "Source",
    "skills_detected": "Skills Detected",
    "match_score": "Score",
    "is_fall_2026": "Fall 2026",
    "job_url": "Apply Link"
})

st.dataframe(
    table_df,
    use_container_width=True,
    hide_index=True,
    column_config={
        "Apply Link": st.column_config.LinkColumn("Apply Link"),
        "Score": st.column_config.ProgressColumn(
            "Score",
            min_value=0,
            max_value=100,
        ),
        "Fall 2026": st.column_config.CheckboxColumn("Fall 2026")
    }
)
st.divider()
st.subheader("Job Cards")

for _, job in filtered_df.head(20).iterrows():
    with st.container(border=True):
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(f"### {job['title']}")
            st.write(f"**Company:** {job['company']}")
            st.write(f"**Location:** {job['location']}")
            st.write(f"**Source:** {job['source']}")
            st.write(f"**Skills:** {job.get('skills_detected', 'N/A')}")
            st.write(f"**Score:** {job['match_score']}/100")

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
    mime="text/csv"
)