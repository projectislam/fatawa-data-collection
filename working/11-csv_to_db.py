import os
import re
import sqlite3
import pandas as pd
from bs4 import BeautifulSoup
from datetime import datetime

# Database file
DB_FILE = "fatawa.db"

# Directory containing CSV files
CSV_DIR = "../11-darultaqwa.org/data/"

# Function to clean HTML content
def clean_html(html):
    if not isinstance(html, str):
        return ""
    html = html.replace("/", "&#47;")
    return BeautifulSoup(html, "html.parser").get_text()

def clear_style(html):
    if not html:
        return html
    
    return re.sub(r'<(\w+)(\s+[^>]*)?>', r'<\1>', html)

# Function to standardize date format
def standardize_date(date_str):
    try:
        urdu_to_english_months = {
            "جنوری": "January", "فروری": "February", "مارچ": "March", "اپریل": "April",
            "مئی": "May", "جون": "June", "جولائی": "July", "اگست": "August",
            "ستمبر": "September", "اکتوبر": "October", "نومبر": "November", "دسمبر": "December"
        }
        match = re.search(r'(\d{1,2}) (\w+) (\d{4})', date_str)
        day, urdu_month, year = match.groups()
        english_month = urdu_to_english_months.get(urdu_month, "")
        return datetime.strptime(f"{day} {english_month} {year}", "%d %B %Y").strftime("%Y-%m-%d")
    except ValueError:
        return date_str

# Function to process a single CSV file
def process_csv(file_path, conn):
    df = pd.read_csv(file_path, dtype=str).fillna("")

    for _, row in df.iterrows():
        fatwa_number = row["fatwa_number"]
        link = row["link"]
        title = clean_html(row["title"])
        question = clear_style(row["question_html"])
        answer = clear_style(row["answer_html"])
        fatwa_issued_at = standardize_date(row["issued_at"])
        category_level_1 = row["category_lvl_1"]
        category_level_2 = row["category_lvl_2"]
        category_level_3 = ""
        dar_ul_ifta = "دارالافتاء جامعہ دار التقوی لاہور"
        dar_ul_ifta_id = 11

        cursor = conn.cursor()

        cursor.execute("""
            SELECT COUNT(*) FROM fatawa WHERE title = ? AND dar_ul_ifta_id = ?
        """, (title, dar_ul_ifta_id))
                
        if cursor.fetchone()[0] == 0:

            cursor.execute("""
                INSERT INTO fatawa (fatwa_number, link, title, question, answer, 
                                category_level_1, category_level_2, category_level_3, 
                                fatwa_issued_at, dar_ul_ifta, dar_ul_ifta_id) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (fatwa_number, link, title, question, answer, category_level_1, category_level_2, category_level_3, fatwa_issued_at, dar_ul_ifta, dar_ul_ifta_id))
            
            # Get the last inserted row ID
            # row_id = cursor.lastrowid

            # Insert into FTS table
            # cursor.execute("INSERT INTO fatawa_fts (rowid, title) VALUES (?, ?)", (row_id, title))

            conn.commit()

# Main script
def main():
    conn = sqlite3.connect(DB_FILE)

    count = 0

    # Process each CSV file
    for file_name in os.listdir(CSV_DIR):
        if file_name.endswith(".csv"):
            file_path = os.path.join(CSV_DIR, file_name)
            print(f"Processing: {file_name}")
            process_csv(file_path, conn)
        
            count = count + 1

            if count == 10:
                # pass
                exit(1)

    conn.close()
    print("Data import complete!")

if __name__ == "__main__":
    main()
