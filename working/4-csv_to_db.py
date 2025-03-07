import os
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Database file
DB_FILE = "fatawa.db"

# Directory containing CSV files
CSV_DIR = "../4-darulifta-deoband.com/data/"

# Function to clean HTML content
def clean_html(html):
    if not isinstance(html, str):
        return ""
    return BeautifulSoup(html, "html.parser").get_text()

# Function to standardize date format
def standardize_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%b-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str

# Function to process a single CSV file
def process_csv(file_path, conn):
    df = pd.read_csv(file_path, dtype=str).fillna("")

    for _, row in df.iterrows():
        fatwa_number = row["fatwa_number"]
        link = row["link"]
        title = clean_html(row["title"])
        question = row["question"]
        answer = row["answer"]
        fatwa_issued_at = standardize_date(row["issued_at"])
        category_level_1 = row["category_level_1"]
        category_level_2 = row["category_level_2"]
        category_level_3 = ""
        dar_ul_ifta = "دارالعلوم دیوبند انڈیا"
        dar_ul_ifta_id = 4

        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO fatawa (fatwa_number, link, title, question, answer, 
                               category_level_1, category_level_2, category_level_3, 
                               fatwa_issued_at, dar_ul_ifta, dar_ul_ifta_id) 
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fatwa_number, link, title, question, answer, category_level_1, category_level_2, category_level_3, fatwa_issued_at, dar_ul_ifta, dar_ul_ifta_id))
        
        # Get the last inserted row ID
        row_id = cursor.lastrowid

        # Insert into FTS table
        cursor.execute("INSERT INTO fatawa_fts (rowid, title) VALUES (?, ?)", (row_id, title))

        conn.commit()

# Main script
def main():
    conn = sqlite3.connect(DB_FILE)
    
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
