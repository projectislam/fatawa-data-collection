import os
import csv
import requests
from bs4 import BeautifulSoup
import cloudscraper
import time

base_url = "https://darultaqwa.org/darulifta/"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

scraper = cloudscraper.create_scraper()

def save_to_csv(filename, data_rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

def get_topic_list():
    try:
        response = requests.get(base_url)
    except Exception as e:
        try:
            response = scraper.get(base_url)
        except Exception as e2:
            time.sleep(1)
            response = scraper.get("http://darultaqwa.org/darulifta/")

    soup = BeautifulSoup(response.text, "html.parser")

    menu_items = soup.select("nav > ul.elementor-nav-menu > li")

    topics = []

    for menu_item in menu_items:
        menu_link_ele = menu_item.select_one("a")
        menu_title = menu_link_ele.get_text().strip()
        menu_link = menu_link_ele.get("href")

        submenu_items = menu_item.select("ul.sub-menu > li")

        sub_topics = []

        for submenu in submenu_items:
            link_ele = submenu.select_one("a")
            title = link_ele.get_text().strip()
            link = link_ele.get("href")

            sub_topics.append({
                "link": link,
                "title": title
            })
        
        topics.append({
            "link": menu_link,
            "title": menu_title,
            "sub_topics": sub_topics
        })

    return topics

def get_total_pages(topic):
    link = topic["link"]
    try:
        response = requests.get(link)
    except Exception as e:
        try:
            response = scraper.get(link)
        except Exception as e2:
            link = link.replace("https", "http")
            response = scraper.get(link)
        
    soup = BeautifulSoup(response.text, "html.parser")

    last_link = soup.select_one("div.pagination-wrap > ul.pagination > li:nth-last-child(2) > a")

    return int(last_link.get_text().strip())

def get_page_link(page_number, topic):
    link = topic["link"]

    if page_number == 1:
        return link
    
    return f"{link}page/{page_number}"
        

def get_question_list(page_link):
    try:
        response = requests.get(page_link)
    except Exception as e:
        try:
            response = scraper.get(page_link)
        except Exception as e2:
            page_link = page_link.replace("https",  "http")
            response = scraper.get(page_link)

    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.row > div.content-section > div.blg-pst-wrp > div.post")

    questions = []

    for item in items:
        link_ele = item.select_one("div.post-inf > h4 > a")
        link = link_ele.get("href")
        title = link_ele.get_text().strip()

        questions.append({
            "link": link,
            "title": title
        })

    return questions


def get_question_detail(question):
    link = question["link"]
    
    try:
        response = requests.get(link)
    except Exception as e:
        response = scraper.get(link)

    soup = BeautifulSoup(response.text, "html.parser")

    html_ele = soup.select_one("div.blog-detail-wrp > div.row div.post > div.blog-detail")

    fatwa_number_ele = html_ele.select_one("div.blog-detail-inf ul > li:nth-child(1)")
    date_ele = html_ele.select_one("div.blog-detail-inf ul > li:nth-child(2)")
    topic_ele = html_ele.select_one("div.blog-detail-inf ul > li:nth-child(3)")

    fatwa_number = fatwa_number_ele.get_text().strip().split(":")[1] if fatwa_number_ele.get_text().strip() else ""
    date = date_ele.get_text().strip().split(":")[1] if date_ele.get_text() else ""
    category_lvl_1 = topic_ele.select_one("a:nth-child(2)").get_text().strip() if topic_ele.select_one("a:nth-child(2)") else ""
    category_lvl_2 = topic_ele.select_one("a:nth-child(3)").get_text().strip() if topic_ele.select_one("a:nth-child(3)") else ""

    container = html_ele.select_one("div.blog-detail-desc h3")

    question_html = ""
    answer_html = ""

    if not container:
        container = html_ele.select_one("div.blog-detail-desc p")
        question_html += str(container)

    paras = container.find_next_siblings()

    answer_start = False

    for para in paras:
        if "fatwa-ans" in para.get("class", []):
            answer_start = True
            continue

        if "pst-shr-tgs" in para.get("class", []):
            break

        if answer_start:
            answer_html += str(para)
        else:
            question_html += str(para)

    if not answer_html:
        answer_html = question_html
        question_html = ""

    
    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "date": date,
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "fatwa_number": fatwa_number,
        "html_container": str(html_ele)
    }

topics = get_topic_list()
total_topics = len(topics)

print(total_topics, "total topics found")

for topic_index, topic in enumerate(topics, 1):
    if topic_index < 10:
        continue

    print(f"{topic_index}/{total_topics}", topic["link"])

    total_pages = get_total_pages(topic)

    print(total_pages, "total pages found")

    for page_number in range(1, total_pages + 1):
        if topic_index == 10 and page_number < 136:
            continue

        page_link = get_page_link(page_number, topic)

        print("Fetching page...", page_link)

        questions = get_question_list(page_link)
        total_questions = len(questions)

        print(total_questions, "total questions found")

        data_rows = []

        for question_index, question in enumerate(questions, 1):
            print(f"Topic({topic_index}/{total_topics}) Page({page_number}/{total_pages}) Q({question_index}/{total_questions})", question["link"])

            content = get_question_detail(question)

            data_rows.append({
                "link": question["link"],
                "title": question["title"],
                "question_html": content["question_html"],
                "answer_html": content["answer_html"],
                "fatwa_number": content["fatwa_number"],
                "issued_at": content["date"],
                "category_lvl_1": content["category_lvl_1"],
                "category_lvl_2": content["category_lvl_2"],
                "html_container": content["html_container"],
                "dar_ul_ifta": "darultaqwa.org"
            })

        filename = f"{data_dir}/{topic_index}-{page_number}.csv"
        save_to_csv(filename, data_rows)


print("END")
