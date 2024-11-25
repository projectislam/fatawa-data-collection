import requests
import os
import csv
import time
from bs4 import BeautifulSoup

base_url = "https://usmaniapsh.com/new_questions"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

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
    time.sleep(0.5)
    link = question["link"]
    response = requests.get(link)
    soup = BeautifulSoup(response.text, "html.parser")

    questionELe = soup.select_one("div.listing-bok div.col-md-12.sawal-jawab > p:nth-child(3)")
    answerEle = soup.select_one("div.listing-bok div.col-md-12.sawal-jawab > div.sawal_jawab")
    fatwaEle = soup.select_one("#fatwa_number")
    dateELe = soup.select_one("div.listing-bok div.col-md-12.sawal-jawab > div.row > div:nth-child(3)")
    tagsEle = soup.select("div.listing-bok div.col-md-12.sawal-jawab a")

    if not questionELe:
        print(response.text)

    question = questionELe.get_text().strip()
    answer_html = str(answerEle)
    fatwa_number = fatwaEle.get_text().strip()
    date = dateELe.get_text().replace("تاریخ تصدیق :", "").strip()
    kitab = ""
    bab = ""
    fasal = ""

    if not question or not answer_html:
        raise ValueError("Question or answer content not found")

    for tag in tagsEle:
        href = tag.get("href", None)

        if not href:
            continue

        if "/search_individual/kitab/" in href:
            kitab = tag.get_text().strip()
        elif "/search_individual/baab/" in href:
            bab = tag.get_text().strip()
        elif "/search_individual/fasal/" in href:
            fasal = tag.get_text().strip()

    return {
        "question": question,
        "answer_html": answer_html,
        "fatwa_number": fatwa_number,
        "date": date,
        "kitab": kitab,
        "bab": bab,
        "fasal": fasal
    }


total_pages = 148
start_page = 0

for page in range(start_page, total_pages + 1):
    page_number = get_page_number(0)
    page_link = f"{base_url}/{page_number}"

    print("Fetching page...", page_link)

    questions = get_question_list(page_link)

    print(len(questions), "total question found on page number", start_page)

    data_rows = []

    for index, question in enumerate(questions, 1):
        print(start_page, index, question["link"])

        content = get_question_detail(question)

        data_rows.append({
            "issued_at": content["date"],
            "link": question["link"],
            "title": question["title"],
            "question": content["question"],
            "answer": content["answer_html"],
            "fatwa_number": content["fatwa_number"],
            "dar_ul_ifta": "usmaniapsh",
            "kitab": content["kitab"],
            "bab": content["bab"],
            "fasal": content["fasal"]
        })

    filename = f"{data_dir}/{start_page}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = data_rows[0]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for data_row in data_rows:
                writer.writerow(data_row)

    print("->> Questions saved in", filename)

print("END")