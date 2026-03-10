import os
import re

# Folder where your CSV files are stored
folder = "data"

# Set your range
start_from = 16
end_to = 37

# Get all files in folder
files = os.listdir(folder)

# Pattern to match files like "20-1.csv"
pattern = re.compile(r"^(\d+)-(\d+)\.csv$")

# We'll rename files starting from the highest number to avoid conflicts
# Filter files within the range
files_to_rename = []
for file in files:
    match = pattern.match(file)
    if match:
        prefix = int(match.group(1))
        if start_from <= prefix <= end_to:
            files_to_rename.append((prefix, file))

# Sort descending by prefix so we don't overwrite files
files_to_rename.sort(reverse=True)

# Rename files
for prefix, file in files_to_rename:
    new_prefix = prefix + 1
    new_name = f"{new_prefix}-{file.split('-', 1)[1]}"
    old_path = os.path.join(folder, file)
    new_path = os.path.join(folder, new_name)
    print(f"Renaming {file} -> {new_name}")
    os.rename(old_path, new_path)

print("Renaming complete!")