import undetected_chromedriver as uc
from bs4 import BeautifulSoup
import json
import time

options = uc.ChromeOptions()
driver = uc.Chrome(version_main=130, options=options)  # Adjust the version to match Chrome version
driver.get("https://darulifta-deoband.com/")

# Wait for Cloudflare to complete verification
# driver.implicitly_wait(10)
time.sleep(8)

soup = BeautifulSoup(driver.page_source, "html.parser")
containers = soup.select("#navMenu > ul > li.menu_items_mega > ul > li > div > div > .cat_part_sec")

data = []
for container in containers:
    kitab_name = container.find("h3").get_text(strip=True)
    babs = container.select(".sub_level_menu > li > a")
    for bab in babs:
        data.append({
            "kitab": kitab_name,
            "bab": bab.get_text(strip=True),
            "link": bab["href"]
        })

with open("topics.json", "w", encoding="utf-8") as f:
    json.dump(data, f, ensure_ascii=False, indent=4)

driver.quit()
