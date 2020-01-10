from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = r'/home/apollo/work/py-boletus/test/oh_fortuna.csv'
    f_historical = r'/home/apollo/work/py-boletus/data/ES-bonoloto.csv'
    f_out = '/home/apollo/work/py-boletus/out/{0}_{1}_fortuna_{2}.csv'

    json = scrutiny(f_test, f_historical, f_out=f_out, fmt='csv', success_filter=3, order_date_only=True)
    print(json)