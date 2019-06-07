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
       visualize(df_tt, 'bs-')
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

       #separate mem instances for clearness
       start_index = 0
       tail_index = 25
       while(tail_index < df_pivot.shape[0]):
              fig = plt.figure()
              ax = fig.add_subplot(111)

              ax.set(xlabel='Instance name', ylabel='yield(%)',
                     title='Memory Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(
                            176) + 'C' + '(EMA = ' + ema + ' )')

              df_pivot_tmp = df_pivot[start_index:tail_index]
              plt.axis([0,25, 0, 105])
              df_pivot_tmp.plot(ax=ax)
              plt.xticks(np.arange(0, 25), df_pivot_tmp.index, rotation=45)
              fig.autofmt_xdate()

              start_index = tail_index
              tail_index += 25

       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='Instance name', ylabel='yield(%)',
              title='Memory Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(
                     176) + 'C' + '(EMA = ' + ema + ' )')

       df_pivot_tmp = df_pivot[start_index:df_pivot.shape[0]]
       tmp_num = df_pivot.shape[0] - start_index
       plt.axis([0, tmp_num, 0, 105])
       df_pivot_tmp.plot(ax=ax)
       plt.xticks(np.arange(0, tmp_num), df_pivot_tmp.index, rotation=45)
       fig.autofmt_xdate()

       plt.show()

"""
inputs: memory instance,temperature
x-axis:vdd
y-axis:probability of pass
plots for different emas
"""
def mem_vmin_data_ss_one():
       #finding required data frame based on inputs
       df = pd.read_csv('vminCkb.csv')
       df_ss = df.loc[df['Chip Type'] == 'SS']
       temp_list = ['25', '125', '150', 'M40']
       temp = temp_list[0]
       dftemp = df_ss.loc[df['Chip Temp'] == temp]
       dfmem = dftemp.drop_duplicates(['Architecture'])
       mem_list = dfmem['Architecture'].values.tolist()
       mem_instance = mem_list[0]
       dftemp_mem = dftemp.loc[dftemp['Architecture'] == mem_instance]

       #finding vdd list for x-axis and calc prob of pass
       tmp_df = pd.read_csv('mem.csv')
       tmp_df_ss = tmp_df.loc[tmp_df['Chip Type'] == 'SS']
       tmp_df_ss_samev = tmp_df_ss.loc[tmp_df_ss['VDDPE (Range)'] == tmp_df_ss['VDDCE (Range)']]
       dfvol = tmp_df_ss_samev.drop_duplicates(['VDDPE (Range)'])
       vol_list = sorted(dfvol['VDDPE (Range)'].values.tolist())

       # finding emas
       dfemas = dftemp_mem.drop_duplicates(['EMA#1'])
       dfema = dfemas['EMA#1']
       ema_list = dfema.values.tolist()

       #plotting
       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
              title='Probability plot for <' + mem_instance + '> at Temp = ' + str(temp) + chr(176) + 'C')
       plt.axis([0.4, 1.2, 0, 105])

       for ema in ema_list:
              df_required = dftemp_mem.loc[dftemp_mem['EMA#1'] == ema]
              prob_list = calc_prob(df_required,vol_list)
              plt.plot(vol_list, prob_list, 's-')

       plt.legend(ema_list, loc='right')
       plt.show()

       return

'''
inputs: ema = default(A2),temperature
x-axis:vdd
y-axis:probability of pass
plots for different memory instance
'''
#too many mem instaces -> hard to visualize all
def mem_vmin_data_ss_two():
       #finding required data frame based on inputs
       df = pd.read_csv('vminCkb.csv')
       df_ss = df.loc[df['Chip Type'] == 'SS']
       temp_list = ['25', '125', '150', 'M40']
       temp = temp_list[0]
       dftemp = df_ss.loc[df['Chip Temp'] == temp]
       default_ema = 'A2'
       dftemp_ema = dftemp.loc[dftemp['EMA#1'] == default_ema]

       #finding vdd list for x-axis and calc prob of pass
       tmp_df = pd.read_csv('mem.csv')
       tmp_df_ss = tmp_df.loc[tmp_df['Chip Type'] == 'SS']
       tmp_df_ss_samev = tmp_df_ss.loc[tmp_df_ss['VDDPE (Range)'] == tmp_df_ss['VDDCE (Range)']]
       dfvol = tmp_df_ss_samev.drop_duplicates(['VDDPE (Range)'])
       vol_list = sorted(dfvol['VDDPE (Range)'].values.tolist())

       # vol_list = [0.54, 0.6, 0.63, 0.6375, 0.675, 0.72, 0.81, 0.88, 0.9, 0.96, 1.05, 1.2]


       # finding memory instance
       dfmems = dftemp_ema.drop_duplicates(['Architecture'])
       mem_list = dfmems['Architecture'].values.tolist()

       #plotting memory instance in different graphs(too many mem instances)
       head_index = 0
       tail_index = 25
       while(tail_index < len(mem_list)):
              fig = plt.figure()
              ax = fig.add_subplot(111)
              ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
                     title='Probability plot for all mem_instances at ema = A2, Temp = ' + str(temp) + chr(176) + 'C')
              plt.axis([0.4, 1.2, 0, 105])

              for mem in mem_list[head_index:tail_index]:
                     df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
                     prob_list = calc_prob(df_required, vol_list)
                     plt.plot(vol_list, prob_list, 's-')

              plt.legend(mem_list[head_index:tail_index], loc='right')
              head_index = tail_index
              tail_index += 25

       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
              title='Probability plot for all mem_instances at ema = A2, Temp = ' + str(temp) + chr(176) + 'C')
       plt.axis([0.4, 1.2, 0, 105])

       for mem in mem_list[head_index:len(mem_list)]:
              df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
              prob_list = calc_prob(df_required, vol_list)
              plt.plot(vol_list, prob_list, 's-')

       plt.legend(mem_list[head_index:len(mem_list)], loc='right')

       plt.show()
       return
