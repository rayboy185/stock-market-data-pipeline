import os
import sys
from pathlib import Path

import pandas as pd
import pytest
import sqlalchemy as sa
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.append(str(ROOT))

load_dotenv(ROOT / ".env")


@pytest.fixture(scope="module")
def engine():
    engine = sa.create_engine(
        f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
        f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
    )
    yield engine
    engine.dispose()


def test_raw_tables_exist(engine):
    with engine.connect() as conn:
        result = conn.execute(
            sa.text(
                """
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                  AND table_name IN ('raw_stocks', 'raw_us_yield', 'raw_us_inflation', 'raw_uk_yield')
                ORDER BY table_name
                """
            )
        )
        tables = {row[0] for row in result.fetchall()}

    assert {"raw_stocks", "raw_us_yield", "raw_us_inflation", "raw_uk_yield"}.issubset(tables)


def test_staging_views_and_mart_can_query(engine):
    with engine.connect() as conn:
        for view_name in ["stg_stocks", "stg_macro"]:
            result = conn.execute(sa.text(f"SELECT COUNT(*) FROM {view_name}"))
            assert result.scalar() >= 0

        mart_count = conn.execute(sa.text("SELECT COUNT(*) FROM mart_ai_signals")).scalar()
        assert mart_count >= 0


def test_raw_stocks_has_required_columns(engine):
    with engine.connect() as conn:
        df = pd.read_sql_query(
            "SELECT * FROM raw_stocks LIMIT 5",
            conn,
        )

    assert {"date", "ticker", "close"}.issubset(df.columns)


def test_macro_tables_have_numeric_metrics(engine):
    with engine.connect() as conn:
        yield_df = pd.read_sql_query("SELECT * FROM raw_us_yield ORDER BY date DESC LIMIT 5", conn)
        inflation_df = pd.read_sql_query("SELECT * FROM raw_us_inflation ORDER BY date DESC LIMIT 5", conn)
        uk_df = pd.read_sql_query("SELECT * FROM raw_uk_yield ORDER BY date DESC LIMIT 5", conn)

    assert "us_10y_yield" in yield_df.columns
    assert "us_inflation_proxy" in inflation_df.columns
    assert "uk_10y_yield" in uk_df.columns
