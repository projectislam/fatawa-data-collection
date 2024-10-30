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
    url = "https://www.banuri.edu.pk/readfatawa"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, 'html.parser')
    
    pagination = soup.select_one('a.last')  # Ensure this CSS selector matches the actual element on the page

    if pagination is None:
        print("Pagination element not found. Please check the selector or the page structure.")
        return 1  # Default to 1 if pagination is missing, or handle as appropriate

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
    # Send a request to the question page
    response = requests.get(question_url)
    response.raise_for_status()
    
    # Parse the HTML content
    soup = BeautifulSoup(response.content, 'html.parser')

    # Extract "issued_at" from the URL
    issued_at = question_url.split('/')[-1]

    # Extract "title"
    title_tag = soup.select_one(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div:nth-child(2) > h3'
    )
    title = title_tag.get_text(strip=True) if title_tag else "Title not found"

    # Extract "question"
    question_tag = soup.select_one(
        'body > section.inner-section > div > div > div.col-md-9.col-md-push-3.listing-bok > div > div.col-md-12.sawal-jawab > p:nth-child(3)'
    )
    question_text = question_tag.get_text(strip=True) if question_tag else "Question not found"

    # Extract "answer"
    answer_html = ""
    answer_start = soup.find('h4', class_='question_heading', string='جواب')
    if answer_start:
        for sibling in answer_start.find_next_siblings():
            if sibling.name == "hr" and 'big-hr' in sibling.get("class", []):
                break
            answer_html += str(sibling)
    
    # Extract "fatwa_number"
    fatwa_number_tag = soup.select_one('#fatwa_number')
    fatwa_number = fatwa_number_tag.get_text(strip=True) if fatwa_number_tag else "Fatwa number not found"

    # Set "dar_ul_ifta" to "banuri"
    dar_ul_ifta = "banuri"

    # Extract "kitab", "bab", and "fasal"
    kitab, bab, fasal = None, None, None
    tags = soup.find_all('div', class_='tag')
    for tag in tags:
        link = tag.find('a')
        if link:
            href = link.get("href", "")
            if "/questions/kitab" in href:
                kitab = (link.get_text(strip=True), href.split("/")[-1])
            elif "/questions/bab" in href:
                bab = (link.get_text(strip=True), href.split("/")[-1])
            elif "/questions/fasal" in href:
                fasal = (link.get_text(strip=True), href.split("/")[-1])

    # Compile question details
    return {
        "issued_at": issued_at,
        "title": title,
        "question": question_text,
        "answer": answer_html,
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
