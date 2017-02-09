import pandas as pd


stats = {}

def draw_to_str(draw,sep='_'):
  return sep.join([draw['N1'],draw['N2'],draw['N3'],draw['N4'],draw['N5'],draw['N6']])


def check_draw(f_in,draw,f_out=None,experiment='results'):
  df = pd.read_csv(f_in)
  df['draw'] = draw
  df['success'] = 0
  df['comp'] = False

  for i, row in df.iterrows():
    #print(row['N1'])
    success=0
    for key, value in draw.items():
      if value in (row.N1,row.N2,row.N3,row.N4,row.N5,row.N6):
        success=success+1
      elif value == row.NC:
        df.set_value(i,'comp',True)
    df.set_value(i,'success',success)

  df = df[df['success']>2]
  df.sort_values(by=['success','comp'],ascending=False,inplace=True)

  #import pdb;pdb.set_trace()
  max_num_success = df['success'].max()
  if f_out:
    df.to_csv(f_out.format(max_num_success,experiment,draw_to_str(draw)))
  return df
    #print ('N1: {0},N2: {1},N3: {2},N4: {3},N5: {4},N6: {5},C: {6}'.format(row.N1,row.N2,row.N3,row.N4,row.N5,row.N6,row.NC))


if __name__ == '__main__':
  draw_test = dict(N1=8,N2=14,N3=15,N4=24,N5=32,N6=36)
  f_test = r'c:\work\github\py-boletus\test\reducida_test.csv'
  
  df_test = pd.read_csv(f_test,names=['N1','N2','N3','N4','N5','N6'])
  
  f_in = r'c:\work\github\py-boletus\data\ES-bonoloto.csv'
  f_out = 'c:\\work\\github\\py-boletus\\out\\{0}_{1}_results_{2}.csv'
  df_total = None
  for i, draw in df_test.iterrows():
    df_parcial = check_draw(f_in,draw)
    if df_total is not None:
      df_total = df_total.append(df_parcial)
    else:
      df_total = df_parcial.copy()
  max_num_success = df_total['success'].max()
  df_total.to_csv(f_out.format(max_num_success,'boletus','M'))
