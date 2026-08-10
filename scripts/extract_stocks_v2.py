import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import logging

load_dotenv()

# Setup logging — writes errors to a file instead of just printing
logging.basicConfig(
    filename="pipeline.log",
    level=logging.INFO,
    format="%(asctime)s — %(levelname)s — %(message)s"
)

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

tickers = ["NVDA", "MSFT", "GOOGL", "AMD", "META"]

def get_last_loaded_date():
    """Check what date we last loaded so we only fetch new data."""
    with engine.connect() as conn:
        result = conn.execute(text("""
            SELECT EXISTS (
                SELECT 1 FROM information_schema.tables 
                WHERE table_name = 'raw_stocks'
            )
        """))
        table_exists = result.fetchone()[0]

        if not table_exists:
            return None

        result = conn.execute(text("SELECT MAX(date) FROM raw_stocks"))
        last_date = result.fetchone()[0]
        return last_date

def load_stocks():
    try:
        # Check last loaded date
        last_date = get_last_loaded_date()

        if last_date:
            start_date = pd.Timestamp(last_date) + pd.Timedelta(days=1)
            logging.info(f"Incremental load — fetching from {start_date}")
            print(f"Last load was {last_date}. Fetching new data from {start_date}...")
        else:
            start_date = "2023-01-01"
            logging.info("Full load — no existing data found.")
            print("No existing data. Running full load from 2023-01-01...")

        df = yf.download(tickers, start=start_date, auto_adjust=True)

        if df.empty:
            print("No new data available yet. Pipeline is up to date.")
            logging.info("No new data to load.")
            return

        df = df.stack(level=1).reset_index()
        df.columns = [c.lower().replace(" ", "_") for c in df.columns]

        # Append only new rows — not replace everything
        df.to_sql("raw_stocks", engine, if_exists="append", index=False)

        rows = len(df)
        print(f"Done. {rows} new rows loaded into raw_stocks.")
        logging.info(f"Loaded {rows} new rows into raw_stocks.")

    except Exception as e:
        logging.error(f"Pipeline failed: {e}")
        print(f"Error: {e}")

load_stocks()