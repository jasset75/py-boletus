import csv
import urllib.request
from datetime import datetime
from pathlib import Path

URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQALTRaLDFfhXOAQmeONPqmFKm9yOiQ4W97rhWgR41BZ7czFsjK5YktD6fnETKHGB9YUnyQ4XBSbhZx/pub?gid=0&single=true&output=csv'
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / 'data' / 'ES-bonoloto.csv'

def main():
    print("Downloading new data from Google Sheets...")
    
    hist_rows = []
    latest_date = None
    
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            if not row:
                continue
            hist_rows.append(row)
            if not latest_date:
                # the first normal entry's date
                d_str = row[0]
                latest_date = datetime.strptime(d_str, "%d/%m/%Y")
    
    print(f"Latest date in local DB: {latest_date.strftime('%d/%m/%Y')}")

    # Fetch new data
    req = urllib.request.Request(URL)
    with urllib.request.urlopen(req) as response:
        lines = [l.decode('utf-8') for l in response.readlines()]
    
    reader = csv.reader(lines)
    try:
        new_header = next(reader)
    except StopIteration:
        pass
    
    diff_rows = []
    
    for row in reader:
        if not row or not row[0]:
            continue
        d_str = row[0]
        try:
            row_date = datetime.strptime(d_str, "%d/%m/%Y")
        except ValueError:
            continue
            
        if row_date > latest_date:
            # Reformat appropriately
            # Google CSV uses: FECHA, N1, N2, N3, N4, N5, N6, COMP, R
            # Local mapping: DATE, N1..N6, NC, R
            new_date_str = f"{row_date.day}/{row_date.month:02d}/{row_date.year}"
            formatted_row = [new_date_str]
            # N1-N6
            for i in range(1, 7):
                formatted_row.append(f"{int(row[i]):02d}")
            # NC (COMP in Google Sheet)
            formatted_row.append(f"{int(row[7]):02d}")
            # R (Reintegro)
            formatted_row.append(str(int(row[8])))
            diff_rows.append(formatted_row)
            
    if not diff_rows:
        print("Local DB is already up to date.")
    else:
        print(f"Found {len(diff_rows)} new records. Appending...")
        
        # Sort descending chronologically
        diff_rows.sort(key=lambda x: datetime.strptime(x[0], "%d/%m/%Y"), reverse=True)
        
        # Combine diff_rows + hist_rows
        all_rows = diff_rows + hist_rows
        
        # Write back to DATA_FILE
        with open(DATA_FILE, 'w', encoding='utf-8', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['DATE', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'NC', 'R'])
            for r in all_rows:
                writer.writerow(r)
        
        print(f"Saved {len(diff_rows)} new records into {DATA_FILE}")

if __name__ == '__main__':
    main()
