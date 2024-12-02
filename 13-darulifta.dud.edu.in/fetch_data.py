import os
import csv
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options

options = Options()
options.page_load_strategy = 'eager'
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = webdriver.Chrome(options=options)

base_url = "https://darulifta.dud.edu.in"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

page_link = f"{base_url}/search?s="

driver.get(page_link)

sequence_number = 1

while True:
    html_container_ele = driver.find_element(By.ID, "accordionExample")
    html_container = html_container_ele.get_attribute("outerHTML")

    items = html_container_ele.find_elements(By.CSS_SELECTOR, "#accordionExample > div.card")
    
    print(len(items), "total question found")

    data_rows = []

    for item in items:
        title_ele = item.find_element(By.CSS_SELECTOR, "div.card-header > h2")
        category_lvl_1_ele = item.find_element(By.CSS_SELECTOR, "div.card-header > span.badge")
        answer_ele = item.find_element(By.CSS_SELECTOR, "div.collapse > div.card-body")
        fatwa_number_elements = answer_ele.find_elements(By.CSS_SELECTOR, "p:nth-child(1)")
        fatwa_number_ele = fatwa_number_elements[0] if fatwa_number_elements else None

        title = title_ele.text.strip()
        category_lvl_1 = category_lvl_1_ele.text.strip()
        answer_html = str(answer_ele.get_attribute("outerHTML"))
        fatwa_number = fatwa_number_ele.get_attribute("innerText") if fatwa_number_ele else ""

        if "Ref. No" in fatwa_number:
             fatwa_number = fatwa_number.replace("Ref. No. ", "").strip()

        data_rows.append({
            "title": title,
            "answer_html": answer_html,
            "fatwa_number": fatwa_number,
            "category_lvl_1": category_lvl_1,
            "html_container": str(html_container),
            "dar_ul_ifta": "darulifta.dud.edu.in"
        })

    filename = f"{data_dir}/{sequence_number}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

    sequence_number += 1

    next_link = driver.find_element(By.CSS_SELECTOR, '#pagination > ul > li > a[rel="next"]')

    if not next_link:
         break
    
    next_link.click()

    


driver.quit()