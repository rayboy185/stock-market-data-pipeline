import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)


def get_last_loaded_date(table_name: str):
    with engine.connect() as conn:
        result = conn.execute(
            text(
                """
                SELECT EXISTS (
                    SELECT 1
                    FROM information_schema.tables
                    WHERE table_name = :table_name
                )
                """
            ),
            {"table_name": table_name},
        )
        table_exists = result.fetchone()[0]

        if not table_exists:
            return None

        result = conn.execute(text(f"SELECT MAX(date) FROM {table_name}"))
        return result.fetchone()[0]


def load_series(table_name: str, ticker: str, column_name: str):
    last_date = get_last_loaded_date(table_name)

    if last_date:
        start_date = pd.Timestamp(last_date) + pd.Timedelta(days=1)
        start_date = start_date.strftime("%Y-%m-%d")
        print(f"Last load for {table_name} was {last_date}. Fetching from {start_date}...")
    else:
        start_date = "2023-01-01"
        print(f"No existing data for {table_name}. Running full load from {start_date}...")

    data = yf.download(ticker, start=start_date, auto_adjust=True)
    if data.empty:
        print(f"No new data for {table_name}.")
        return

    data = data[["Close"]].reset_index()
    data.columns = ["date", column_name]
    data.to_sql(table_name, engine, if_exists="append", index=False)
    print(f"{table_name}: {len(data)} rows loaded.")


load_series("raw_us_yield", "^TNX", "us_10y_yield")
load_series("raw_us_inflation", "TIP", "us_inflation_proxy")
load_series("raw_uk_yield", "^TNX", "uk_10y_yield")