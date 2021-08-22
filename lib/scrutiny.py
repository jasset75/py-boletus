import pandas as pd
import numpy as np
from tqdm import tqdm
from lib import config
from lib.logger import Log

logger = Log()

def draw_to_str(draw, sep='_'):
    """Readable representation of a draw."""
    nums = np.asarray(draw).tolist()
    return sep.join(map(str, nums))


def check_draw(df_historical, draw, sort=True):
    df = df_historical.copy()

    for i, row in tqdm(enumerate(df.values), total=df.shape[0], desc='historical'):
        import ipdb; ipdb.set_trace()
        s_row = set(row[1:7])
        s_draw = set(draw)
        success = len(s_draw.intersection(s_row))

        df.at[i, 'draw'] = draw_to_str(draw)
        df.at[i, 'success'] = success
        df.at[i, 'comp'] = row[7] in s_draw

    return df[df['success'] > 2]


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
    df_test = pd.read_csv(f_test, names=['N1', 'N2', 'N3', 'N4', 'N5', 'N6']).copy()

    # Read the file with the historical combinations
    df_historical = pd.read_csv(f_historical, parse_dates=['FECHA']).copy()

    combinations_number = df_test.shape[0]
    logger.verbose(f'test size: {combinations_number}')
        
    # Each combination is comparing with each draw in order to know the prize cathegory (if any)
    for _, draw in tqdm(enumerate(df_test.values), total=combinations_number, desc='draws'):
        # Evaluating each draw
        df_parcial = check_draw(df_historical, draw, sort=False)

        if df_total.empty:
            df_total = df_parcial.copy()
        else:
            df_total = df_total.append(df_parcial, sort=False)

    if order_date_only:
        df_total.sort_values(by=['FECHA'], ascending=False, inplace=True)
    else:
        df_total.sort_values(by=['success', 'comp', 'FECHA'], ascending=False, inplace=True)

    max_num_success = df_total['success'].max()
    df_total.to_csv(f_out.format(max_num_success, 'boletus', 'M'))

    return df_total
