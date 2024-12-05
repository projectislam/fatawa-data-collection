import os
import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://www.jamiamuhammad.com"
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

def get_page_link(page_number):
    if page_number == 1:
        return f"{base_url}/new_questions"
    
    count = (page_number - 1) * 20

    return f"{base_url}/Frontend/new_questions/{count}"


def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("#mainContent > div > div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div:nth-child(1) > div > div > div.col-lg-12.col-md-12.col-sm-12.col-xs-12")

    questions = []

    for item in items:
        link_ele = item.select_one("a")
        link = link_ele.get("href")

        questions.append({
            "link": link
        })
    
    return questions

def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_container = soup.select_one("#mainContent > div > div.col-lg-8.col-md-8.col-sm-12.col-xs-12 > div > div")

    title_ele = html_container.select_one("h1")
    question_html = html_container.select_one("#divPrint > div:nth-child(1)")
    answer_html = html_container.select_one("#divPrint > div:nth-child(2)")

    title = title_ele.get_text().strip()
    question_html = str(question_html)
    answer_html = str(answer_html)

    return {
        "title": title,
        "question_html": question_html,
        "answer_html": answer_html,
        "html_container": str(html_container)
    }

total_pages = 8
start_page = 1

for page_number in range(start_page, total_pages + 1):
    page_link = get_page_link(page_number)

    print("Fetching...", page_link)

    questions = get_question_list(page_link)
    total_questions = len(questions)

    print(total_questions, "total questions found")

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_number, f"{index}/{total_questions}", question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": content["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "html_container": content["html_container"],
            "dar_ul_ifta": "jamiamuhammad.com"
        })


    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)


print("END")
