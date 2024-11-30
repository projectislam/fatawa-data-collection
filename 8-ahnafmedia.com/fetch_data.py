import requests
import os
import csv
from bs4 import BeautifulSoup

base_url = "https://ahnafmedia.com/darulifta"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

def format_page_link(page_number):
    return f"{base_url}/?page={page_number}&filter=resolved"

def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("#post-11513 div.dwqa-questions-list > div.dwqa-question-item")

    questions = []

    for item in items:
        link_ele = item.select_one("header.dwqa-question-title > a")
        category_ele = item.select_one("div.dwqa-question-meta > span.dwqa-question-category > a")

        link = link_ele.get("href")
        title = link_ele.get_text().strip()

        category_lvl_1 = category_ele.get_text().strip() if category_ele else ""

        questions.append({
            "link": link,
            "title": title,
            "category_lvl_1": category_lvl_1
        })

    return questions


total_page = 8
start_page = 1

page_link = format_page_link(start_page)

questions = get_question_list(page_link)

print(questions[:3])