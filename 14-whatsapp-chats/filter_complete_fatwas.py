import csv

input_file = "formatted_fatwas.csv"
output_file = "complete_fatwas.csv"

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    reader = csv.DictReader(infile)
    fieldnames = reader.fieldnames
    writer = csv.DictWriter(outfile, fieldnames=fieldnames)
    writer.writeheader()

    kept_count = 0
    total = 0
    id = 0

    for row in reader:
        total += 1
        if row['question'].strip() and row['answer'].strip():
            id = id + 1
            row['id'] = id
            writer.writerow(row)
            kept_count += 1

print(f"✅ Total records processed: {total}")
print(f"✅ Complete fatwas written: {kept_count}")
print(f"📄 Saved to: '{output_file}'")
