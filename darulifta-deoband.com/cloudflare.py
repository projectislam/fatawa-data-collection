import cloudscraper

scraper = cloudscraper.create_scraper()  # Initialize the scraper
response = scraper.get("https://darulifta-deoband.com/home/qa_ur/islamic-beliefs/1")

if response.status_code == 200:
    print(response.text)  # Page content if bypass was successful
else:
    print("Failed to bypass Cloudflare.")
