import json
# pip install python-docx if you want to work directly with .docx
from docx import Document

# Load your JSON data
with open('your_data.json', 'r') as f:
    data = json.load(f)

# Load your Word document
doc = Document('your_book.docx') # Or process a text file

# Dictionary to store therapy text (you'll need to populate this based on your book's structure)
therapy_data = {}
# Example: Assuming headings in the Word doc match the 'name' in JSON
for paragraph in doc.paragraphs:
    for item in data:
        if item["name"].strip() in paragraph.text: # Simple matching - needs refinement
            # The following paragraph might contain the therapy
            if paragraph.next_paragraph:
                therapy_data[item["name"].strip()] = paragraph.next_paragraph.text.strip()

# Update the JSON data with therapy information
updated_data = []
for item in data:
    therapy = therapy_data.get(item["name"].strip(), "Therapy information not found.")
    updated_data.append({**item, "therapy": therapy})

# Write the updated JSON to a new file
with open('updated_data.json', 'w') as f:
    json.dump(updated_data, f, indent=2)

print("Therapy text added to JSON (potentially needs manual review).")
