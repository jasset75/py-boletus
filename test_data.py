from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = r'/home/apollo/work/py-boletus/test/reducida_test.csv'
    f_historical = r'/home/apollo/work/py-boletus/data/ES-bonoloto.csv'
    f_out = '/home/apollo/work/py-boletus/out/{0}_{1}_results_{2}.csv'

    scrutiny(f_test, f_historical, f_out)
