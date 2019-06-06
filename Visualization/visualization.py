import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
"""
inputs: voltage,temperature,chip type
x-axis:library name
y-axis:yield
"""

def std_cell_yield():
       df = pd.read_csv('sample.csv')
       temp_list = ['25', '125', '150', 'M40']
       temp = temp_list[0]
       dftemp = df.loc[df['Chip Temp'] == temp]


       dflibf = dftemp.drop_duplicates(['VDD (V)'])
       dflib = dflibf['VDD (V)']
       # transform into list
       voltage_list = dflib.values.tolist()

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

"""
inputs: temperature,library name,chip type
x-axis:vdd
y-axis:probability of pass
"""
def calc_prob(df,voltage_list):

       df_shamoo = df.loc[df['Shmoo Value'].isnull() == False]
       shamoo_value = df_shamoo['Shmoo Value']
       # transform into list
       shamoo_value_list = shamoo_value.values.tolist()

       # percentage = No. of (shamoo value < each vdd value) / total number of shamoo value
       prob_list = []
       count = 0
       for vol in voltage_list:
              for value in shamoo_value_list:
                     if (value < vol):
                            count += 1
              prob_list.append(100 * count / len(shamoo_value_list))
              count = 0
       return prob_list

def visualize(df,color):
       dflibf = df.drop_duplicates(['VDD (Range)'])
       dflib = dflibf['VDD (Range)']
       # transform into list
       voltage_list = dflib.values.tolist()
       prob_list = calc_prob(df,voltage_list)
       plt.plot(voltage_list, prob_list,color)
       return

def sc_vmin_data():
       df = pd.read_csv('vminStd.csv')
       temp_list = ['25', '125', '150', 'M40']

       temp = temp_list[0]
       dftemp = df.loc[df['Chip Temp'] == temp]

       dflibf = dftemp.drop_duplicates(['Test Item'])
       dflib = dflibf['Test Item']
       # transform into list
       library_names_list = dflib.values.tolist()
       library_name = library_names_list[0]

       dftemp_lib = dftemp.loc[dftemp['Test Item'] == library_name]
       #plotting
       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='VDD(V)', ylabel='probability of pass(%)',
              title=library_name + ' at ' + str(temp) + ' ' + chr(176) + 'C')
       plt.axis([0.4, 1.2, 0, 105])


       df_ff = dftemp_lib.loc[dftemp['Chip Type'] == 'FF']
       visualize(df_ff,'ys-')
       df_tt = dftemp_lib.loc[dftemp['Chip Type'] == 'TT']
       visualize(df_ff, 'bs-')
       df_ss = dftemp_lib.loc[dftemp['Chip Type'] == 'SS']
       visualize(df_ss,'rs-')

       plt.legend(['FF','TT', 'SS'], loc='right')

       plt.show()
       return

"""
inputs:voltage, temperature,ema
x-axis:library names
y-axis:yield

"""
def memory_yield_summary():
       df = pd.read_csv('mem.csv')
       temp_list = ['25', '125', '150', 'M40']
       temp = temp_list[0]
       dftemp = df.loc[df['Chip Temp'] == temp]

       ema_list = ['A0', 'A1', 'A2', 'A3', 'A4', 'A5', 'A6', 'A7']
       ema = ema_list[1]
       df_ema_temp = dftemp.loc[df['EMA#1'] == ema]
       df_ema_temp_samev = df_ema_temp.loc[df_ema_temp['VDDPE (Range)'] == df_ema_temp['VDDCE (Range)']]

       dfvol = df_ema_temp_samev.drop_duplicates(['VDDPE (Range)'])
       dfvoll = dfvol['VDDPE (Range)']
       vol_list = dfvoll.values.tolist()
       voltage = vol_list[0]

       df_required = df_ema_temp.loc[df['VDDPE (Range)'] == voltage]
       df_pivot = df_required.pivot_table(index=['Architecture'], columns="Chip Type", values="Value",
                                          aggfunc=lambda x: 100 * (x == '(P)').sum() / (
                                                  (x == '(P)').sum() + (x == '(F)').sum()))

       fig = plt.figure()
       ax = fig.add_subplot(111)

       ax.set(xlabel='Instance name', ylabel='yield(%)',
              title='Memory Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(176) + 'C' + '(EMA = ' + ema + ' )')

       plt.axis([0, df_pivot.shape[0], 0, 105])
       df_pivot.plot(ax=ax)
       plt.xticks(np.arange(0, df_pivot.shape[0]), df_pivot.index, rotation=45)
       fig.autofmt_xdate()
       plt.show()
