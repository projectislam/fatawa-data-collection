import sqlite3

# Database file
DB_FILE = "fatawa.db"

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
    dar_ul_ifta TEXT,
    dar_ul_ifta_id INTEGER,
    is_favorite INTEGER NOT NULL CHECK (is_favorite IN (0,1)) DEFAULT 0,
    fatwa_issued_at TEXT,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT DEFAULT CURRENT_TIMESTAMP
);
"""

# Main script
def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute(CREATE_TABLE_QUERY)
    conn.commit()

    conn.close()
    print("Database table created")

if __name__ == "__main__":
    main()