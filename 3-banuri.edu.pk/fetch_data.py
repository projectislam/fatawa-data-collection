import os
import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://www.banuri.edu.pk"
data_dir = "./data"

sawal_text = "سوال"
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

def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("div.listing-bok ul.list-question > li > a")

    questions = []

    for item in items:
        title = item.get_text().strip()
        link = item.get("href")

        questions.append({
            "title": title,
            "link": link
        })

    return questions


def get_question_detail(question):
    link = question["link"]

    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    date = link.split('/')[-1]

    html_container = soup.select_one("div.listing-bok > div.row > div.sawal-jawab")
    paras = html_container.find("h3").find_next_siblings()

    question_html = ""
    answer_html = ""

    answer_start = False

    for para in paras:
        text = para.get_text().strip()

        if jawab_text in text:
            answer_start = True

        if answer_start:
            answer_html += str(para)
        else:
            question_html += str(para)

        if para.name == "hr" and "big-hr" in para.get("class", []):
            break

    fatwa_number_ele = html_container.select_one("#fatwa_number")
    fatwa_number = fatwa_number_ele.get_text().strip() if fatwa_number_ele else ""

    tags = html_container.select("div.tag > a")

    category_lvl_1 = ""
    category_lvl_2 = ""
    category_lvl_3 = ""

    for tag in tags:
        link = tag.get("href")
        text = tag.get_text().strip()

        if "/questions/kitab" in link:
            category_lvl_1 = text
        elif "/questions/bab" in link:
            category_lvl_2 = text
        elif "/questions/fasal" in link:
            category_lvl_3 = text

    return {
        "link": link,
        "question_html": question_html,
        "answer_html": answer_html,
        "date": date,
        "fatwa_number": fatwa_number,
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "category_lvl_3": category_lvl_3,
        "html_container": str(html_container)
    }

total_pages = 1248
start_page = 1

for page_number in range(start_page, total_pages + 1):
    page_link = f"{base_url}/new-questions/page/{page_number}"

    print("Fetching...", page_number, page_link)

    questions = get_question_list(page_link)
    total_questions = len(questions)

    print(total_questions, "total questions found on page", page_number)

    data_rows = []

    for question_number, question in enumerate(questions, 1):
        print(page_number, f"{question_number}/{total_questions}", question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "issued_at": content["date"],
            "fatwa_number": content["fatwa_number"],
            "dar_ul_ifta": "banuri.edu.pk",
            "category_lvl_1": content["category_lvl_1"],
            "category_lvl_2": content["category_lvl_2"],
            "category_lvl_3": content["category_lvl_3"],
            "html_container": content["html_container"]
        })

        break

    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)

    break

print("END")