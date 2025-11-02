#!/usr/bin/env python3
import requests
import csv
import io

# New spreadsheet URL
new_sheet_url = "https://docs.google.com/spreadsheets/d/1cUr2KoqGtZhx6zIAQw-LkUR9xFwS2xR6HNVKed3qSvQ/export?format=csv&gid=0"

print("Fetching new spreadsheet...")
response = requests.get(new_sheet_url)
response.raise_for_status()

# Parse the CSV
csv_data = list(csv.reader(io.StringIO(response.text)))

print(f"Spreadsheet has {len(csv_data)} rows and {len(csv_data[0]) if csv_data else 0} columns")

print("\nFirst few rows of the spreadsheet:")
for i, row in enumerate(csv_data[:10]):  # Print first 10 rows
    print(f"Row {i}: {row}")

print("\nAnalyzing structure...")
if csv_data:
    headers = csv_data[0]
    print(f"Headers: {headers}")
    
    # Let's look for patterns in the data
    for i, row in enumerate(csv_data[1:20]):  # Check first 19 data rows
        print(f"Sample data row {i+1}: {row}")