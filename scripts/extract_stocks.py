import os
import yfinance as yf
import pandas as pd
from sqlalchemy import create_engine
from dotenv import load_dotenv

load_dotenv()

engine = create_engine(
    f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}"
    f"@{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

tickers = ["NVDA", "MSFT", "GOOGL", "AMD", "META"]

df = yf.download(tickers, start="2023-01-01", auto_adjust=True)

df = df.stack(level=1).reset_index()
df.columns = [c.lower().replace(" ", "_") for c in df.columns]
df = df.rename(columns={"level_1": "ticker", "level_0": "date"} if "level_1" in df.columns else {"price": "ticker"})

print("Columns received:", df.columns.tolist())

df.to_sql("raw_stocks", engine, if_exists="replace", index=False)
print(f"Done. {len(df)} rows loaded into raw_stocks.")