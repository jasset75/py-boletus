import csv
import os
import tempfile
import urllib.request
from datetime import datetime
from io import StringIO
from pathlib import Path

URL = 'https://docs.google.com/spreadsheets/d/e/2PACX-1vQALTRaLDFfhXOAQmeONPqmFKm9yOiQ4W97rhWgR41BZ7czFsjK5YktD6fnETKHGB9YUnyQ4XBSbhZx/pub?gid=0&single=true&output=csv'
ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_FILE = ROOT_DIR / 'data' / 'ES-bonoloto.csv'
LOCAL_HEADER = ['DATE', 'N1', 'N2', 'N3', 'N4', 'N5', 'N6', 'NC', 'R']
REMOTE_HEADER_FIRST_COLUMN = 'FECHA'
DOWNLOAD_TIMEOUT_SECONDS = 30


def _parse_date(value):
    return datetime.strptime(value, '%d/%m/%Y')


def _read_local_rows(data_file):
    with data_file.open('r', encoding='utf-8', newline='') as f:
        reader = csv.reader(f)
        try:
            header = next(reader)
        except StopIteration as exc:
            raise ValueError(f'Local history is empty: {data_file}') from exc

        if header != LOCAL_HEADER:
            raise ValueError(f'Unexpected local header: {header!r}')

        rows = [row for row in reader if row]

    if not rows:
        raise ValueError(f'Local history has no draw rows: {data_file}')

    dated_rows = []
    seen_dates = set()
    for line_number, row in enumerate(rows, start=2):
        if len(row) != len(LOCAL_HEADER):
            raise ValueError(
                f'Invalid local row length at line {line_number}: {len(row)}'
            )
        try:
            row_date = _parse_date(row[0])
        except ValueError as exc:
            raise ValueError(
                f'Invalid local date at line {line_number}: {row[0]!r}'
            ) from exc
        if row_date in seen_dates:
            raise ValueError(f'Duplicate local date at line {line_number}: {row[0]}')
        seen_dates.add(row_date)
        dated_rows.append((row_date, row))

    if any(
        dated_rows[index][0] < dated_rows[index + 1][0]
        for index in range(len(dated_rows) - 1)
    ):
        raise ValueError('Local history must be sorted from newest to oldest')

    return rows, dated_rows[0][0]


def _download_remote_csv(url=URL):
    request = urllib.request.Request(
        url,
        headers={'User-Agent': 'py-boletus/0.1'},
    )
    with urllib.request.urlopen(
        request,
        timeout=DOWNLOAD_TIMEOUT_SECONDS,
    ) as response:
        return response.read().decode('utf-8-sig')


def _normalize_remote_rows(csv_text):
    reader = csv.reader(StringIO(csv_text))
    try:
        header = next(reader)
    except StopIteration as exc:
        raise ValueError('Downloaded history is empty') from exc

    if len(header) < len(LOCAL_HEADER) or header[0].strip() != REMOTE_HEADER_FIRST_COLUMN:
        raise ValueError(f'Unexpected remote header: {header!r}')

    normalized_rows = []
    seen_dates = set()
    for line_number, row in enumerate(reader, start=2):
        if not row or not row[0].strip():
            continue
        if len(row) < len(LOCAL_HEADER):
            raise ValueError(
                f'Invalid remote row length at line {line_number}: {len(row)}'
            )

        try:
            row_date = _parse_date(row[0].strip())
            main_numbers = [int(value) for value in row[1:7]]
            complementary = int(row[7])
            reintegro = int(row[8])
        except ValueError as exc:
            raise ValueError(f'Invalid remote row at line {line_number}: {row!r}') from exc

        if row_date in seen_dates:
            raise ValueError(f'Duplicate remote date at line {line_number}: {row[0]}')
        if len(set(main_numbers)) != 6 or not all(1 <= number <= 49 for number in main_numbers):
            raise ValueError(f'Invalid main numbers at line {line_number}: {main_numbers!r}')
        if not 1 <= complementary <= 49 or complementary in main_numbers:
            raise ValueError(
                f'Invalid complementary number at line {line_number}: {complementary}'
            )
        if not 0 <= reintegro <= 9:
            raise ValueError(f'Invalid reintegro at line {line_number}: {reintegro}')

        seen_dates.add(row_date)
        normalized_rows.append((row_date, [
            f'{row_date.day}/{row_date.month:02d}/{row_date.year}',
            *(f'{number:02d}' for number in main_numbers),
            f'{complementary:02d}',
            str(reintegro),
        ]))

    if not normalized_rows:
        raise ValueError('Downloaded history has no valid draw rows')

    normalized_rows.sort(key=lambda item: item[0], reverse=True)
    return normalized_rows


def _write_rows_atomically(data_file, rows):
    temporary_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode='w',
            encoding='utf-8',
            newline='',
            dir=data_file.parent,
            prefix=f'.{data_file.name}.',
            suffix='.tmp',
            delete=False,
        ) as f:
            temporary_path = Path(f.name)
            writer = csv.writer(f)
            writer.writerow(LOCAL_HEADER)
            writer.writerows(rows)
            f.flush()
            os.fsync(f.fileno())

        os.replace(temporary_path, data_file)
    except Exception:
        if temporary_path is not None:
            temporary_path.unlink(missing_ok=True)
        raise


def update_data(data_file=DATA_FILE, url=URL):
    historical_rows, latest_date = _read_local_rows(data_file)
    print(f"Latest date in local DB: {latest_date.strftime('%d/%m/%Y')}")

    remote_rows = _normalize_remote_rows(_download_remote_csv(url))
    new_rows = [row for row_date, row in remote_rows if row_date > latest_date]

    if not new_rows:
        print('Local DB is already up to date.')
        return 0

    _write_rows_atomically(data_file, new_rows + historical_rows)
    print(f'Saved {len(new_rows)} new records into {data_file}')
    return len(new_rows)


def main():
    print('Downloading new data from Google Sheets...')
    update_data()


if __name__ == '__main__':
    main()
