from pathlib import Path
import sys

ROOT_DIR = Path(__file__).resolve().parents[1]
if str(ROOT_DIR) not in sys.path:
    sys.path.insert(0, str(ROOT_DIR))

from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = ROOT_DIR / 'test' / 'test_data.csv'
    f_historical = ROOT_DIR / 'data' / 'test_data_historical.csv'
    f_out = str(ROOT_DIR / 'out' / '{0}_{1}_test_data_{2}.csv')

    df = scrutiny(f_test, f_historical, f_out=f_out, fmt='csv', success_filter=3, order_date_only=True, verbose=True)
    print(df)
