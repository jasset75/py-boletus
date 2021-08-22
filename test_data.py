from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = r'./test/test_data.csv'
    f_historical = r'./data/test_data_historical.csv'
    f_out = './out/{0}_{1}_test_data_{2}.csv'

    df = scrutiny(f_test, f_historical, f_out=f_out, fmt='csv', success_filter=3, order_date_only=True, verbose=True)
    print(df)
