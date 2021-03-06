import pandas as pd
import numpy as np
from tqdm import tqdm


def draw_to_str(draw, sep='_'):
    """Readable representation of a draw."""
    nums = np.asarray(draw).tolist()
    return sep.join(map(str, nums))


def check_draw(df_historical, draw, sort=True):
    df = df_historical.copy()

    for i, row in tqdm(enumerate(df.values), total=df.shape[0], desc='historical'):
        s_row = set(row[1:7])
        s_draw = set(draw)
        success = len(s_draw.intersection(s_row))

        df.at[i, 'draw'] = draw_to_str(draw)
        df.at[i, 'success'] = success
        df.at[i, 'comp'] = row[7] in s_draw

    return df[df['success'] > 2]


def scrutiny(f_test, f_historical, f_out, fmt='csv', success_filter=3, order_date_only=False):
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
    df_total = pd.DataFrame()
    df_test = pd.read_csv(f_test, names=['N1', 'N2', 'N3', 'N4', 'N5', 'N6'])
    df_historical = pd.read_csv(f_historical, parse_dates=['FECHA'])

    for i, draw in tqdm(enumerate(df_test.values), total=df_test.shape[0], desc='draws'):
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
