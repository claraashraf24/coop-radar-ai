# CoopRadar AI

CoopRadar AI is an automated Canadian co-op job tracker built for students looking for Fall 2026 opportunities in AI, software engineering, data science, DevOps, MLOps, cloud, and automation.

The platform collects jobs from job APIs, filters Canada-based co-op/internship roles, ranks them using custom matching logic, categorizes each job, and displays everything in a live Streamlit dashboard.

## Live Dashboard

https://coop-radar-ai-ulfqtmnnhcp2ma8xhr3vdf.streamlit.app/

## Features

- Automated job collection from multiple sources
- Fall 2026 co-op/internship detection
- Ontario-first prioritization
- AI/software/data relevance scoring
- Job category classification
- Interactive Streamlit dashboard
- Company, source, category, score, and keyword filters
- Clickable apply links
- CSV export for filtered jobs

## Job Categories

The system classifies jobs into:

- AI / Machine Learning
- Software Engineering
- Data Science
- Data / Analytics
- DevOps / MLOps
- Cloud Engineering
- Automation / QA
- Business / Product
- Other

## Tech Stack

- Python
- Pandas
- SQLite
- Streamlit
- Plotly
- YAML configuration
- Adzuna API
- Remotive API

## Project Structure

```text
coop-radar-ai/
├── config/
│   ├── keywords.yml
│   └── search_queries.yml
├── dashboard/
│   └── app.py
├── data/
│   └── exports/
│       └── jobs_export.csv
├── src/
│   ├── collectors/
│   ├── matching/
│   ├── processing/
│   └── storage/
├── requirements.txt
├── .env.example
└── README.md