import os
from dbm import sqlite3
from fastapi import HTTPException, FastAPI

import pandas as pd
from sqlalchemy import create_engine
from sqlmodel import Session

from Models.user_models import *

sqlite_file_name = "formula1.sqlite"
engine = create_engine(f"sqlite:///{sqlite_file_name}", echo=True)

DATA_FOLDER = "data"  # Folder where CSV files are stored

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

def get_session():
    with Session(engine) as session:
        yield session

def load_csvs_data():
    if not os.path.isdir(DATA_FOLDER):
        raise HTTPException(status_code=400, detail="Data folder not found")

    loaded_tables = []

    # Use raw sqlite3 to clear tables before inserting
    conn = sqlite3.connect(sqlite_file_name)
    cursor = conn.cursor()

    for filename in os.listdir(DATA_FOLDER):
        if filename.endswith(".csv"):
            table_name = filename.replace(".csv", "")
            file_path = os.path.join(DATA_FOLDER, filename)
            try:
                df = pd.read_csv(file_path)

                # Clear the table first
                cursor.execute(f"DELETE FROM {table_name}")
                conn.commit()

                # Insert CSV data
                df.to_sql(table_name, con=conn, if_exists="append", index=False)
                loaded_tables.append({"table": table_name, "rows": len(df)})

            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Error loading {filename}: {e}")

    conn.close()
    return {"status": "success", "tables_loaded": loaded_tables}