import requests
from bs4 import BeautifulSoup
import csv
import os
import time

BASE_URL = "https://www.banuri.edu.pk/new-questions"
QUESTION_URL = "https://www.banuri.edu.pk/readquestion"
DATA_DIR = "./data"

# Create data directory if it doesn't exist
os.makedirs(DATA_DIR, exist_ok=True)

def get_total_pages():
    response = requests.get(BASE_URL)
    soup = BeautifulSoup(response.text, 'html.parser')
    pagination = soup.select_one(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div:nth-child(3) > nav > ul > li:last-child a'
    )
    last_page_url = pagination['href']
    total_pages = int(last_page_url.split('/')[-1])
    
    return 1
    # return total_pages

def get_question_links(page_number):
    url = f"{BASE_URL}/page/{page_number}"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    question_links = soup.select(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div:nth-child(2) > ul > li > a'
    )
    return [link['href'] for link in question_links]

def get_question_details(question_url):
    response = requests.get(question_url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    # Extract required details
    issued_at = question_url.split('/')[-1]
    title = soup.select_one(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div:nth-child(2) > h3'
    ).get_text(strip=True)
    
    # Question text
    question_text = soup.select_one(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div.col-md-12.sawal-jawab > p:nth-child(3)'
    ).get_text(strip=True)

    # Answer text (all paragraphs between answer heading and <hr>)
    answer_elements = soup.select(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div.col-md-12.sawal-jawab > h4.question_heading + p, h4.question_heading + p ~ p'
    )
    answer_text = " ".join([p.get_text(strip=True) for p in answer_elements])

    # Fatwa number
    fatwa_number = soup.select_one("#fatwa_number").get_text(strip=True)

    dar_ul_ifta = "banuri"
    
    # Extract kitab, bab, and fasal tags after the second big-hr
    tags = soup.select("hr.big-hr ~ .tag a")
    kitab, bab, fasal = None, None, None
    for tag in tags:
        href = tag['href']
        if "/questions/kitab" in href:
            kitab = {'title': tag.get_text(strip=True), 'id': href.split('/')[-1]}
        elif "/questions/bab" in href:
            bab = {'title': tag.get_text(strip=True), 'id': href.split('/')[-1]}
        elif "/questions/fasal" in href:
            fasal = {'title': tag.get_text(strip=True), 'id': href.split('/')[-1]}
    
    return {
        "issued_at": issued_at,
        "title": title,
        "question": question_text,
        "answer": answer_text,
        "fatwa_number": fatwa_number,
        "dar_ul_ifta": dar_ul_ifta,
        "kitab": kitab,
        "bab": bab,
        "fasal": fasal
    }

def save_to_csv(page_number, questions_data):
    filename = f"{DATA_DIR}/{page_number}.csv"
    with open(filename, mode='w', newline='', encoding='utf-8') as csv_file:
        fieldnames = [
            "issued_at", "title", "question", "answer", "fatwa_number",
            "dar_ul_ifta", "kitab", "bab", "fasal"
        ]
        writer = csv.DictWriter(csv_file, fieldnames=fieldnames)
        writer.writeheader()
        for question in questions_data:
            writer.writerow(question)

def main():
    total_pages = get_total_pages()
    print(f"Total pages found: {total_pages}")
    
    for page in range(1, total_pages + 1):
        print(f"Scraping page {page} of {total_pages}")
        question_links = get_question_links(page)
        
        questions_data = []
        for question_link in question_links:
            question_url = question_link
            print(f"  Scraping question at {question_url}")
            question_details = get_question_details(question_url)
            questions_data.append(question_details)
            time.sleep(1)  # Pause to avoid rate limiting
        
        save_to_csv(page, questions_data)
        print(f"Saved page {page} data to {DATA_DIR}/{page}.csv")
        time.sleep(2)  # Pause between pages

if __name__ == "__main__":
    main()
