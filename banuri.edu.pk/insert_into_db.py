import sqlite3
import csv
import os
import re
from datetime import datetime

# Database file path
db_path = "../db.sqlite"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create "dar_ul_ifta" table with new columns "logo" and "website", and insert one record
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dar_ul_ifta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        en_id TEXT,
        name TEXT,
        logo TEXT,
        website TEXT
    )
''')
cursor.execute('''
    INSERT OR IGNORE INTO dar_ul_ifta (en_id, name, logo, website) VALUES (?, ?, ?, ?)
''', ("banuri", "Banuri Town", "path/to/logo.png", "https://banuri.edu.pk"))
dar_ul_ifta_id = cursor.lastrowid  # Get the ID of the inserted row

# Create "kitab" table (top-level category)
cursor.execute('''
    CREATE TABLE IF NOT EXISTS kitab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        en_id TEXT UNIQUE,
        urdu TEXT,
        dar_ul_ifta INTEGER,
        FOREIGN KEY (dar_ul_ifta) REFERENCES dar_ul_ifta(id)
    )
''')

# Create "bab" table with reference to "kitab" (subcategory of "kitab")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS bab (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        en_id TEXT UNIQUE,
        urdu TEXT,
        kitab INTEGER,
        dar_ul_ifta INTEGER,
        FOREIGN KEY (kitab) REFERENCES kitab(id),
        FOREIGN KEY (dar_ul_ifta) REFERENCES dar_ul_ifta(id)
    )
''')

# Create "fasal" table with reference to "bab" (subcategory of "bab")
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fasal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        en_id TEXT UNIQUE,
        urdu TEXT,
        bab INTEGER,
        dar_ul_ifta INTEGER,
        FOREIGN KEY (bab) REFERENCES bab(id),
        FOREIGN KEY (dar_ul_ifta) REFERENCES dar_ul_ifta(id)
    )
''')

# Create "fatwa" table with issued_at as DATE
cursor.execute('''
    CREATE TABLE IF NOT EXISTS fatwa (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        fatwa_number TEXT,
        dar_ul_ifta INTEGER,
        link TEXT,
        title TEXT,
        question TEXT,
        answer TEXT,
        kitab INTEGER,
        bab INTEGER,
        fasal INTEGER,
        issued_at DATE,
        created_at TEXT DEFAULT CURRENT_TIMESTAMP,
        updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (dar_ul_ifta) REFERENCES dar_ul_ifta(id),
        FOREIGN KEY (kitab) REFERENCES kitab(id),
        FOREIGN KEY (bab) REFERENCES bab(id),
        FOREIGN KEY (fasal) REFERENCES fasal(id)
    )
''')

# Create FTS5 virtual table for full-text search on title
cursor.execute('''
    CREATE VIRTUAL TABLE IF NOT EXISTS fatwa_fts USING fts5(
        title, content='fatwa', content_rowid='id'
    )
''')

# Function to extract Urdu and English text without quotes
def extract_urdu_english(text):
    match = re.match(r"\('(.+?)',\s*'(.+?)'\)", text)
    return match.groups() if match else (text, "")

# Function to parse and format issued_at date
def parse_date(date_str):
    try:
        return datetime.strptime(date_str, "%d-%m-%Y").strftime("%Y-%m-%d")
    except ValueError:
        return None

# Process CSV files in the "data" folder
data_folder = "./data"
for filename in os.listdir(data_folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(data_folder, filename)
        
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract and insert into "kitab", "bab", and "fasal" tables
                kitab_id, bab_id, fasal_id = None, None, None
                
                # Insert into "kitab" table
                urdu_kitab, en_kitab = extract_urdu_english(row['kitab'])
                cursor.execute('''
                    INSERT OR IGNORE INTO kitab (en_id, urdu, dar_ul_ifta)
                    VALUES (?, ?, ?)
                ''', (en_kitab, urdu_kitab, dar_ul_ifta_id))
                cursor.execute('SELECT id FROM kitab WHERE en_id = ?', (en_kitab,))
                kitab_id = cursor.fetchone()[0]

                # Insert into "bab" table, linked to "kitab"
                urdu_bab, en_bab = extract_urdu_english(row['bab'])
                cursor.execute('''
                    INSERT OR IGNORE INTO bab (en_id, urdu, kitab, dar_ul_ifta)
                    VALUES (?, ?, ?, ?)
                ''', (en_bab, urdu_bab, kitab_id, dar_ul_ifta_id))
                cursor.execute('SELECT id FROM bab WHERE en_id = ?', (en_bab,))
                bab_id = cursor.fetchone()[0]

                # Insert into "fasal" table, linked to "bab"
                urdu_fasal, en_fasal = extract_urdu_english(row['fasal'])
                cursor.execute('''
                    INSERT OR IGNORE INTO fasal (en_id, urdu, bab, dar_ul_ifta)
                    VALUES (?, ?, ?, ?)
                ''', (en_fasal, urdu_fasal, bab_id, dar_ul_ifta_id))
                cursor.execute('SELECT id FROM fasal WHERE en_id = ?', (en_fasal,))
                fasal_id = cursor.fetchone()[0]

                # Format issued_at date for SQLite
                issued_at_date = parse_date(row['issued_at'])
                
                # Insert into "fatwa" table
                cursor.execute('''
                    INSERT INTO fatwa (
                        fatwa_number, dar_ul_ifta, link, title, question, answer,
                        kitab, bab, fasal, issued_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    row['fatwa_number'], dar_ul_ifta_id, row['link'], row['title'],
                    row['question'], row['answer'], kitab_id, bab_id, fasal_id,
                    issued_at_date
                ))
                fatwa_id = cursor.lastrowid  # Get the inserted fatwa ID

                # Insert into FTS table for full-text search on title
                cursor.execute('''
                    INSERT INTO fatwa_fts(rowid, title) VALUES (?, ?)
                ''', (fatwa_id, row['title']))

# Create indexes on dar_ul_ifta, kitab, bab, and fasal columns for fast searching
for column in ["dar_ul_ifta", "kitab", "bab", "fasal"]:
    cursor.execute(f'''
        CREATE INDEX IF NOT EXISTS idx_fatwa_{column} ON fatwa ({column})
    ''')

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully, data inserted with full-text search and indexes.")
