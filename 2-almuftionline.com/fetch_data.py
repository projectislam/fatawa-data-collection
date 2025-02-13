import requests
import os
import csv
from bs4 import BeautifulSoup

base_url = "https://almuftionline.com/blog"
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

def convert_year(year_str):
    if year_str.startswith("00"):
        return "20" + year_str[2:]
    return year_str 

def get_question_list(page_link):
    response = requests.get(page_link)
    soup = BeautifulSoup(response.text, "html.parser")

    cards = soup.select("div.pagelayer-posts-container div.pagelayer-wposts-col")

    questions = []

    for card in cards:
        link_ele = card.select_one(".pagelayer-wposts-content > a")

        link = link_ele.get("href")
        title = link_ele.get_text().strip()

        parts = link.rstrip('/').rsplit('/', 4)

        year = convert_year(parts[1])
        month = parts[2]
        day = parts[3]
        formatted_date = f"{year}-{month}-{day}"

        fatwa_number = parts[4]

        questions.append({
            "title": title,
            "link": link,
            "date": formatted_date,
            "fatwa_number": fatwa_number
        })

    return questions


def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_container = soup.select_one("div.pagelayer-content div.pagelayer-row-holder > div.pagelayer-col > div.pagelayer-col-holder")

    category_lvl_1_ele = soup.select_one("div.entry-content.pagelayer-post-excerpt figure.wp-block-table > table tr:nth-child(1) > td:nth-child(2)")
    category_lvl_2_ele = soup.select_one("div.entry-content.pagelayer-post-excerpt figure.wp-block-table > table tr:nth-child(1) > td:nth-child(3)")

    category_lvl_1 = ""
    category_lvl_2 = ""

    if category_lvl_1_ele:
        category_lvl_1 = category_lvl_1_ele.get_text().strip()
    else:
        category_ele = soup.select_one(".pagelayer-post-info-label.pagelayer-terms > a")
        if category_ele:
            category_lvl_1 = category_ele.get_text().strip()

    if category_lvl_2_ele:
        category_lvl_2 = category_lvl_2_ele.get_text().strip()

    content_ele = soup.select_one("div.entry-content.pagelayer-post-excerpt > div > .has-text-align-center")

    question_html = ""
    answer_html = ""

    if content_ele:
        paras = content_ele.find_next_siblings()

        answer_start = False

        for para in paras:
            if "has-text-align-center" in para.get("class", []):
                answer_start = True

            if answer_start:
                answer_html += str(para)
            else:
                question_html += str(para)
    else:
        article_content_ele = soup.select_one(".entry-content.pagelayer-post-excerpt div.pagelayer-col-holder")
        answer_html = str(article_content_ele)

    if not answer_html:
        answer_html = question_html
        question_html = ""

    if not answer_html:
        raise ValueError("Answer content not found")

    return {
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "question_html": question_html,
        "answer_html": answer_html,
        "html_container": str(html_container)
    }




total_pages = 1119
start_page = 112

for page_number in range(start_page, total_pages + 1):
    page_link = f"{base_url}/page/{page_number}"

    print("Getting question from page", page_link)

    questions = get_question_list(page_link)

    print(len(questions), "Total question found on page number", page_number)

    if not questions:
        continue

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_number, index, question["link"])

        content = get_question_detail(question)
        
        data_rows.append({
            "issued_at": question["date"],
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "fatwa_number": question["fatwa_number"],
            "dar_ul_ifta": "jameya-tur-rasheed",
            "category_lvl_1": content["category_lvl_1"],
            "category_lvl_2": content["category_lvl_2"],
            "html_container": content["html_container"]
        })

    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)

print("END")