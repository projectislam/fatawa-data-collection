import os
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Database file
DB_FILE = "fatawa.db"

# Directory containing CSV files
CSV_DIR = "../4-darulifta-deoband.com/data/"

# Define table schema
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS fatawa (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    fatwa_number TEXT,
    link TEXT,
    title TEXT,
    question TEXT,
    answer TEXT,
    category_level_1 TEXT,
    category_level_2 TEXT,
    category_level_3 TEXT,
    fatwa_issued_at TEXT,
    dar_ul_ifta INTEGER DEFAULT 1,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# Enable Full-Text Search (FTS5) on title column
CREATE_FTS_TABLE_QUERY = """
CREATE VIRTUAL TABLE IF NOT EXISTS fatawa_fts USING fts5(title, content='fatawa', content_rowid='id');
"""

# Function to clean HTML content
def clean_html(html):
    if not isinstance(html, str):
        return ""
    return BeautifulSoup(html, "html.parser").get_text()

# Function to standardize date format
def standardize_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return ""

# Function to process a single CSV file
def process_csv(file_path, conn):
    df = pd.read_csv(file_path, dtype=str).fillna("")

    # TODO: find data folder and work

    for _, row in df.iterrows():
        fatwa_number = row["fatwa_number"] if row["fatwa_number"].isdigit() else ""
        link = row["link"]
        title = clean_html(row["title"])
        question = row["question"]
        answer = row["answer"]
        fatwa_issued_at = row["issued_at"]
        category_level_1 = row["category_lvl_1"]
        category_level_2 = row["category_lvl_2"]
        category_level_3 = row["category_lvl_3"]
        dar_ul_ifta = 4

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fatawa (fatwa_number, link, title, question, answer, 
                               category_level_1, category_level_2, category_level_3, 
                               fatwa_issued_at, dar_ul_ifta) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fatwa_number, link, title, question, answer, category_level_1, category_level_2, category_level_3, fatwa_issued_at, dar_ul_ifta))
        
        # Get the last inserted row ID
        row_id = cursor.lastrowid

        # Insert into FTS table
        cursor.execute("INSERT INTO fatawa_fts (rowid, title) VALUES (?, ?)", (row_id, title))

        conn.commit()

# Main script
def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute(CREATE_TABLE_QUERY)
    cursor.execute(CREATE_FTS_TABLE_QUERY)
    conn.commit()

    # Process each CSV file
    for file_name in os.listdir(CSV_DIR):
        if file_name.endswith(".csv"):
            file_path = os.path.join(CSV_DIR, file_name)
            print(f"Processing: {file_name}")
            process_csv(file_path, conn)
        exit()

    conn.close()
    print("Data import complete!")

if __name__ == "__main__":
    main()
