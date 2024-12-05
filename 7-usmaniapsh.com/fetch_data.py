import requests
import os
import csv
import time
from bs4 import BeautifulSoup

base_url = "https://usmaniapsh.com/new_questions"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

def save_to_csv(filename, data_rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

def get_page_number(page):
    if page == 0:
        return ""
    
    return page * 30

def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.listing-bok ul.list-question li")

    questions = []

    for item in items:
        linkEle = item.select_one("a")
        title = linkEle.get_text().strip()
        link = linkEle.get("href")

        questions.append({
            "title": title,
            "link": link
        })

    return questions

def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_container = soup.select_one("div.listing-bok > div.row div.sawal-jawab")

    paras = html_container.select_one("h3.question_heading").find_next_siblings()

    question_html = ""

    for para in paras:
        if "question_heading" in para.get("class", []):
            break

        question_html += str(para)

    answerEle = soup.select_one("div.listing-bok div.col-md-12.sawal-jawab > div.sawal_jawab")
    fatwaEle = soup.select_one("#fatwa_number")
    dateELe = soup.select_one("div.listing-bok div.col-md-12.sawal-jawab > div.row > div:nth-child(3)")
    tagsEle = soup.select("div.listing-bok div.col-md-12.sawal-jawab a")

    answer_html = str(answerEle)
    fatwa_number = fatwaEle.get_text().strip()
    date = dateELe.get_text().replace("تاریخ تصدیق :", "").strip()
    category_lvl_1 = ""
    category_lvl_2 = ""
    category_lvl_3 = ""

    if not question_html or not answer_html:
        raise ValueError("Question or answer content not found")

    for tag in tagsEle:
        href = tag.get("href", None)
        text = tag.get_text().strip()

        if not href:
            continue

        if "/search_individual/kitab/" in href:
            category_lvl_1 = text
        elif "/search_individual/baab/" in href:
            category_lvl_2 = text
        elif "/search_individual/fasal/" in href:
            category_lvl_3 = text

    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "fatwa_number": fatwa_number,
        "date": date,
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "category_lvl_3": category_lvl_3,
        "html_container": str(html_container)
    }


total_pages = 148
start_page = 0 # start from 0

for page in range(start_page, total_pages + 1):
    page_number = get_page_number(page)
    page_link = f"{base_url}/{page_number}"

    print("Fetching page...", page_link)

    questions = get_question_list(page_link)

    print(len(questions), "total question found on page number", start_page)

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(start_page, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "issued_at": content["date"],
            "fatwa_number": content["fatwa_number"],
            "dar_ul_ifta": "usmaniapsh.com",
            "category_lvl_1": content["category_lvl_1"],
            "category_lvl_2": content["category_lvl_2"],
            "category_lvl_3": content["category_lvl_3"],
            "html_container": content["html_container"]
        })

    filename = f"{data_dir}/{page}.csv"
    save_to_csv(filename, data_rows)

print("END")