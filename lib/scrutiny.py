import pandas as pd
import numpy as np
from tqdm import tqdm
from lib import config
from lib.logger import Log

logger = Log()

# Historical data columns
_DATE_COLUMN = 'DATE'
_N1 = 'N1' 
_N2 = 'N2'
_N3 = 'N3'
_N4 = 'N4'
_N5 = 'N5'
_N6 = 'N6'

# Result columns
_DRAW_COLUMN = 'draw'
_MAX_SUCCESS_COLUMN = 'max_success'
_COMP_COLUMN = 'comp'
_COMP_COLUMN_INDEX = 7

def draw_to_str(draw, sep='-'):
    """Readable representation of a draw."""
    nums = np.asarray(draw).tolist()
    return sep.join(map(str, nums))


def check_draw(df_historical, draw, sort=True):
    """Check a combination from historical draw."""
    df = df_historical.copy()

    for i, row in tqdm(enumerate(df.values), total=df.shape[0], desc='historical'):
        s_row = set(row[1:7])
        s_draw = set(draw)
        success = len(s_draw.intersection(s_row))
        comp_number = row[_COMP_COLUMN_INDEX]

        df.at[i, _DRAW_COLUMN] = draw_to_str(draw)
        df.at[i, _MAX_SUCCESS_COLUMN] = int(success)
        df.at[i, _COMP_COLUMN] = int(comp_number in s_draw)
    
    return df


def scrutiny(f_test, f_historical, f_out, fmt='csv', success_filter=3, order_date_only=False, verbose=True):
    """Test all numbers in ``f_test`` file with the historical draws and return the matches for each one.

    :param f_test: file with the numbers to test, each row for each independent experiment
    :type f_test: str
    :param f_historical: file with historical draws
    :type f_historical: str
    :param f_out: file to save the output with results
    :type f_out: str
    :param fmt: output file format
    :type fmt: str ('csv' for CSV format)
    :param success_filter: number of matches from witch the success is returned
    :type success_filter: int
    :param order_date_only: if True only sorted by
    :type order_date_only: bool
    :return: data frame with all success
    :rtype: pandas.DataFrame
    """
    config.verbose(verbose)

    # Data frame to store the results
    df_total = pd.DataFrame()

    # Read the test file with the sample to be tested with the historical combinations
    df_test = pd.read_csv(f_test, names=[
        'N1',
        'N2',
        'N3',
        'N4',
        'N5',
        'N6'
    ]).copy()

    # Read the file with the historical combinations
    df_historical = pd.read_csv(f_historical, parse_dates=[_DATE_COLUMN]).copy()

    combinations_number = df_test.shape[0]
    logger.verbose(f'test size: {combinations_number}')
        
    # Each combination is comparing with each draw in order to know the prize cathegory (if any)
    for _, draw in tqdm(enumerate(df_test.values), total=combinations_number, desc='draws'):
        # Evaluating each draw
        df_parcial = check_draw(df_historical, draw, sort=False)
        df_parcial = df_parcial[df_parcial[_MAX_SUCCESS_COLUMN] > 2]

        if df_total.empty:
            df_total = df_parcial.copy()
        else:
            df_total = df_total.append(df_parcial, sort=False)

    # Order
    if order_date_only:
        df_total.sort_values(by=[_DATE_COLUMN], ascending=False, inplace=True)
    else:
        df_total.sort_values(by=[_MAX_SUCCESS_COLUMN, _COMP_COLUMN, _DATE_COLUMN], ascending=False, inplace=True)

    # Final config
    df_total.fillna(0, inplace=True)
    max_num_success = df_total[_MAX_SUCCESS_COLUMN].max()

    # Save to file
    df_total.to_csv(f_out.format(max_num_success, 'boletus', 'M'))

    return df_total
