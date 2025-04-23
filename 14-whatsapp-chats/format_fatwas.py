import csv
import re

input_file = "filtered_chat.csv"
output_file = "formatted_fatwas.csv"

# Matches fatwa number like *(478/42)* or *(66/10/41)*
fatwa_number_pattern = re.compile(r'[\*]?\(([\d/]+)\)[\*]?')
# Urdu dash pattern
qa_splitter = re.compile(r'۔{5,}')
# Pattern to find any `*...۔۔۔۔۔۔۔...*`
dashes_in_asterisks = re.compile(r'\*[^*]*۔{5,}[^*]*\*')

id = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = ['id', 'date', 'time', 'sender', 'fatwa_number', 'question', 'answer', 'message']
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    for row in reader:
        message = row['message'].strip()
        fatwa_number = ""
        question = ""
        answer = ""

        # ❌ Skip if dashed line is inside *...*
        if dashes_in_asterisks.search(message):
            answer = message
        else:
            # ✅ Split into question and answer
            split_match = qa_splitter.split(message, maxsplit=1)
            if len(split_match) == 2:
                question = split_match[0].strip()
                answer = split_match[1].strip()
            else:
                answer = message

        # ✅ Extract fatwa number
        fatwa_match = fatwa_number_pattern.search(message)
        if fatwa_match:
            fatwa_number = fatwa_match.group(1)
            message = fatwa_number_pattern.sub('', message).strip()

        id = id + 1

        writer.writerow({
            'id': id,
            'date': row['date'],
            'time': row['time'],
            'sender': row['sender'],
            'fatwa_number': fatwa_number,
            'question': question,
            'answer': answer,
            'message': message
        })

print(f"Formatted fatwas saved to '{output_file}' (excluded messages with dashed line in *...*)")
