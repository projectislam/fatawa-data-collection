import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
import time
import json
import csv
import os

options = Options()
options.page_load_strategy = 'eager'  # Load only the DOM; avoid waiting for full page load
# options.add_argument("--headless")
options.add_argument("--disable-gpu")
options.add_argument("--no-sandbox")

driver = uc.Chrome(options=options)

# driver.set_page_load_timeout(10)  # Timeout for loading each page

# Ensure the data directory exists
os.makedirs("./data", exist_ok=True)

def get_start_page(link):
    # if link == "https://darulifta-deoband.com/home/qa_ur/islamic-beliefs/1":
    #     return 78
    
    return 1

def get_total_pages(link):
    print("Scrapping Link", link)

    driver.get(link)

    try:
        last_page_link = driver.find_element(By.CSS_SELECTOR, "#midle_content > div > div:nth-child(2) > nav > ul > li:last-child > a")
        total_pages = int(last_page_link.get_attribute("href").split("=")[-1])
    except Exception as e:
        print("Could not find total pages:", e)
        return
    
    print("Finding total pages", total_pages)

    return total_pages

def scrape_topic(topic, sequence_number):
    try:
        link = topic["link"]

        total_pages = get_total_pages(link)

        start_page = get_start_page(link)

        for page_num in range(start_page, total_pages + 1):
            print("Fetching page number", page_num)

            sequence_number = sequence_number + 1

            page_link = f"{link}?page={page_num}"

            print(page_link)

            driver.get(page_link)

            questions = driver.find_elements(By.CSS_SELECTOR, "#recent_fatwas > ul > li")

            print(len(questions), "questions found on page number", page_num)

            question_links = []

            for question in questions:
                try:
                    question_link = question.find_element(By.TAG_NAME, "a").get_attribute("href")
                    question_links.append(question_link)
                except Exception as e:
                    print("Error extracting href from question:", e)
                    continue

            print(len(question_links), "question href found")

            # Extract and save each question's details
            for question_link in question_links:
                try:
                    print("Fetching question", question_link)
                    
                    driver.get(question_link)

                    # Extract details on the question page

                    fatwa_number = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > div > p.quesid > span").text.split(":")[-1].strip()
                    issued_at = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > p.fatwa_answer > span.answer_date_urdu").get_attribute("innerHTML").split(":")[0].strip()
                    title = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > h2:nth-child(2)").text.replace("عنوان:", "").strip()
                    question_text = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > h2:nth-child(3)").text.replace("سوال:", "").strip()
                    
                    answer = ""
                    li_element = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li")
                    fatwa_answer_element = li_element.find_element(By.CSS_SELECTOR, ".fatwa_answer")
                    siblings_after_fatwa = fatwa_answer_element.find_elements(By.XPATH, "following-sibling::*")

                    for sibling in siblings_after_fatwa:
                        answer += sibling.get_attribute("outerHTML")

                    # Prepare data row

                    data_row = {
                        "issued_at": issued_at,
                        "link": question_link,
                        "title": title,
                        "question": question_text,
                        "answer": answer,
                        "fatwa_number": fatwa_number,
                        "dar_ul_ifta": "deoband",
                        "category_level_1": topic["kitab"],
                        "category_level_2": topic["bab"].split("(")[0].strip()
                    }

                    # Save data to CSV

                    csv_filename = f"./data/{sequence_number}-{link.split('/')[-2]}-{page_num}.csv"
                    with open(csv_filename, "a", encoding="utf-8-sig", newline="") as csvfile:
                        writer = csv.DictWriter(csvfile, fieldnames=data_row.keys())
                        if csvfile.tell() == 0:
                            writer.writeheader()  # Write header if file is empty
                        writer.writerow(data_row)

                    print(f"Saved data for fatwa_number {fatwa_number}")
                except Exception as e:
                    print("Error scraping question:", e)

    except Exception as e:
        print(f"Error occurred: {e}")
        driver.quit()

with open("./topics.json", "r", encoding="utf-8") as file:
    topics = json.load(file)

driver.get("https://darulifta-deoband.com/home/qa_ur/islamic-beliefs/1")

print("Manually Resolve captcha on browser")
time.sleep(15)

print("Scrap Starting....")

sequence_number = 86

for topic in topics[3:4]:
    print("Scraping...", topic["link"])
    
    scrape_topic(topic, sequence_number)

    print("Scraping complete...", topic["link"])

print("->> END")

# Close browser
driver.quit()