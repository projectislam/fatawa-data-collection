import csv
import re

# File paths
input_file = "chat.txt"
output_file = "chat.csv"

# Regex pattern to detect new message lines
message_pattern = re.compile(r'^(\d{1,2}/\d{1,2}/\d{2}), (\d{1,2}:\d{2}\s[APMapm]{2}) - (.*)$')

id = 0

with open(input_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', newline='', encoding='utf-8') as outfile:
    writer = csv.writer(outfile)
    writer.writerow(['id', 'date', 'time', 'sender', 'message'])

    date, time, sender, message = None, None, None, ""

    for line in infile:
        line = line.strip()
        match = message_pattern.match(line)

        if match:
            # Write the previous message if it had a sender
            if date is not None and sender:
                id = id + 1
                writer.writerow([id, date, time, sender, message.strip()])

            date, time, content = match.groups()

            if ': ' in content:
                sender, message = content.split(': ', 1)
            else:
                sender, message = None, ""  # Skip system messages

        else:
            message += '\n' + line

    # Final message
    if date is not None and sender:
        id = id + 1
        writer.writerow([id, date, time, sender, message.strip()])

print(f"Filtered chat exported to {output_file}")
