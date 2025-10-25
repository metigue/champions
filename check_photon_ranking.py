import requests
import csv
import io

# Debug script to check if Photon is in the Ranking sheet and what name it has

illuminati_ranking_url = "https://docs.google.com/spreadsheets/d/10OeQixQCrMKuw-pa3-LDUOQO70WGAFYROPu825Kr-eo/export?format=csv&gid=323504536"

print("Checking if Photon exists in Ranking sheet...")
rank_response = requests.get(illuminati_ranking_url)
rank_response.raise_for_status()
rank_csv = list(csv.reader(io.StringIO(rank_response.text)))

print(f"Ranking sheet has {len(rank_csv)} rows")

# Look for Photon specifically in Ranking sheet
for row_idx in range(len(rank_csv)):
    for col_idx in range(len(rank_csv[row_idx])):
        cell_value = rank_csv[row_idx][col_idx]
        if "photon" in cell_value.lower():
            print(f"Found Photon at Row {row_idx}, Col {col_idx}: '{cell_value}'")
            # Show row and column context
            print(f"  Row header (Col 0): '{rank_csv[row_idx][0] if len(rank_csv[row_idx]) > 0 else 'N/A'}'")
            if col_idx < len(rank_csv[0]) if rank_csv else []:
                print(f"  Column header: '{rank_csv[0][col_idx] if rank_csv and len(rank_csv) > 0 and len(rank_csv[0]) > col_idx else 'N/A'}'")
            print(f"  Full row: {rank_csv[row_idx]}")
            
            # Try to parse the name like the build script does
            name_part = ""
            i = 0
            while i < len(cell_value):
                char = cell_value[i]
                # Check if character is a-z, A-Z, 0-9, hyphen, space, or parentheses
                char_code = ord(char)
                if (65 <= char_code <= 90) or (97 <= char_code <= 122) or (48 <= char_code <= 57) or char in ' -()':
                    name_part += char
                    i += 1
                else:
                    # Found first non-allowed character (likely emoji start)
                    break
            
            clean_name = name_part.strip()
            print(f"  Parsed name: '{clean_name}'")
            print(f"  Will look for BG data with key: '{clean_name.lower()}'")