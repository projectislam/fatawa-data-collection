import csv

input_file = "chat.csv"
output_file = "filtered_chat.csv"
filter_phrase = "بندہ عاطف محمود عفی"

total = 0
matched = 0
id = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    writer = csv.DictWriter(outfile, fieldnames=reader.fieldnames)
    
    writer.writeheader()

    for row in reader:
        total += 1
        if filter_phrase in row['message']:
            id = id + 1
            row['id'] = id
            writer.writerow(row)
            matched += 1

# Summary output
print(f"✅ Total messages       : {total}")
print(f"✅ Matched messages     : {matched}")
print(f"✅ Unmatched messages   : {total - matched}")
print(f"📄 Filtered messages saved to '{output_file}'")
