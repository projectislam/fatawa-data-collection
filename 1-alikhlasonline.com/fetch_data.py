import requests
import os
import csv
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs

base_url = "https://alikhlasonline.com"
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

    html_ele = soup.select_one("div.col-md-8.minHeight > div:nth-child(1)")
    question_ele = soup.select_one("#printthis > div:nth-child(2)")
    answer_ele = soup.select_one("#printthis > div:nth-child(3)")
    date_ele = soup.select_one("div.text-left.hidden-print > table tr td:nth-child(4)")

    question_html = str(question_ele)
    question_html = question_html.replace('<b class="text-danger">سوال: </b>', "")

    answer_html = str(answer_ele)
    answer_html = answer_html.replace('<b class="text-danger">جواب: </b>', "")

    date = date_ele.get_text().strip()

    html_container = str(html_ele)

    parsed_url = urlparse(link)
    query_params = parse_qs(parsed_url.query)
    fatwa_number = query_params.get("id", [None])[0]

    return {
        "question_html": question_html,
        "answer_html": answer_html,
        "fatwa_number": fatwa_number,
        "date": date,
        "html_container": html_container
    }


total_pages = 224
start_page = 1

for page_number in range(start_page, total_pages + 1):
    page_link = f"{base_url}/allquestions.aspx?lang=1&page={page_number}"

    print("Page number", page_number, page_link)
    
    questions = get_question_list(page_link)

    print(len(questions), "total questions found on page number", page_number)

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_number, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "fatwa_number": content["fatwa_number"],
            "issued_at": content["date"],
            "html_container": content["html_container"],
            "dar_ul_ifta": "alikhlasonline",
        })


    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)

print("END")