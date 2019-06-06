import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import re
"""
inputs: voltage,temperature,chip type
x-axis:library name
y-axis:yield
"""
def std_cell_yield():
       df = pd.read_csv('sample.csv')
       temp_list = [25, 125, 150, 'M40']
       temp = temp_list[0]
       dftemp = df.loc[df['Chip Temp'] == temp]


       dflibf = dftemp.drop_duplicates(['VDD (V)'])
       dflib = dflibf['VDD (V)']
       # transform into list
       voltage_list = dflib.values.tolist()
       print(voltage_list)
       voltage = voltage_list[0]
       dftemp_volt = dftemp.loc[df['VDD (V)'] == voltage]

       df_pivot = dftemp_volt.pivot_table(index=['Test Item'], columns="Chip Type", values="Result",
                                         aggfunc=lambda x: 100 * (x == '(P)').sum() / (
                                                        (x == '(P)').sum() + (x == '(F)').sum()))
       fig = plt.figure()
       ax = fig.add_subplot(111)

       ax.set(xlabel='library name', ylabel='yield(%)',
              title='Stdcell Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(176) + 'C')

       plt.axis([0, df_pivot.shape[0], 0, 105])
       df_pivot.plot(ax=ax)
       plt.xticks(np.arange(0, df_pivot.shape[0]), df_pivot.index,rotation = 45)
       fig.autofmt_xdate()
       plt.show()
       return
