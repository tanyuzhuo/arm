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
def calc_prob(df):
       df_shamoo = df.loc[df['Shmoo Value'].isnull() == False]
       shamoo_value = df_shamoo['Shmoo Value']
       shamoo_value_list = shamoo_value.values.tolist()
       #obtain x-axis
       voltage_list = []
       v1 = min(shamoo_value_list) - 0.1
       v2 = max(shamoo_value_list) + 0.1
       tmpv = v1
       while (tmpv <= v2):
              voltage_list.append(tmpv)
              tmpv += 0.02
              tmpv = round(tmpv, 2)

       # percentage = No. of (shamoo value < each vdd value) / total number of shamoo value
       prob_list = []
       count = 0
       for vol in voltage_list:
              for value in shamoo_value_list:
                     if (value < vol):
                            count += 1
              prob_list.append(100 * count / len(shamoo_value_list))
              count = 0
       return prob_list,voltage_list


def sc_vmin_data(spec_vol):
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


       df_ff = dftemp_lib.loc[dftemp['Chip Type'] == 'FF']
       prob_list,vol_list = calc_prob(df_ff)
       plt.plot(vol_list, prob_list, 's-')

       df_tt = dftemp_lib.loc[dftemp['Chip Type'] == 'TT']
       prob_list,vol_list = calc_prob(df_tt)
       plt.plot(vol_list, prob_list, 's-')

       df_ss = dftemp_lib.loc[dftemp['Chip Type'] == 'SS']
       prob_list,vol_list = calc_prob(df_ss)
       plt.plot(vol_list, prob_list, 's-')

       df_sf = dftemp_lib.loc[dftemp['Chip Type'] == 'SF']
       prob_list,vol_list = calc_prob(df_sf)
       plt.plot(vol_list, prob_list, 's-')

       df_fs = dftemp_lib.loc[dftemp['Chip Type'] == 'FS']
       prob_list,vol_list = calc_prob(df_fs)
       plt.plot(vol_list, prob_list, 's-')

       plt.axvline(x=spec_vol,linestyle='dashed')
       plt.legend(['FF','TT', 'SS','SF','FS','operating Spec'], loc='right')

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


       df_required = df_ema_temp_samev.loc[df['VDDPE (Range)'] == voltage]
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
       return

"""
inputs: memory instance,temperature
x-axis:vdd
y-axis:probability of pass
plots for different emas
"""
def mem_vmin_data_ss_one(spec_vol):
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

       # finding emas
       dfemas = dftemp_mem.drop_duplicates(['EMA#1'])
       dfema = dfemas['EMA#1']
       ema_list = dfema.values.tolist()

       #plotting
       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
              title='Probability plot for <' + mem_instance + '> at Temp = ' + str(temp) + chr(176) + 'C')


       for ema in ema_list:
              df_required = dftemp_mem.loc[dftemp_mem['EMA#1'] == ema]
              prob_list,vol_list = calc_prob(df_required)
              plt.plot(vol_list, prob_list, 's-')

       plt.axvline(x=spec_vol, linestyle='dashed')
       legend_list = ema_list
       legend_list.append('Operating Spec')
       plt.legend(legend_list, loc='right')

       plt.show()

       return

'''
inputs: ema = default(A2),temperature
x-axis:vdd
y-axis:probability of pass
plots for different memory instance
'''
#too many mem instaces -> hard to visualize all
def mem_vmin_data_ss_two(spec_vol):
       #finding required data frame based on inputs
       df = pd.read_csv('vminCkb.csv')
       df_ss = df.loc[df['Chip Type'] == 'SS']
       temp_list = ['25', '125', '150', 'M40']
       temp = temp_list[0]
       dftemp = df_ss.loc[df['Chip Temp'] == temp]
       default_ema = 'A2'
       dftemp_ema = dftemp.loc[dftemp['EMA#1'] == default_ema]

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


              for mem in mem_list[head_index:tail_index]:
                     df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
                     prob_list,vol_list = calc_prob(df_required)
                     plt.plot(vol_list, prob_list, 's-')

              plt.axvline(x=spec_vol, linestyle='dashed')
              tmp_legend_list = mem_list[head_index:tail_index]
              tmp_legend_list.append('Operating Spec')
              plt.legend(tmp_legend_list, loc='right')
              head_index = tail_index
              tail_index += 25

       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
              title='Probability plot for all mem_instances at ema = A2, Temp = ' + str(temp) + chr(176) + 'C')


       for mem in mem_list[head_index:len(mem_list)]:
              df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
              prob_list,vol_list = calc_prob(df_required)
              plt.plot(vol_list, prob_list, 's-')

       plt.axvline(x=spec_vol, linestyle='dashed')
       tmp_legend_list = mem_list[head_index:len(mem_list)]
       tmp_legend_list.append('Operating Spec')
       plt.legend(tmp_legend_list, loc='right')

       plt.show()
       return

"""
inputs:temperature,ss dataset,v1,v2
rows:library names
columns:voltage range,step is 20mV(default)
cell_text: p/f
"""
def sc_shamoo_data_ss(v1,v2):
       #obtain required dataframe based on inputs
       df = pd.read_csv('vminStd.csv')
       temp_list = ['25', '125', '150', 'M40']
       df_ss = df.loc[df['Chip Type'] == 'SS']
       temp = temp_list[0]
       dftemp = df_ss.loc[df_ss['Chip Temp'] == temp]

       #obtain rows
       dflibf = df_ss.drop_duplicates(['Test Item'])
       dflib = dflibf['Test Item']
       library_names_list = dflib.values.tolist()
       rows = library_names_list
       print(rows)

       #obtain columns
       vol_list = []
       tmpv = v1
       while (tmpv <= v2):
              vol_list.append(tmpv)
              tmpv += 0.02
              tmpv = round(tmpv, 2)
       columns = vol_list


       #obtain max. shamoo value as standard
       #if vol < shamoo: 'f' else: 'p'
       cell_text = []
       cell_color = []
       for i in range(len(library_names_list)):
              library_name = library_names_list[i]
              df_required = dftemp.loc[dftemp['Test Item'] == library_name]
              df_shamoo = df_required.loc[df_required['Shmoo Value'].isnull() == False]
              shamoo_value = max(df_shamoo['Shmoo Value'].values.tolist())

              # obtain cell_text
              tmp_cell_text = []
              tmp_cell_color = []
              # cell_text = []
              for vol in vol_list:
                     if (vol <= shamoo_value):
                            tmp_cell_text.append('F')
                            tmp_cell_color.append("#ff0000")
                     else:
                            tmp_cell_text.append('P')
                            tmp_cell_color.append("#008000")

              cell_text.append(tmp_cell_text)
              cell_color.append(tmp_cell_color)


       #plotting table
       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.axis('off')
       #title might overlap with the table(can be adjusted by pad,but depends on how large the table is.)
      # plt.title('Shamoo data for SS at Temp = ' + str(temp) + chr(176) + 'C',pad = 40)

       the_table = plt.table(cellText=cell_text,
                             cellColours=cell_color,
                             rowLabels=rows,
                             colLabels=columns,
                             loc='center')
       plt.show()

def memory_shamoo_data_ss(v1,v2):
       #obtain required dataframe
       df = pd.read_csv('vminCkb.csv')
       temp_list = ['25', '125', '150', 'M40']
       df_ss = df.loc[df['Chip Type'] == 'SS']
       temp = temp_list[0]
       dftemp = df_ss.loc[df_ss['Chip Temp'] == temp]

       #obtain columns
       vol_list = []
       tmpv = v1
       while (tmpv <= v2):
              vol_list.append(tmpv)
              tmpv += 0.02
              tmpv = round(tmpv, 2)
       columns = vol_list

       # obtain rows
       dfmemf = df_ss.drop_duplicates(['Architecture'])
       mem_instances_list = dfmemf['Architecture'].values.tolist()
       rows = mem_instances_list

       # obtain max. shamoo value as standard
       # if vol < shamoo: 'f' else: 'p'
       cell_text = []
       cell_color = []
       for i in range(len(mem_instances_list)):
              mem_name = mem_instances_list[i]
              df_required = dftemp.loc[dftemp['Architecture'] == mem_name]
              shamoo_value = max(df_required['Shmoo Value'].values.tolist())

              # obtain cell_text
              tmp_cell_text = []
              tmp_cell_color = []
              # cell_text = []
              for vol in vol_list:
                     if (vol <= shamoo_value):
                            tmp_cell_text.append('F')
                            tmp_cell_color.append("#ff0000")
                     else:
                            tmp_cell_text.append('P')
                            tmp_cell_color.append("#008000")

              cell_text.append(tmp_cell_text)
              cell_color.append(tmp_cell_color)


       # plt.title('Shamoo data for SS at Temp = ' + str(temp) + chr(176) + 'C',pad = 40)
       start_index = 0
       end_index = 30
       while(end_index < len(mem_instances_list)):
              # plotting table
              fig = plt.figure()
              ax = fig.add_subplot(111)
              ax.axis('off')
              the_table = plt.table(cellText=cell_text[start_index:end_index],
                                    cellColours=cell_color[start_index:end_index],
                                    rowLabels=rows[start_index:end_index],
                                    colLabels=columns,
                                    loc='center')
              start_index = end_index
              end_index += 30
       # plotting table
       fig = plt.figure()
       ax = fig.add_subplot(111)
       ax.axis('off')

       end_index = len(mem_instances_list)
       the_table = plt.table(cellText=cell_text[start_index:end_index],
                             cellColours=cell_color[start_index:end_index],
                             rowLabels=rows[start_index:end_index],
                             colLabels=columns,
                             loc='center')

       plt.show()


# sc_vmin_data(0.35)
# mem_vmin_data_ss_one(0.6)
# mem_vmin_data_ss_two(0.6)
# sc_shamoo_data_ss(0.3,0.5)
# memory_shamoo_data_ss(0.5,0.7)