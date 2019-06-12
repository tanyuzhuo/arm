from PyQt5.QtWidgets import*
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
#from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import image
import wholeDataTest
import re
import random
from dython import nominal
import time
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import MaxNLocator
from scipy import stats

dfstd = pd.DataFrame()
dfmem = pd.DataFrame()
dfmemckb = pd.DataFrame()

class ProgressCheck(QThread):
     change_value = pyqtSignal(int)
     # running = False
     # def __init__(self,parent=None):
     #     super(ProgressCheck,self).__init__(parent)
     #     self.running = True
     def run(self):
         try:
             #init class
             wholeDataTestClass = wholeDataTest.wholeDataTest(self.textDirec)
             #collect all csv files
             wholeDataTestClass.collectFiles()
             #init processing info
             numberOfFiles = wholeDataTestClass.processAllCSVInit()

             #loop and process each file
             for i in range(numberOfFiles):
                 #update status bar here


                 statusPercent = i/numberOfFiles
                 self.change_value.emit(statusPercent)

                 wholeDataTestClass.processIndivCSV(i)
             #print test meta info
             wholeDataTestClass.testsFinished()

         #catches when file is not chosen correctly
         except FileNotFoundError as e:
             print("wrong file selected")
         return


class mainWindow(QMainWindow):

    def __init__(self):
        #inits blank textbox content
        self.textDirec = ""
        QMainWindow.__init__(self)

        loadUi("vis.ui",self)
        self.toolButton.clicked.connect(self.files)

        self.pushButton_Process.clicked.connect(self.preprocessing)

        self.pushButton_2.clicked.connect(self.load)
        self.progressBar.setMaximum(100)
        self.comboBox.currentIndexChanged[str].connect(self.print)
        self.setWindowTitle("Arm Workflow Data Visualisation & Science V0.5")

        self.pushButton.clicked.connect(self.ml3)

    def preprocessing(self):
        self.thread = ProgressCheck()
        self.thread.change_value.connect(self.setProgressVal)
        self.thread.start()


    def setProgressVal(self,val):
        self.progressBar.setValue(val)
    def files(self):
        current = QtCore.QDir.current()
        currentPath = QtCore.QDir.currentPath()

        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", currentPath)
        self.textDirec = current.relativeFilePath(dir)

        self.textEdit.setText(self.textDirec)

    def print(self,str):
        cur_txt = str
        if cur_txt == 'Stdcell Yield Data':
            self.groupBox_StdYield.show()
            try:
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.std_cell_yield)

        else:
            self.groupBox_StdYield.hide()
        if cur_txt == 'Stdcell Vmin Data':
            self.groupBox_StdVmin.show()
            try:
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.sc_vmin_data)

        else:
            self.groupBox_StdVmin.hide()
        if cur_txt == 'Stdcell Shmoo Data':
            self.groupBox_StdShmoo.show()
            try:
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.sc_shamoo_data)
        else:
            self.groupBox_StdShmoo.hide()

        if cur_txt == 'Memory Yield Data':
            self.groupBox_MemYield.show()
            try:
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.memory_yield_summary)

        else:
            self.groupBox_MemYield.hide()
        if (cur_txt == 'Memory Vmin Data (Instance)' or cur_txt == 'Memory Vmin Data (EMA)'):
            if cur_txt == 'Memory Vmin Data (Instance)':
                  self.groupBox_3.show()
                  self.groupBox_MemVmin_2.show()
                  try:
                      self.pushButton.clicked.disconnect()
                  except:
                      pass
                  self.pushButton.clicked.connect(self.mem_vmin_data_instance)
            else:
                  self.groupBox_MemVmin_2.hide()
            if cur_txt == 'Memory Vmin Data (EMA)':
                  self.groupBox_3.show()
                  self.groupBox_MemVmin.show()
                  try:
                      self.pushButton.clicked.disconnect()
                  except:
                      pass
                  self.pushButton.clicked.connect(self.mem_vmin_data_ema)
            else:
                  self.groupBox_MemVmin.hide()
        else:
            self.groupBox_3.hide()


        if cur_txt == 'Memory Shmoo Data':
            self.groupBox_MemShmoo.show()
            try:
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.memory_shamoo_data)
        else:
            self.groupBox_MemShmoo.hide()
        return

    def load(self,text):
            global dfstd,dfmem,dfmemckb,temp_list,voltage_list,library_names_list,ema_list_yield,volmem_list,split_list,split_list_vmin,mem_list,ema_list_vmin
            if dfstd.empty:
              dfstd = pd.read_csv('resultsPerDir/vminStd.csv')

            dftempf = dfstd.drop_duplicates(['Chip Temp'])
            dftemplib = dftempf['Chip Temp']
            # transform into list
            temp_list = dftemplib.values.tolist()
            temp_list_string = [str(i) for i in temp_list]
            # add list to ComboBox
            self.comboBox_Temp.addItems(temp_list_string)

            dfsplit_shmoo_stdf = dfstd.drop_duplicates(['Chip Type'])
            dfsplit_shmoo_std = dfsplit_shmoo_stdf['Chip Type']
            split_list_vmin = dfsplit_shmoo_std.values.tolist()
            split_list_vmin_string = [str(i) for i in split_list_vmin]
            self.comboBox_Split.addItems(split_list_vmin_string)

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

            mainlib_list=[]
            subset_library = []
            vt_block = []
            transistor_size = []

            for i in library_names_list:
                tmp_list = re.split('_', i)
                mainlib_list.append(tmp_list[0])
                subset_library.append(tmp_list[1])
                vt_block.append(tmp_list[2])
                transistor_size.append(tmp_list[3])


            mainlib_list_f = list(dict.fromkeys(mainlib_list))
            mainlib_list_string = [str(i) for i in mainlib_list_f]
            subset_library_f=list(dict.fromkeys(subset_library))
            subset_library_string = [str(i) for i in subset_library_f]
            vt_block_f=list(dict.fromkeys(vt_block))
            vt_block_string = [str(i) for i in vt_block_f]
            transistor_size_f=list(dict.fromkeys(transistor_size))
            transistor_size_string = [str(i) for i in transistor_size_f]
            self.comboBox_Mainlib.addItems(mainlib_list_string)
            self.comboBox_Sublib.addItems(subset_library_string)
            self.comboBox_Vt.addItems(vt_block_string)
            self.comboBox_Size.addItems(transistor_size_string)


            if dfmem.empty:
              dfmem = pd.read_csv('resultsPerDir/mem.csv',dtype={"Chip Temp": str})
            dfemaf = dfmem.drop_duplicates(['EMA#1'])
            dfema = dfemaf['EMA#1']
            # transform into list
            ema_list_yield = dfema.values.tolist()
            ema_list_string = [str(i) for i in ema_list_yield]
            # add list to ComboBox
            self.comboBox_EmaYield.addItems(ema_list_string)


            df_ema_temp_samev = dfmem.loc[dfmem['VDDPE (Range)'] == dfmem['VDDCE (Range)']]
            dfvolmemf = df_ema_temp_samev.drop_duplicates(['VDDPE (Range)'])
            dfvolmem = dfvolmemf['VDDPE (Range)']
            # transform into list
            volmem_list = dfvolmem.values.tolist()
            volmem_list_string = [str(i) for i in volmem_list ]
            # add list to ComboBox
            self.comboBox_Voltage_MemYield.addItems(volmem_list_string)

            #mem Vmin operations
            #
            #
            if dfmemckb.empty:
              dfmemckb = pd.read_csv('resultsPerDir/vminCkb.csv')

            dfsplit = dfmemckb.drop_duplicates(['Chip Type'])
            dfsplitlib = dfsplit['Chip Type']
            # transform into list
            split_list = dfsplitlib.values.tolist()
            split_list_string = [str(i) for i in split_list]
            # add list to ComboBox
            self.comboBox_SplitVmin.addItems(split_list_string)
            self.comboBox_Split_2.addItems(split_list_string)

            dfarchi = dfmemckb.drop_duplicates(['Architecture'])
            mem_list = dfarchi['Architecture'].values.tolist()
            mem_list_string = [str(i) for i in mem_list ]

            # add list to ComboBox
            self.comboBox_Instance.addItems(mem_list_string)

            dfema = dfmemckb.drop_duplicates(['EMA#1'])
            dfemalib = dfema['EMA#1']
            # transform into list
            ema_list_vmin = dfemalib.values.tolist()
            ema_list_vmin_string = [str(i) for i in ema_list_vmin]
            # add list to ComboBox
            self.comboBox_EmaVmin.addItems(ema_list_vmin_string)

    def predict():
        global dfstd,library_names_list


        return
    def ml(self):
        global dfstd
        data=dfstd
        data['Chip Temp'] = pd.to_numeric(data['Chip Temp'], errors = 'coerce').fillna(-40.0).astype(float)

        # used to create sub-dataframes
        temperatureList = []
        vminList = []
        processList = []
        libraryList = []
        for i in range(len(data)): # iterate through csv to pick required data

            if data['Shmoo Value'][i] != -9.9:
                temperatureList.append(data['Chip Temp'][i])
                vminList.append(data['Shmoo Value'][i])
                processList.append(data['Chip Type'][i])
                libraryList.append(data['Test Item'][i])

        # First Datatict does not include the library data
        dataDict = {'Library':libraryList, 'Vmin':vminList , 'Temperature':temperatureList, 'Process':processList}
        df = pd.DataFrame(dataDict)

        #print(df.head()) # (for debugging purposes)

        # boxplot -> process comparison
        flatui = ["#9b59b6", "#34495e", "#95a5a6", "#e74c3c"]
        plt.figure(figsize=(13,10))
        sns.boxplot(x='Process', y='Vmin', data=df, hue='Temperature', showmeans=True, palette = flatui)
        plt.title('Boxplots of observed SC Vmin by Process and Temperature', fontsize=22)
        plt.show()


        return
    def ml2(self):
        global dfstd
        data=dfstd
        data['Chip Temp'] = pd.to_numeric(data['Chip Temp'], errors = 'coerce').fillna(-40.0).astype(float)

        # used to create sub-dataframes
        temperatureList = []
        vminList = []
        processList = []
        libraryList = []
        for i in range(len(data)): # iterate through csv to pick required data

            if data['Shmoo Value'][i] != -9.9:
                temperatureList.append(data['Chip Temp'][i])
                vminList.append(data['Shmoo Value'][i])
                processList.append(data['Chip Type'][i])
                libraryList.append(data['Test Item'][i])

        # First Datatict does not include the library data
        dataDict = {'Library':libraryList, 'Vmin':vminList , 'Temperature':temperatureList, 'Process':processList}
        df = pd.DataFrame(dataDict)

        # boxplot -> library comparison
        g = sns.catplot(x='Library', y='Vmin', data=df, col="Process", height = 10, aspect = 2, hue = 'Temperature', kind='box')
        g.set_xticklabels(rotation=85)
        plt.show()

        return
    def ml3(self):
        global dfstd
        data=dfstd
        data['Chip Temp'] = pd.to_numeric(data['Chip Temp'], errors = 'coerce').fillna(-40.0).astype(float)

        # used to create sub-dataframes
        temperatureList = []
        vminList = []
        processList = []
        libraryList = []
        for i in range(len(data)): # iterate through csv to pick required data

            if data['Shmoo Value'][i] != -9.9:
                temperatureList.append(data['Chip Temp'][i])
                vminList.append(data['Shmoo Value'][i])
                processList.append(data['Chip Type'][i])
                libraryList.append(data['Test Item'][i])

        # First Datatict does not include the library data
        dataDict = {'Library':libraryList, 'Vmin':vminList , 'Temperature':temperatureList, 'Process':processList}
        df = pd.DataFrame(dataDict)
        nominal.associations(df, nominal_columns=['Process','Library'], theil_u= True)
        return

    def calc_prob(self,df):

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



    def sc_vmin_data(self):
           global temp_list,dfstd,library_names_list

           spec_vol = self.vspecStd.value()
           inxTemp = self.comboBox_Temp.currentIndex()
           temp = temp_list[inxTemp]
           dftemp = dfstd.loc[dfstd['Chip Temp'] == temp]



           inxLib = self.comboBox_Lib.currentIndex()
           library_name = library_names_list[inxLib]
           dftemp_lib = dftemp.loc[dftemp['Test Item'] == library_name]


           #plotting
           fig = plt.figure()
           ax = fig.add_subplot(111)
           ax.set(xlabel='VDD(V)', ylabel='probability of pass(%)',
                  title=library_name + ' at ' + str(temp) + ' ' + chr(176) + 'C')



           df_ff = dftemp_lib.loc[dftemp['Chip Type'] == 'FF']
           prob_list,vol_list = self.calc_prob(df_ff)
           plt.plot(vol_list, prob_list, 'ys-')

           df_tt = dftemp_lib.loc[dftemp['Chip Type'] == 'TT']
           prob_list,vol_list = self.calc_prob(df_ff)
           plt.plot(vol_list, prob_list, 'bs-')

           df_ss = dftemp_lib.loc[dftemp['Chip Type'] == 'SS']
           prob_list,vol_list = self.calc_prob(df_ff)
           plt.plot(vol_list, prob_list, 'rs-')


           plt.axvline(x=spec_vol,linestyle='dashed')
           plt.legend(['FF','TT', 'SS','operating Spec'], loc='right')

           plt.show()
           return

    def std_cell_yield(self):

        global temp_list,dfstd
        # user selection

        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = dfstd.loc[dfstd['Chip Temp'] == temp]
        inxVol = self.comboBox_Voltage_StdYield.currentIndex()
        voltage = voltage_list[inxVol]
        dftemp_volt = dftemp.loc[dfstd['VDD (Range)'] == voltage]

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
        return
    def memory_yield_summary(self):

        global temp_list,dfmem,ema_list_yield,volmem_list
        # user selection
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = dfmem.loc[dfmem['Chip Temp'] == temp]
        inxEma = self.comboBox_EmaYield.currentIndex()
        ema = ema_list_yield[inxEma]
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
        return
    def mem_vmin_data_ema(self):
        global temp_list,dfmem,dfmemckb,mem_list,split_list

        spec_vol = self.vspecMem.value()

        inxSplit = self.comboBox_SplitVmin.currentIndex()
        split = split_list[inxSplit]

        df_ss = dfmemckb.loc[dfmemckb['Chip Type'] == split]
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df_ss.loc[dfmemckb['Chip Temp'] == temp]
        inxMem = self.comboBox_Instance.currentIndex()
        mem_instance= mem_list[inxMem]
        dftemp_mem = dftemp.loc[dftemp['Architecture'] == mem_instance]

        # #finding vdd list for x-axis and calc prob of pass
        #
        # tmp_df_ss = dfmem.loc[dfmem['Chip Type'] == split]
        # tmp_df_ss_samev = tmp_df_ss.loc[tmp_df_ss['VDDPE (Range)'] == tmp_df_ss['VDDCE (Range)']]
        # dfvol = tmp_df_ss_samev.drop_duplicates(['VDDPE (Range)'])
        # vol_list = sorted(dfvol['VDDPE (Range)'].values.tolist())

        # finding emas
        dfemas = dftemp_mem.drop_duplicates(['EMA#1'])
        dfema = dfemas['EMA#1']
        ema_list = dfema.values.tolist()

        #plotting
        fig = plt.figure()
        ax = fig.add_subplot(111)
        ax.set(xlabel='Vdd(V)', ylabel='probability of pass(%)',
               title='Probability plot for <' + mem_instance + '> at Temp = ' + str(temp) + chr(176) + 'C'+' for '+ split)


        for ema in ema_list:
               df_required = dftemp_mem.loc[dftemp_mem['EMA#1'] == ema]
               prob_list,vol_list = self.calc_prob(df_required)
               plt.plot(vol_list, prob_list, 's-')

        plt.axvline(x=spec_vol, linestyle='dashed')
        legend_list = ema_list
        legend_list.append('Operating Spec')
        plt.legend(legend_list, loc='right')
        plt.show()
        return

    def mem_vmin_data_instance(self):
        global temp_list,dfmem,dfmemckb,ema_list_vmin,split_list
        #finding required data frame based on inputs

        spec_vol = self.vspecMem.value()
        inxSplit = self.comboBox_SplitVmin.currentIndex()
        split = split_list[inxSplit]

        df_ss = dfmemckb.loc[dfmemckb['Chip Type'] == split]
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df_ss.loc[dfmemckb['Chip Temp'] == temp]
        inxEma = self.comboBox_EmaVmin.currentIndex()
        default_ema = ema_list_vmin[inxEma]
        dftemp_ema = dftemp.loc[dftemp['EMA#1'] == default_ema]

        # #finding vdd list for x-axis and calc prob of pass
        #
        # tmp_df_ss = dfmem.loc[dfmem['Chip Type'] == split]
        # tmp_df_ss_samev = tmp_df_ss.loc[tmp_df_ss['VDDPE (Range)'] == tmp_df_ss['VDDCE (Range)']]
        # dfvol = tmp_df_ss_samev.drop_duplicates(['VDDPE (Range)'])
        # vol_list = sorted(dfvol['VDDPE (Range)'].values.tolist())

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
                      title='Probability plot for all mem_instances at ema = '+ default_ema + ',Temp = ' + str(temp) + chr(176) + 'C'+' for '+ split)


               for mem in mem_list[head_index:tail_index]:
                      df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
                      prob_list,vol_list = self.calc_prob(df_required)
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
               title='Probability plot for all mem_instances at ema = '+ default_ema +',Temp = ' + str(temp) + chr(176) + 'C'+' for '+ split)

        for mem in mem_list[head_index:len(mem_list)]:
                df_required = dftemp_ema.loc[dftemp_ema['Architecture'] == mem]
                prob_list,vol_list = self.calc_prob(df_required)
                plt.plot(vol_list, prob_list, 's-')

        plt.axvline(x=spec_vol, linestyle='dashed')
        tmp_legend_list = mem_list[head_index:len(mem_list)]
        tmp_legend_list.append('Operating Spec')
        plt.legend(tmp_legend_list, loc='right')

        plt.show()
        return

    def sc_shamoo_data(self):
        global dfstd,temp_list,split_list_vmin
        #finding required data frame based on inputs

        v1 = self.v1std.value()
        v2 = self.v2std.value()
        inxSplit = self.comboBox_Split.currentIndex()
        split = split_list_vmin[inxSplit]
        df = dfstd.loc[dfstd['Chip Type'] == split]
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df.loc[df['Chip Temp'] == temp]

        #obtain rows
        dflibf = dfstd.drop_duplicates(['Test Item'])
        dflib = dflibf['Test Item']
        library_list = dflib.values.tolist()
        rows = library_list

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
        for i in range(len(library_list)):
               library_name = library_list[i]
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
        return

    def memory_shamoo_data(self):
        global dfmemckb,temp_list,split_list

        #finding required data frame based on inputs

        v1 = self.v1Mem.value()
        v2 = self.v2Mem.value()
        inxSplit = self.comboBox_Split_2.currentIndex()
        split = split_list_vmin[inxSplit]
        df = dfmemckb.loc[dfmemckb['Chip Type'] == split]
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df.loc[df['Chip Temp'] == temp]

        #obtain columns
        vol_list = []
        tmpv = v1
        while (tmpv <= v2):
               vol_list.append(tmpv)
               tmpv += 0.02
               tmpv = round(tmpv, 2)
        columns = vol_list

        # obtain rows
        dfmemf = df.drop_duplicates(['Architecture'])
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

        return
app = QApplication([])
window = mainWindow()
window.show()
app.exec_()
