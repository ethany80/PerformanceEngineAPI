from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import os

# Create the engine (adjust the connection string as needed)
engine = create_engine(
    os.getenv("PERF_ENGINE_SQL_Connection_String"),
    echo=True,
)

# Optionally: create a configured "Session" class
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
