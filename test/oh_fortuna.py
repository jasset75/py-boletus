from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm
from lib.scrutiny import check_draw, draw_to_str

if __name__ == '__main__':
    f_test = r'/home/apollo/work/py-boletus/test/oh_fortuna.csv'

    df_test = pd.read_csv(f_test, names=['N1', 'N2', 'N3', 'N4', 'N5', 'N6'])

    f_historical = r'/home/apollo/work/py-boletus/data/ES-bonoloto.csv'
    df_historical = pd.read_csv(f_historical, parse_dates=['FECHA'])

    f_out = '/home/apollo/work/py-boletus/out/{0}_{1}_fortuna_{2}.csv'
    df_total = pd.DataFrame()

    for i, draw in tqdm(enumerate(df_test.values), total=df_test.shape[0], desc='draws'):
        df_parcial = check_draw(df_historical, draw, sort=False)

        if df_total.empty:
            df_total = df_parcial.copy()
        else:
            df_total = df_total.append(df_parcial, sort=False)

    df_total.sort_values(by=['success', 'comp', 'FECHA'], ascending=False, inplace=True)
    max_num_success = df_total['success'].max()
    df_total.to_csv(f_out.format(max_num_success, 'boletus', 'M'))
