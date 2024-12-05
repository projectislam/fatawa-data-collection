import requests
import os
import csv
from bs4 import BeautifulSoup

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

    return page * 150

def get_question_list(page_link):
    print("Getting question list from...", page_link)
    response = requests.get(page_link)

    soup = BeautifulSoup(response.text, "html.parser")

    rows = soup.select("body > div > div.container-fluid.contain > div > div > div.card-body > table > tr")

    questions = []

    for row in rows:
        date_ele = row.select_one("td:nth-child(1)")
        fatwa_num_ele = row.select_one("td:nth-child(2)")
        title_ele = row.select_one("td:nth-child(3) > span")
        link_ele = row.find("a", class_="link-danger")

        if not link_ele:
            continue

        date = date_ele.get_text()
        fatwa_num = fatwa_num_ele.get_text()
        title = title_ele.get_text().strip()
        link = link_ele.get("href")
        link = link.rsplit("/", 1)[0]
        last_part = link.rstrip("/").split("/")[-1]

        if last_part != fatwa_num:
            link = f"https://onlinefatawa.com/view_fatwa_unicode/{fatwa_num}"

        questions.append({
            "date": date,
            "fatwa_num": fatwa_num,
            "title": title,
            "link": link
        })

    return questions


def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_container = soup.select_one("div.container-fluid.contain > div.row > div.col-md-8")

    date_ele = soup.select_one("body > div > div.container-fluid.contain > div > div.col-md-8 > div.card > div > div > div:nth-child(1) > div.txt.robotolight.mobile")
    date = date_ele.get_text()

    if not date or date == "0000-00-00":
        date = question["date"]

    category_ele = soup.select_one("body > div > div.container-fluid.contain > div > div.col-md-8 > div.eight > h6")
    category = category_ele.get_text().strip()
    category_parts = category.split("/")

    category_lvl_1 = category_parts[0]
    category_lvl_2 = category_parts[1]
    category_lvl_3 = category_parts[2]

    question_ele = soup.select_one("body > div > div.container-fluid.contain > div > div.col-md-8 > p:nth-child(5)")
    question_html = str(question_ele)

    answer_ele = soup.select_one("body > div > div.container-fluid.contain > div > div.col-md-8 h5.amiri")
    answer_html = str(answer_ele)

    siblings = answer_ele.find_next_siblings()

    for sibling in siblings:
        if "row" in sibling.get("class", []):
            break

        answer_html += str(sibling)

    return {
        "answer_html": answer_html,
        "question_html": question_html,
        "date": date,
        "category_lvl_1": category_lvl_1,
        "category_lvl_2": category_lvl_2,
        "category_lvl_3": category_lvl_3,
        "html_container": html_container
    }




base_url = "https://onlinefatawa.com/NewFatawa"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

total_fatawa = 13950
fatawa_per_page = 150
total_pages = int(total_fatawa / 150)
start_page = 0 # start from 0

for page_number in range(start_page, total_pages + 1):
    print("Page number", page_number)

    num = get_page_number(page_number)
    page_link = f"{base_url}/{num}"

    questions = get_question_list(page_link)
    total_questions = len(questions)

    print(total_questions, "total questions found on", page_link)

    data_rows = []

    for index, question in enumerate(questions, start=1):
        print(page_number, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question": content["question_html"],
            "answer": content["answer_html"],
            "issued_at": content["date"],
            "fatwa_number": question["fatwa_num"],
            "dar_ul_ifta": "onlinefatawa.com",
            "category_lvl_1": content["category_lvl_1"],
            "category_lvl_2": content["category_lvl_2"],
            "category_lvl_3": content["category_lvl_3"],
            "html_container": content["html_container"]
        })

    filename = f"{data_dir}/{page_number}.csv"
    save_to_csv(filename, data_rows)


print("END")




