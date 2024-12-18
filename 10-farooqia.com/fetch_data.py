import os
import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://www.farooqia.com/%D8%AF%D8%A7%D8%B1%D8%A7%D9%84%D8%A7%D9%81%D8%AA%D8%A7%D8%A1/page"

data_dir = "./data"

jawab_text = "جواب"

os.makedirs(data_dir, exist_ok=True)

def save_to_csv(filename, data_rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

def get_question_list(link):
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.gdlr-core-pbf-element > div.gdlr-core-course-style-list > div.gdlr-core-course-item-list")

    questions = []

    for item in items:
        link_ele = item.select_one("a")
        fatwa_ele = link_ele.select_one("span.gdlr-core-course-item-id")
        title_ele = link_ele.select_one("span.gdlr-core-course-item-title")

        link = link_ele.get("href")
        title = title_ele.get_text().strip()
        fatwa_number = fatwa_ele.get_text().strip() if fatwa_ele else ""

        questions.append({
            "link": link,
            "title": title,
            "fatwa_number": fatwa_number
        })

    return questions

def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_ele = soup.select_one("div.gdlr-core-pbf-element > div.gdlr-core-text-box-item > div.gdlr-core-text-box-item-content")
    container_ele = html_ele.select_one("h4") or html_ele.select_one("h3")  or html_ele.select_one("h2")  or html_ele.select_one("h1")
    paras = container_ele.find_next_siblings()

    question_html = ""
    answer_html = ""
    answer_start = False

    for para in paras:
        text = para.get_text().strip()

        if jawab_text in text:
            answer_start = True
            continue

        if answer_start:
            answer_html += str(para)
        else:
            question_html += str(para)

    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "html_container": str(html_ele)
    }

        

total_pages = 132
start_page = 65

for page_number in range(start_page, total_pages + 1):
    link = f"{base_url}/{page_number}"

    print(page_number, link)

    questions = get_question_list(link)

    print(len(questions), "total questions found")

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_number, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "fatwa_number": question["fatwa_number"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "html_container": content["html_container"],
            "dar_ul_ifta": "farooqia.com"
        })

        
    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)

print("END")

        