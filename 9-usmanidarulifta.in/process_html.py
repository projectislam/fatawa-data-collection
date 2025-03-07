import os
import csv
import requests
from bs4 import BeautifulSoup
import glob
import pandas as pd
import re
import time

pd.set_option("display.max_colwidth", None)

input_dir = "./data"
output_dir = "./process_data"

os.makedirs(output_dir, exist_ok=True)

csv_files = glob.glob(os.path.join(input_dir, "*.csv"))

for file in csv_files:
    print(f"Processing file {file}")
    df = pd.read_csv(file)

    if df["question_html"].notna().any() or df["answer_html"].notna().any():
        filename = os.path.basename(file)
        df.to_csv(os.path.join(output_dir, filename), index=False)
        continue
    
    html_container = str(df["html_container"])
    soup = BeautifulSoup(html_container, "html.parser")

    content_container = soup.select_one("div.post-body.entry-content > div")

    paras = content_container.find_next_siblings()

    if len(paras) < 3:
        content_container = soup.select_one("div.post-body.entry-content > p")

    paras = content_container.find_next_siblings()

    if len(paras) < 3:
        print("Unable to process content")
        exit(1)

    question_html = ""
    answer_html = ""

    answer_start = False

    for para in paras:
        text = para.get_text().strip()

        if "-------------------" in text:
            answer_start = True
            parts = re.split(r'-{7,}', str(para))
            question_html += parts[0]
            answer_html += parts[1]
            continue

        if answer_start:
            answer_html += str(para)
        else:
            question_html += str(para)

        

    df["question_html"] = question_html
    df["answer_html"] = answer_html

    # Extract filename from path
    filename = os.path.basename(file)

    # Save processed CSV with the same name in output directory
    df.to_csv(os.path.join(output_dir, filename), index=False)

print("Processing complete!")