from datetime import datetime
import pandas as pd
import numpy as np
from tqdm import tqdm

stats = {}


def draw_to_str(draw, sep='_'):
    nums = np.asarray(draw).tolist()
    return sep.join(map(str,nums))

def check_draw(df_historical, draw, sort=True):
    df = df_historical.copy()

    for i, row in tqdm(df.iterrows(), total=df.shape[0], desc='historical'):
        success = 0
        for key, value in draw.items():
            if value in (row.N1, row.N2, row.N3, row.N4, row.N5, row.N6):
                success += 1
            elif value == row.NC:
                df.at[i, 'comp'] = True
        df.at[i, 'success'] = success
        df.at[i, 'draw'] = draw_to_str(draw)

    df = df[df['success'] > 2]
    df.sort_values(by=['success', 'comp'], ascending=False, inplace=True)

    return df

if __name__ == '__main__':
    f_test = r'/home/apollo/work/py-boletus/test/oh_fortuna.csv'

    df_test = pd.read_csv(f_test, names=['N1', 'N2', 'N3', 'N4', 'N5', 'N6'])

    f_historical = r'/home/apollo/work/py-boletus/data/ES-bonoloto.csv'
    df_historical = pd.read_csv(f_historical, parse_dates=['FECHA'])

    f_out = '/home/apollo/work/py-boletus/out/{0}_{1}_fortuna_{2}.csv'
    df_total = pd.DataFrame()

    for i, draw in tqdm(df_test.iterrows(), total=df_test.shape[0], desc='draws'):
        df_parcial = check_draw(df_historical, draw, sort=False)

        if df_total.empty:
            df_total = df_parcial.copy()
        else:
            df_total = df_total.append(df_parcial, sort=False)

    df_total.sort_values(by=['success', 'comp', 'FECHA'], ascending=False, inplace=True)
    max_num_success = df_total['success'].max()
    df_total.to_csv(f_out.format(max_num_success, 'boletus', 'M'))
