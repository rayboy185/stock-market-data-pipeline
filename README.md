# Stock Market Data Pipeline

An automated, containerized data pipeline that tracks daily price movements for major AI-sector stocks (NVDA, MSFT, GOOGL, AMD, META), calculates technical signals, and surfaces them on an interactive Power BI dashboard — with zero manual work after setup.

This project does not predict markets. It automates the repetitive work of pulling, cleaning, and calculating signals from raw price data, so a human can make faster, better-informed decisions.

![Project pic](images/first%20dashboard%20pic.png)

---

## Architecture


![Stack](images/diagram%20view.png)

---

## Stack

- **Python** — extraction (`yfinance`, `pandas`, `sqlalchemy`)
- **PostgreSQL** — storage
- **dbt** — transformation, testing
- **Docker / Docker Compose** — full containerization
- **Apache Airflow** — orchestration, scheduling
- **Power BI** — dashboard
- **GitHub Actions** — CI/CD
- **Slack** — failure alerting

---

## What it does

- Pulls daily price data for 5 AI-sector stocks, plus macro context (US 10-year yield, inflation proxy)
- Incremental loading — only fetches new data, never re-downloads history
- dbt models calculate: daily return %, 7-day and 30-day moving averages, volume spike detection, trend direction
- Data quality enforced with 13 automated dbt tests (uniqueness, null checks, valid ranges)
- Fully containerized — the entire stack (database, extraction, transformation) rebuilds from zero with one command
- Scheduled daily via Airflow, with Slack alerts on failure
- Every push to GitHub automatically runs the full test suite via CI/CD

![Project pic 2](images/second%20dashboard%20pic.png)
![Project pic 3](images/third%20dashboard%20pic.png)

---

## Running it locally

1. Clone the repo
2. Copy `.env.example` to `.env` and fill in your database credentials
3. Copy `.env.docker.example` to `.env.docker` similarly (if applicable)
4. Run:
```bash
docker-compose up --build
```
This builds and runs the extractor, dbt, and PostgreSQL — from an empty database to a fully populated analytics table.

5. Connect Power BI to `localhost:5432` (or `5433` depending on your setup), database `ai_stocks`

---

## Known limitations

- Single-node, local-only — not built for production scale or cloud deployment
- No ML/predictive modeling — purely descriptive technical signals
- One dbt mart, full-refresh materialization — no incremental models or dimensional design yet
- Airflow uses a "Docker outside of Docker" pattern (mounted `docker.sock`) — a pragmatic choice for single-machine local development, not a production orchestration pattern

---

## Why these choices

- **yfinance over scraping official sources** — after hitting anti-bot blocks on government data sources, switched to yfinance-derived proxies (^TNX, TIP) for macro context, prioritizing reliability over source purity
- **dbt for transformation** — SQL-native, testable, dependency-aware; staging/mart separation keeps raw data immutable and auditable
- **Docker + Airflow** — applying real orchestration and containerization practice to a data pipeline, not just running scripts manually

---

## Author

Built by RAY' as a first end-to-end data engineering project, applying DevOps fundamentals (Docker, CI/CD, orchestration) to a new domain.
