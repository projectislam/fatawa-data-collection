import requests
from bs4 import BeautifulSoup
import csv
import os

base_url = "https://www.suffahpk.com/category/fatawa-darul-uloom-karachi/"
data_dir = "./data"

bismillah_text = "بسم اللہ الرحمن الرحیم"
jawab = "جواب :"
jawab_text_1 = "الجواب حامدا ومصلیا"
jawab_text_2 = "الجواب"
jawab_text_3 = "الجواب حامداومصلیاً"
jawab_text_4 = "الجواب بعون ملہم الصواب"
jawab_text_5 = "الجواب حامداومصلیا"
jawab_text_6 = "الجواب حامدامصلیا ً"
jawab_text_7 = "الجواب حماداً و مصلیاً"
jawab_text_8 = "الجواب و باللہ التوفیق و ھو المستعان"
jawab_text_9 = "الجواب باسم ملھم الصواب"
jawab_text_10 = "الجواب   حامداومصلیا"
jawab_text_11 = "الجواب حامداًومصلیاً"
jawab_text_12 = "الجواب حامداومصلیاً  "
jawab_text_13 = "الجواب حامداومصلیا "
jawab_text_14 = "الجواب حامداومصلیا"
jawab_text_15 = "الجواب حامدا و مصلیا"
jawab_text_16 = "الجواب حامداومصلیا"
jawab_text_17 = "الجواب حامدا ومصلیا "
jawab_text_18 = "الجواب حامداومصلیا ً"
jawab_text_19 = "الجواب حامداومصلیاً "
jawab_text_20 = "الجواب حامداً و مصلیاً"
jawab_text_21 = " الجواب   حامداومصلیا ً"
jawab_text_22 = "الجواب حامدًا ومصلیاً"
jawab_text_23 = "الجواب و باللہ التوفیق و ھو المستعان"
jawab_text_24 = "الجواب  حامداومصلیاً"
jawab_text_25 = " الجواب حامداومصلیا ً"
jawab_text_26 = " الجواب حامداومصلیا"
jawabs = [jawab_text_1, jawab_text_2, jawab_text_3, jawab_text_4, jawab_text_5,
          jawab_text_6, jawab_text_7, jawab_text_8, jawab_text_9, jawab_text_10, 
          jawab_text_11, jawab_text_12, jawab_text_13, jawab_text_14, jawab_text_15,
          jawab_text_16, jawab_text_17, jawab_text_18, jawab_text_19, jawab_text_20,
          jawab_text_21, jawab_text_22, jawab_text_23, jawab_text_24, jawab_text_25,
          jawab_text_26]

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/93.0.4577.63 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9",
    "Accept-Encoding": "gzip, deflate, br",
    "Connection": "keep-alive"
}

# Create data directory if it doesn't exist
os.makedirs(data_dir, exist_ok=True)

def save_to_csv(filename, data_rows):
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

def get_question_list(page_num):
    page_url = f"{base_url}/page/{page_num}"
    response = requests.get(page_url)
    soup = BeautifulSoup(response.text, 'html.parser')

    articles = soup.select("#main > article")

    questions = []

    for article in articles:
        heading = article.find("h1", class_="entry-title")
        title = heading.get_text()
        link = heading.find("a").get("href")

        date_ele = article.find("time", class_="updated")
        date = date_ele.get_text()

        questions.append({
            "title": title, 
            "link": link, 
            "date": date
        })

    return questions


def get_question_detail(question):
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    html_container = soup.select_one("#post-conten-single")

    paras = soup.select("#post-conten-single > p")

    question_html = ""
    answer_html = ""

    answer_start = False

    for para in paras:
        next_text = ""
        text = para.get_text()

        next_para = para.find_next_sibling()

        if next_para:
            next_text = next_para.get_text()

        if text == bismillah_text and (next_text in jawabs or jawab in next_text):
            answer_start = True

        if text in jawabs or jawab in text:
            answer_start = True

        if answer_start:
            answer_html += str(para)
        else:
            question_html += str(para)

    if not answer_html:
        answer_html = question_html
        question_html = ""

    return {
        "answer_html": answer_html,
        "question_html": question_html,
        "html_container": str(html_container)
    }





total_pages = 34
start_page = 1


for page_num in range(start_page, total_pages + 1):
    print("Page number", page_num)

    questions = get_question_list(page_num)

    print(len(questions), "total questions found on page", page_num)

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(page_num, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "link": question["link"],
            "title": question["title"],
            "question_html": content["question_html"],
            "answer_html": content["answer_html"],
            "issued_at": question["date"],
            "dar_ul_ifta": "suffah-darul-uloom-karachi",
            "html_container": content["html_container"]
        })

    filename = f"{data_dir}/{page_num}.csv"
    save_to_csv(filename, data_rows)

print("End")

