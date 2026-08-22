import os
import requests
from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime

PROJECT_DIR = "/opt/airflow/project"

def slack_failure_alert(context):
    webhook_url = os.environ.get("SLACK_WEBHOOK_URL")
    if not webhook_url:
        return
    task_id = context["task_instance"].task_id
    dag_id = context["task_instance"].dag_id
    message = {
        "text": f":red_circle: *Pipeline failed*\nDAG: `{dag_id}`\nTask: `{task_id}`"
    }
    requests.post(webhook_url, json=message)

with DAG(
    dag_id="ai_stocks_pipeline",
    start_date=datetime(2026, 8, 1),
    schedule="0 7 * * *",
    catchup=False,
    tags=["ai-stocks"],
    default_args={"on_failure_callback": slack_failure_alert},
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