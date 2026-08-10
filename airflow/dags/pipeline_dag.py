from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_DIR = "/opt/airflow/project"

with DAG(
    dag_id="ai_stocks_pipeline",
    start_date=datetime(2026, 8, 1),
    schedule="0 7 * * *",
    catchup=False,
    tags=["ai-stocks"],
) as dag:

    start_postgres = BashOperator(
        task_id="ensure_postgres_healthy",
        bash_command=f"cd {PROJECT_DIR} && docker compose up -d --wait postgres",
    )

    run_extractor = BashOperator(
        task_id="run_extractor",
        bash_command=f"cd {PROJECT_DIR} && docker compose run --rm extractor",
    )

    run_dbt = BashOperator(
        task_id="run_dbt",
        bash_command=f"cd {PROJECT_DIR} && docker compose run --rm dbt",
    )

    start_postgres >> run_extractor >> run_dbt