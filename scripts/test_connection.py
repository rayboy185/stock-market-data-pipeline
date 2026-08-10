import os
from dotenv import load_dotenv
from sqlalchemy import create_engine, text

# Load all variables from .env file into Python's environment

load_dotenv()

# Build the connection string using those variables

engine = create_engine(
f"postgresql://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
    f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}"
)

# Open a connection and run a test query

with engine.connect() as conn:
    result = conn.execute(text("SELECT version();"))
    print("Connected successfully," , result.fetchone()[0])
