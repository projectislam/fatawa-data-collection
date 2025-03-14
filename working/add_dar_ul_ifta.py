import sqlite3

# Database file
DB_FILE = "fatawa.db"

# Define table schema
CREATE_TABLE_QUERY = """
CREATE TABLE IF NOT EXISTS dar_ul_ifta (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    website TEXT,
    logo_path TEXT,
    list_order INTEGER
);
"""


# Main script
def main():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()

    # Create tables if they don't exist
    cursor.execute(CREATE_TABLE_QUERY)
    conn.commit()

    dar_ul_ifta_list = [
        {
            "name": "دارالافتاء، جامعہ دارالعلوم کراچی",
            "website": "https://www.suffahpk.com/category/fatawa-darul-uloom-karachi",
            "logo_path": "",
            "list_order": 1
        },
        {
            "name": "جامعہ علوم اسلامیہ علامہ محمد یوسف بنوری ٹاؤن",
            "website": "https://www.banuri.edu.pk",
            "logo_path": "",
            "list_order": 2
        },
        {
            "name": "دار الافتاء جامعۃ الرشید،کراچی",
            "website": "https://almuftionline.com/blog",
            "logo_path": "",
            "list_order": 3
        },
        {
            "name": "دارالعلوم دیوبند انڈیا",
            "website": "https://darulifta-deoband.com",
            "logo_path": "",
            "list_order": 4
        },
        
        {
            "name": "دار العلوم وقف ديوبند انڈیا",
            "website": "https://darulifta.dud.edu.in",
            "logo_path": "",
            "list_order": 5
        },
        {
            "name": "دار الافتاء جامعه بنوریه عالمیه",
            "website": "https://onlinefatawa.com",
            "logo_path": "",
            "list_order": 6
        },
        {
            "name": "دارالا فتاء جامعہ عثمانیہ پشاور",
            "website": "https://usmaniapsh.com",
            "logo_path": "",
            "list_order": 7
        },
        {
            "name": "دار الافتاء،مرکز اھل السنۃ والجماعۃ سرگودھا",
            "website": "https://ahnafmedia.com/darulifta",
            "logo_path": "",
            "list_order": 8
        },
        {
            "name": "عثمانی دارالافتاء انڈیا",
            "website": "https://www.usmanidarulifta.in",
            "logo_path": "",
            "list_order": 9
        },
        {
            "name": "دارالافتاء جامعہ فاروقیہ کراچی",
            "website": "https://www.farooqia.com",
            "logo_path": "",
            "list_order": 10
        },
        {
            "name": "دارالافتاء جامعہ دار التقوی لاہور",
            "website": "https://darultaqwa.org/darulifta",
            "logo_path": "",
            "list_order": 11
        },
        {
            "name": "جامعہ امام محمد بن الحسن الشیبانی",
            "website": "https://www.jamiamuhammad.com",
            "logo_path": "",
            "list_order": 12
        },
        {
            "name": "دارالافتاء الاخلاص",
            "website": "https://alikhlasonline.com",
            "logo_path": "",
            "list_order": 13
        },
        
    ]

    for dar_ul_ifta in dar_ul_ifta_list:
        name = dar_ul_ifta["name"]
        website = dar_ul_ifta["website"]
        logo_path = dar_ul_ifta["logo_path"]
        list_order = dar_ul_ifta["list_order"]

        cursor.execute("""
                INSERT INTO dar_ul_ifta (name, website, logo_path, list_order) 
                VALUES (?, ?, ?, ?)
            """, (name, website, logo_path, list_order))
        
        conn.commit()

    conn.close()
    print("Dar ul ifta added in table")

if __name__ == "__main__":
    main()