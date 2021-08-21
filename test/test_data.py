from lib.scrutiny import scrutiny

if __name__ == '__main__':
    f_test = r'./test/reducida_test.csv'
    f_historical = r'./data/ES-bonoloto.csv'
    f_out = './out/{0}_{1}_results_{2}.csv'

    scrutiny(f_test, f_historical, f_out)
