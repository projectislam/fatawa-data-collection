import os
import csv
import time
import json
from bs4 import BeautifulSoup
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options


base_url = "https://darulifta-deoband.com"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)


options = Options()
options.page_load_strategy = 'eager' 
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")
driver = uc.Chrome(options=options)

def save_to_csv(filename, data_rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)


def get_topic_list():
    driver.get(base_url)
    time.sleep(15)

    soup = BeautifulSoup(driver.page_source, "html.parser")
    items = soup.select("#navMenu > ul > li.menu_items_mega > ul > li > div > div > .cat_part_sec")

    data = []

    for item in items:
        category_lvl_1 = item.find("h3").get_text(strip=True)
        subitems = item.select(".sub_level_menu > li > a")

        for subitem in subitems:
            link = subitem.get("href")
            text = subitem.get_text().strip()

            data.append({
                "category_lvl_1": category_lvl_1,
                "category_lvl_2_link": link,
                "category_lvl_2_text": text
            })

    return data

def get_topic_total_pages(topic_link):
    driver.get(topic_link)
    last_page_link = driver.find_element(By.CSS_SELECTOR, "#midle_content > div > div:nth-child(2) > nav > ul > li:last-child > a")
    total_pages = int(last_page_link.get_attribute("href").split("=")[-1])

    return total_pages

def get_question_list(page_link):
    driver.get(page_link)
    items = driver.find_elements(By.CSS_SELECTOR, "#recent_fatwas > ul > li")

    questions = []

    for item in items:
        link_ele = item.find_element(By.TAG_NAME, "a")
        link = link_ele.get_attribute("href")
        title = link_ele.text.replace("Q.", "").strip()

        questions.append({
            "link": link,
            "title": title
        })

    return questions

def get_question_detail(question):
    link = question["link"]
    driver.get(link)

    html_container_ele = driver.find_element(By.ID, 'recent_fatwas')
    html_container = html_container_ele.get_attribute("outerHTML")

    fatwa_number_ele = html_container_ele.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > div > p.quesid > span")
    fatwa_number = fatwa_number_ele.text.split(":")[-1].strip() if fatwa_number_ele else ""
    
    date_ele = html_container_ele.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > p.fatwa_answer > span.answer_date_urdu")
    date = date_ele.get_attribute("innerHTML").split(":")[0].strip() if date_ele else ""
    
    container = html_container_ele.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > h2")
    paras = container.find_elements(By.XPATH, "following-sibling::*")

    question_html = ""
    answer_html = ""

    answer_start = False

    for para in paras:
        if "fatwa_answer" in para.get_attribute("class"):
            answer_start = True
            continue

        if answer_start:
            answer_html += str(para.get_attribute("outerHTML"))
        else:
            question_html += str(para.get_attribute("outerHTML"))

    return {
        "link": question_link,
        "question_html": question_html,
        "answer_html": answer_html,
        "date": date,
        "fatwa_number": fatwa_number,
        "html_container": str(html_container)
    }

topics = get_topic_list()
total_topics = len(topics)

print(total_topics, "total topics found")

for topic_number, topic in enumerate(topics, 1):
    category_lvl_1 = topic["category_lvl_1"]
    category_lvl_2 = topic["category_lvl_2_text"]
    topic_link = topic["category_lvl_2_link"]

    print("Fetching topic....", topic_link)

    total_pages = get_topic_total_pages(topic_link)
    start_page = 1

    print(total_pages, "total pages found for topic", topic_link)

    for page_number in range(start_page, total_pages + 1):
        page_link = f"{topic_link}?page={page_number}"

        info = f"Topic({topic_number}/{total_topics}) Page({page_number}/{total_pages})"
        print(info, page_link)

        questions = get_question_list(page_link)
        total_questions = len(questions)

        print(total_questions, "total questions found on", page_link)

        data_rows = []

        for question_number, question in enumerate(questions, 1):
            question_link = question["link"]

            print(info, f"{question_number}/{total_questions}", question_link)

            try:
                content = get_question_detail(question)

                data_rows.append({
                    "link": question_link,
                    "title": question["title"],
                    "question_html": content["question_html"],
                    "answer_html": content["answer_html"],
                    "issued_at": content["date"],
                    "fatwa_number": content["fatwa_number"],
                    "dar_ul_ifta": "darulifta-deoband.com",
                    "category_lvl_1": category_lvl_1,
                    "category_lvl_2": category_lvl_2,
                    "html_container": content["html_container"]
                })
            except Exception as e:
                print("Error scraping question:", e)

            break

        filename = f"{data_dir}/{topic_number}-{page_number}.csv"
        save_to_csv(filename, data_rows)

        break
    
    break

# Close browser
driver.quit()