import sqlite3
import csv
import os
import re

# Database file path
db_path = "../db.sqlite"

# Connect to SQLite database
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Create "dar_ul_ifta" table and insert one record
cursor.execute('''
    CREATE TABLE IF NOT EXISTS dar_ul_ifta (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        en_id TEXT,
        name TEXT
    )
''')
cursor.execute('''
    INSERT OR IGNORE INTO dar_ul_ifta (en_id, name) VALUES (?, ?)
''', ("banuri", "Banuri Town"))
dar_ul_ifta_id = cursor.lastrowid  # Get the ID of the inserted row

# Create "kitab", "bab", and "fasal" tables with unique en_id constraint
for table_name in ["kitab", "bab", "fasal"]:
    cursor.execute(f'''
        CREATE TABLE IF NOT EXISTS {table_name} (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            en_id TEXT UNIQUE,
            urdu TEXT,
            dar_ul_ifta INTEGER,
            FOREIGN KEY (dar_ul_ifta) REFERENCES dar_ul_ifta(id)
        )
    ''')

# Function to extract Urdu and English text without quotes
def extract_urdu_english(text):
    match = re.match(r"\('(.+?)',\s*'(.+?)'\)", text)
    return match.groups() if match else (text, "")

# Process CSV files in the "data" folder
data_folder = "./data"
for filename in os.listdir(data_folder):
    if filename.endswith(".csv"):
        filepath = os.path.join(data_folder, filename)
        
        with open(filepath, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                # Extract and insert into "kitab", "bab", and "fasal" tables
                for table_name in ["kitab", "bab", "fasal"]:
                    urdu, english = extract_urdu_english(row[table_name])
                    # Insert only if en_id does not already exist
                    cursor.execute(f'''
                        INSERT OR IGNORE INTO {table_name} (en_id, urdu, dar_ul_ifta)
                        VALUES (?, ?, ?)
                    ''', (english, urdu, dar_ul_ifta_id))

# Commit changes and close the connection
conn.commit()
conn.close()

print("Database and tables created successfully, data inserted.")
