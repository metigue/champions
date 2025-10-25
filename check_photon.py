import requests
import csv
import io

# Debug script to check if Photon is in the Battlegrounds sheet

vega_bgs_url = "https://docs.google.com/spreadsheets/d/1KzfdzI_HxK7zk_eTwmdwI5G84k9HSIYPzAMSPgGYjUE/export?format=csv&gid=0"

print("Checking if Photon exists in Battlegrounds sheet...")
bg_response = requests.get(vega_bgs_url)
bg_response.raise_for_status()
bg_csv = list(csv.reader(io.StringIO(bg_response.text)))

print(f"Battlegrounds sheet has {len(bg_csv)} rows")

# Look for Photon specifically in Battlegrounds sheet
for row_idx in range(len(bg_csv)):
    for col_idx in range(len(bg_csv[row_idx])):
        cell_value = bg_csv[row_idx][col_idx]
        if "photon" in cell_value.lower() and "-" in cell_value:
            print(f"Found Photon at Row {row_idx}, Col {col_idx}: '{cell_value}'")
            # Show column header
            if col_idx < len(bg_csv[0]):
                print(f"  Column header: '{bg_csv[0][col_idx]}'")
            print(f"  Full row: {bg_csv[row_idx]}")