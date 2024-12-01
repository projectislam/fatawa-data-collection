import requests
import os
import csv
import cloudscraper
from bs4 import BeautifulSoup

base_url = "https://ahnafmedia.com/darulifta"
data_dir = "./data"

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}


scraper = cloudscraper.create_scraper()

os.makedirs(data_dir, exist_ok=True)

def format_page_link(page_number):
    return f"{base_url}/?page={page_number}&filter=resolved"

def get_question_list(page_link):
    response = scraper.get(page_link)
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


def get_question_detail(question):
    link = question["link"]
    response = scraper.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_ele = soup.select_one("#content div.post-content")
    html2_ele = soup.select_one("#content div.meta-info")

    question_ele = html_ele.select_one("div.dwqa-single-question > div.dwqa-question-item > div.dwqa-question-content")
    answer_ele = html_ele.select_one("div.dwqa-single-question > div.dwqa-answers > div.dwqa-answers-list > div:nth-child(1) > div.dwqa-answer-content")

    date_ele = html2_ele.select_one("div.meta-info-wrapper > span:nth-child(3)")

    question_html = str(question_ele)
    answer_html = str(answer_ele)
    date = date_ele.get_text().strip()

    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "date": date,
        "html_container": html_ele,
        "html_container_2": html2_ele
    }


total_pages = 8
start_page = 1

for page_number in range(start_page, total_pages + 1):
    page_link = format_page_link(start_page)

    print("Page number", page_number, page_link)

    questions = get_question_list(page_link)

    print(len(questions), "total question found on page number", page_number)

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_number, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "issued_at": content["date"],
            "category_lvl_1": question["category_lvl_1"],
            "html_container": content["html_container"],
            "html_container_2": content["html_container_2"],
            "dar_ul_ifta": "ahnafmedia"
        })

    filename = f"{data_dir}/{page_number}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)


print("END")
