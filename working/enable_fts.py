import sqlite3
import re
from bs4 import BeautifulSoup  # Install with `pip install beautifulsoup4`

# Connect to your SQLite database
db_path = "fatawa.db"  # Change this to your actual DB path
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1️⃣ Create FTS5 Virtual Table (External Content Mode to Reduce Size)
cursor.execute("""
    CREATE VIRTUAL TABLE IF NOT EXISTS fatawa_fts USING fts5(
        title, question, answer,
        content='fatawa',
        content_rowid='id',
        tokenize='unicode61 remove_diacritics 1'
    );
""")

conn.commit()

# 2️⃣ Function to Remove HTML and Extract Plain Text
def clean_html(html):
    if not isinstance(html, str):
        return ""
    html = html.replace("/", "&#47;")
    return BeautifulSoup(html, "html.parser").get_text()

# 3️⃣ Populate FTS Table with Cleaned Data
# cursor.execute("DELETE FROM fatawa_fts;")  # Clear old data if exists

# conn.commit()

cursor.execute("SELECT id, title, question, answer FROM fatawa;")
rows = cursor.fetchall()

for row in rows:
    id_, title, question, answer = row

    print(f"Processing row {id_}")
    clean_question = clean_html(question)
    clean_answer = clean_html(answer)
    
    cursor.execute("""
        INSERT INTO fatawa_fts (rowid, title, question, answer)
        VALUES (?, ?, ?, ?);
    """, (id_, title, clean_question, clean_answer))

# 4️⃣ Commit and Optimize Database
conn.commit()
cursor.execute("INSERT INTO fatawa_fts(fatawa_fts) VALUES ('rebuild');")  # Optimize FTS index
conn.commit()

# Close connection
conn.close()

print("FTS5 is now enabled with cleaned text!")
