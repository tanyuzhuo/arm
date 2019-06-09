from PyQt5.QtWidgets import*
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi

#from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import image
temp_list=[]
voltage_list=[]

library_names_list=[]
dfstd = pd.DataFrame()
dfmem = pd.DataFrame()
dfmemckb = pd.DataFrame()
class mainWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        loadUi("vis.ui",self)

        self.setWindowTitle("Arm Workflow Data Visualisation GUI V0.3")
        self.toolButton.clicked.connect(self.files)

        self.pushButton_Process.clicked.connect(self.preprocessing)
        self.connect(self.)
        self.comboBox.activated[str].connect(self.group_sel)
        #self.comboBox_Temp.activated.connect(self.vol_sel)
        self.pushButton_2.clicked.connect(self.memory_yield_summary)

    def preprocessing(self):

        global temp_list,dfstd,dfmem,dfmemckb,voltage_list,library_names_list,ema_list,volmem_list
        #std operations
        #
        #

        dfstd = pd.read_csv('vminStd.csv')
        dftempf = dfstd.drop_duplicates(['Chip Temp'])
        dftemplib = dftempf['Chip Temp']
        # transform into list
        temp_list = dftemplib.values.tolist()
        temp_list_string = [str(i) for i in temp_list]
        # add list to ComboBox
        self.comboBox_Temp.addItems(temp_list_string)

        dfvolf = dfstd.drop_duplicates(['VDD (Range)'])
        dfvol = dfvolf['VDD (Range)']
        # transform into list
        voltage_list = dfvol.values.tolist()
        voltage_list_string = [str(i) for i in voltage_list]
        # add list to ComboBox
        self.comboBox_Voltage_StdYield.addItems(voltage_list_string)

        dflibf = dfstd.drop_duplicates(['Test Item'])
        dflib = dflibf['Test Item']
        # transform into list
        library_names_list = dflib.values.tolist()
        library_names_list_string = [str(i) for i in library_names_list]
        # add list to ComboBox
        self.comboBox_Lib.addItems(library_names_list_string)
        #mem yiled operations
        #
        #
        dfmem = pd.read_csv('mem.csv')
        dfemaf = dfmem.drop_duplicates(['EMA#1'])
        dfema = dfemaf['EMA#1']
        # transform into list
        ema_list = dfema.values.tolist()
        ema_list_string = [str(i) for i in ema_list]
        # add list to ComboBox
        self.comboBox_EmaYield.addItems(ema_list_string)
        self.comboBox_EmaVmin.addItems(ema_list_string)

        df_ema_temp_samev = dfmem.loc[dfmem['VDDPE (Range)'] == dfmem['VDDCE (Range)']]
        dfvolmemf = df_ema_temp_samev.drop_duplicates(['VDDPE (Range)'])
        dfvolmem = dfvolmemf['VDDPE (Range)']
        # transform into list
        volmem_list = dfvolmem.values.tolist()
        volmem_list_string = [str(i) for i in volmem_list ]
        # add list to ComboBox
        self.comboBox_Voltage_MemYield.addItems(volmem_list_string)

        # #mem vmin operations
        # #
        # #
        # dfmemckb = pd.read_csv('vminCkb.csv')



    def group_sel(self,text):
        cur_txt = text
        if cur_txt == 'Stdcell Yield Data':
            self.groupBox_StdYield.show()
        else:
            self.groupBox_StdYield.hide()
        if cur_txt == 'Stdcell Vmin Data':
            self.groupBox_StdVmin.show()
        else:
            self.groupBox_StdVmin.hide()
        if cur_txt == 'Stdcell Shmoo Data':
            self.groupBox_StdShmoo.show()
        else:
            self.groupBox_StdShmoo.hide()
        if cur_txt == 'Memory Yield Data':
            self.groupBox_MemYield.show()
        else:
            self.groupBox_MemYield.hide()
        if cur_txt == 'Memory Vmin Data':
            self.groupBox_MemVmin.show()
        else:
            self.groupBox_MemVmin.hide()
        if cur_txt == 'Memory Shmoo Data':
            self.groupBox_MemShmoo.show()
        else:
            self.groupBox_MemShmoo.hide()

    def files(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Datalogs", "", "Datalog Files (*.txt *.csv)") # Ask for file

    def calc_prob(self,df,voltage_list_v):

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

    def visualize(self,df,color):
           dflibf = df.drop_duplicates(['VDD (Range)'])
           dflib = dflibf['VDD (Range)']
           # transform into list
           voltage_list_v = dflib.values.tolist()
           prob_list = self.calc_prob(df,voltage_list_v)
           plt.plot(voltage_list, prob_list,color)
           return

    def sc_vmin_data(self):
           global temp_list,df,library_names_list


           inxTemp = self.comboBox_Temp.currentIndex()
           temp = temp_list[inxTemp]
           dftemp = dfstd.loc[df['Chip Temp'] == temp]



           inxLib = self.comboBox_Lib.currentIndex()
           library_name = library_names_list[inxLib]
           dftemp_lib = dftemp.loc[dftemp['Test Item'] == library_name]


           #plotting
           fig = plt.figure()
           ax = fig.add_subplot(111)
           ax.set(xlabel='VDD(V)', ylabel='probability of pass(%)',
                  title=library_name + ' at ' + str(temp) + ' ' + chr(176) + 'C')
           plt.axis([0.4, 1.2, 0, 105])


           df_ff = dftemp_lib.loc[dftemp['Chip Type'] == 'FF']
           self.visualize(df_ff,'ys-')
           df_tt = dftemp_lib.loc[dftemp['Chip Type'] == 'TT']
           self.visualize(df_tt, 'bs-')
           df_ss = dftemp_lib.loc[dftemp['Chip Type'] == 'SS']
           self.visualize(df_ss,'rs-')

           plt.legend(['FF','TT', 'SS'], loc='right')

           plt.show()
           return

    def std_cell_yield(self):

        global temp_list,dfstd
        # user selection

        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = dfstd.loc[df['Chip Temp'] == temp]
        inxVol = self.comboBox_Voltage_StdYield.currentIndex()
        voltage = voltage_list[inxVol]
        dftemp_volt = dftemp.loc[df['VDD (Range)'] == voltage]

        df_pivot = dftemp_volt.pivot_table(index=['Test Item'], columns="Chip Type", values="Result",
                                          aggfunc=lambda x: 100 * (x == '(P)').sum() / (
                                                         (x == '(P)').sum() + (x == '(F)').sum()))
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlabel='library name', ylabel='yield(%)',
               title='Stdcell Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(176) + 'C')
        df_pivot.plot(ax=ax)
        plt.xticks(np.arange(0, df_pivot.shape[0]), df_pivot.index,rotation = 45)
        fig.autofmt_xdate()
        plt.show()

    def memory_yield_summary(self):

        global temp_list,dfmem,ema_list,volmem_list
        # user selection
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = dfmem.loc[dfmem['Chip Temp'] == temp]
        inxEma = self.comboBox_EmaYield.currentIndex()
        ema = ema_list[inxEma]
        df_ema_temp = dftemp.loc[dfmem['EMA#1'] == ema]

        inxVol = self.comboBox_Voltage_MemYield.currentIndex()
        voltage = volmem_list[inxVol]
        df_required = df_ema_temp.loc[dfmem['VDDPE (Range)'] == voltage]
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


app = QApplication([])
window = mainWindow()
window.show()
app.exec_()
