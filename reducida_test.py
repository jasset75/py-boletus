from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = r'./test/reducida_test.csv'
    f_historical = r'./data/ES-bonoloto.csv'
    f_out = './out/{0}_{1}_reducida_test_{2}.csv'

    df = scrutiny(f_test, f_historical, f_out=f_out, fmt='csv', success_filter=3, order_date_only=True)
    print(df)