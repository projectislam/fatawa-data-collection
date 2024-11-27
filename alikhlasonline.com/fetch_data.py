import requests
import os
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

base_url = "https://alikhlasonline.com"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.col-md-8.minHeight > div.col-lg-12 > div.UrduTextNafeesPara")

    questions = []

    for item in items:
        linkEle = item.select_one("a")

        title = linkEle.get_text().strip()
        link = linkEle.get("href")
        
        if "http" not in link:
            link = f"{base_url}{link}"
        
        questions.append({
            "title": title,
            "link": link
        })

    return questions


def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    question_ele = soup.select_one("#printthis > div:nth-child(2)")
    answer_ele = soup.select_one("#printthis > div:nth-child(3)")
    date_ele = soup.select_one("#form1 > div:nth-child(9) > div > div.col-md-8.minHeight > div:nth-child(1) > div.text-left.hidden-print > table > tr > td:nth-child(4)")

    question_html = str(question_ele)
    question_html = question_html.replace('<b class="text-danger">سوال: </b>', "")

    answer_html = str(answer_ele)
    answer_html = answer_html.replace('<b class="text-danger">جواب: </b>', "")

    date = date_ele.get_text().strip()

    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    fatwa_number = query_params.get("id", [None])[0]

    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "fatwa_number": fatwa_number,
        "date": date
    }


total_pages = 224
start_page = 1

page_number = 1

page_link = f"{base_url}/allquestions.aspx?lang=1&page={page_number}"

questions = get_question_list(page_link)

print(questions[:3])

question = questions[0]

content = get_question_detail(question)

print(content)