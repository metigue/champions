import requests
import csv
import io

# URLs for the spreadsheets
illuminati_ranking_url = "https://docs.google.com/spreadsheets/d/10OeQixQCrMKuw-pa3-LDUOQO70WGAFYROPu825Kr-eo/export?format=csv&gid=323504536"

print("Fetching Ranking sheet to check row 100...")
response = requests.get(illuminati_ranking_url)
response.raise_for_status()

# Convert the response content to a CSV reader
csv_content = io.StringIO(response.text)
csv_reader = csv.reader(csv_content)

rows = list(csv_reader)

print(f"Ranking sheet has {len(rows)} rows")
print("Row 100 content:")
if len(rows) > 100:
    print(f"Row 100: {rows[100]}")
    for i, cell in enumerate(rows[100]):
        print(f"  Col {i}: '{cell}'")