import os
import csv
import requests
from bs4 import BeautifulSoup

base_url = "https://www.usmanidarulifta.in/"
data_dir = "./data"

os.makedirs(data_dir, exist_ok=True)

def get_topic_list():
    response = requests.get(base_url)
    soup = BeautifulSoup(response.text, "html.parser")

    items = soup.select("#Label1 > div > ul > li")

    topics = []

    for item in items:
        link_ele = item.select_one("a")

        title = link_ele.get_text().strip()
        link = link_ele.get("href")

        topics.append({
            "title": title,
            "link": link
        })

    return topics

def get_topic_questions(soup):
    items = soup.select("#Blog1 > div.blog-posts.hfeed > div.date-outer")

    print(len(items), "total questions found")

    questions = []

    for item in items:
        date_ele = item.select_one("h2.date-header")
        question_link_ele = item.select_one("h3.post-title.entry-title > a")

        date = date_ele.get_text().strip()
        title = question_link_ele.get_text().strip()
        question_link = question_link_ele.get("href")

        content_container = item.select_one("div.post-body.entry-content > div")
        paras = content_container.find_next_siblings()

        question_html = ""
        answer_html = ""

        answer_start = False

        for para in paras:
            text = para.get_text().strip()

            if "-------------------" in text:
                answer_start = True

            if answer_start:
                answer_html += str(para)
            else:
                question_html += str(para)

        questions.append({
            "link": question_link,
            "title": title,
            "date": date,
            "answer_html": answer_html,
            "question_html": question_html,
            "html_container": str(item)
        })

    return questions


def get_topic_pages(topic_index, topic):
    sequence_number = 1
    link = topic["link"]
    
    while True:
        print("Scraping...", link)
        response = requests.get(link)
        soup = BeautifulSoup(response.text, "html.parser")

        questions = get_topic_questions(soup)

        if questions:
            data_rows = []

            for question in questions:
                data_rows.append({
                    "link": question["link"],
                    "title": question["title"],
                    "question_html": question["question_html"],
                    "answer_html": question["answer_html"],
                    "issued_at": question["date"],
                    "html_container": question["html_container"],
                    "dar_ul_ifta": "usmanidarulifta"
                })

            filename = f"{data_dir}/{topic_index}-{sequence_number}.csv"
            with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
                fieldnames = data_rows[0]
                writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
                writer.writeheader()
                for data_row in data_rows:
                        writer.writerow(data_row)

            print("->> Questions saved in", filename)

        older_posts_link_ele = soup.select_one("#blog-pager-older-link > a")

        if not older_posts_link_ele:
            break

        link = older_posts_link_ele.get("href")
        sequence_number = sequence_number + 1


topics = get_topic_list()

total_topics = len(topics)

print(total_topics, "total topics found")

for topic_index, topic in enumerate(topics, 1):
    print(f"{topic_index}/{total_topics}", topic['link'])

    get_topic_pages(topic_index, topic)

print("END")