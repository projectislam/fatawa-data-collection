import undetected_chromedriver as uc
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
import time
import csv

# Initialize the Chrome driver with options
options = webdriver.ChromeOptions()
# options.add_argument("--headless")  # Run in headless mode to speed up
# options.add_argument("--no-sandbox")
# options.add_argument("--disable-dev-shm-usage")

# Set up Chrome driver with webdriver-manager
# driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
# driver = webdriver.Chrome()

driver = uc.Chrome(version_main=130, options=options)

# Load the topics.json file and read the link
import json
with open("./topics.json", "r", encoding="utf-8") as file:
    topics = json.load(file)

# Function to scrape a topic page
def scrape_topic(topic):
    link = topic["link"]

    print(link)

    driver.get(link)

    print("fetch link")

    # Wait for Cloudflare verification to complete
    time.sleep(10)  # Adjust as needed based on Cloudflare delay

    print("after sleep")

    # Find total pages by accessing the last page links
    try:
        last_page_link = driver.find_element(By.CSS_SELECTOR, "#midle_content > div > div:nth-child(2) > nav > ul > li:last-child > a")
        total_pages = int(last_page_link.get_attribute("href").split("=")[-1])
    except Exception as e:
        print("Could not find total pages:", e)
        return
    
    print(total_pages)

    # Iterate through all pages
    for page_num in range(1, total_pages + 1):
        driver.get(f"{link}?page={page_num}")
        # time.sleep(5)  # Adjust based on page load time

        # Find question list items
        questions = driver.find_elements(By.CSS_SELECTOR, "#recent_fatwas > ul > li")

        print(len(questions))

        # Extract and save each question's details
        for question in questions:
            try:
                question_link = question.find_element(By.TAG_NAME, "a").get_attribute("href")
                
                print("Fetching question data", question_link)
                
                driver.get(question_link)
                # time.sleep(5)  # Wait for question page to load

                print("Fetch complete for question")

                # Extract details on the question page
                fatwa_number = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > div > p.quesid > span").text.split(":")[-1].strip()
                issued_at = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > p.fatwa_answer > span.answer_date_urdu").text.split(" :")[0]
                title = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > h2:nth-child(2) > p").text.strip()
                question_text = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li > h2:nth-child(3) > p").text.replace("سوال :", "").strip()
                answer = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li").get_attribute("innerHTML")

                print("Element extracted")

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

                print(data_row)

                # Save data to CSV
                csv_filename = f"./data/{link.split('/')[-2]}-{page_num}.csv"
                with open(csv_filename, "a", encoding="utf-8-sig", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=data_row.keys())
                    if csvfile.tell() == 0:
                        writer.writeheader()  # Write header if file is empty
                    writer.writerow(data_row)

                print(f"Saved data for fatwa_number {fatwa_number}")
            except Exception as e:
                print("Error scraping question:", e)
                continue

# Scrape each topic
# for topic in topics:
#     scrape_topic(topic)

scrape_topic(topics[0])

# Quit driver
driver.quit()
