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

link = "https://darulifta-deoband.com/home/ur/world-religions/32843"

driver.get(link)

time.sleep(15)

# Find the <li> element containing the .fatwa_answer class
li_element = driver.find_element(By.CSS_SELECTOR, "#recent_fatwas > ul > li")

# Find the <p class="fatwa_answer"> element inside <li>
fatwa_answer_element = li_element.find_element(By.CSS_SELECTOR, ".fatwa_answer")

# Get the next sibling elements after the .fatwa_answer element
# This can be done using the `find_elements` method to find all subsequent elements.
# We want everything after the fatwa_answer tag, so we will select the siblings.

# Use XPath to select all siblings after fatwa_answer element
siblings_after_fatwa = fatwa_answer_element.find_elements(By.XPATH, "following-sibling::*")

# Now let's print the HTML content of all the following siblings
for sibling in siblings_after_fatwa:
    print(sibling.get_attribute("outerHTML"))

# Close browser
driver.quit()