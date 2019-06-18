#import necessary modules
from PyQt5.QtWidgets import*
from PyQt5 import QtWidgets, QtCore
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.uic import loadUi
from joblib import load
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import image
import wholeDataTest
import re
import random
import os
from dython import nominal
import time
import seaborn as sns
from matplotlib.ticker import MultipleLocator
from matplotlib.ticker import MaxNLocator
from scipy import stats

#running progressbar in a separate thread to prevent gui freezing
class ProgressCheck(QThread):


     #emits integer progress value
     change_value = pyqtSignal(int)

     def run(self):
         global textDirec
         try:

             wholeDataTestClass = wholeDataTest.wholeDataTest(textDirec)

             wholeDataTestClass.collectFiles()

             numberOfFiles = wholeDataTestClass.processAllCSVInit()


             for i in range(numberOfFiles):
                 #update status bar


                 statusPercent = (i/numberOfFiles)*100
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

        #initialize main window and load GUI from Qt Designer
        QMainWindow.__init__(self)
        loadUi("vis.ui",self)
        self.setWindowTitle("Arm Workflow Data Visualisation & Science V0.7")

        #button connections to different command funcions
        self.toolButton.clicked.connect(self.files)
        self.pushButton_Process.clicked.connect(self.preprocessing)
        self.pushButton_2.clicked.connect(self.load)

        self.progressBar.setValue(0)
        self.progressBar.setMaximum(100)

        #displaying different sections based on inputs selected from the combobox or raido button
        self.comboBox_3.currentIndexChanged[str].connect(self.Sciprint)
        self.comboBox.currentIndexChanged[str].connect(self.print)
        self.radioButton_Mem.toggled.connect(self.memsel)
        self.radioButton_SC.toggled.connect(self.scsel)

    def preprocessing(self):
        #preprocessing progress function connected to the progresscheck thread
        self.thread = ProgressCheck()
        self.thread.change_value.connect(self.setProgressVal)
        self.thread.start()


    def setProgressVal(self,val):

        self.progressBar.setValue(val)

    def files(self):
        global textDirec

        #getting existing directory's file name
        current = QtCore.QDir.current()
        currentPath = QtCore.QDir.currentPath()
        dir = QtWidgets.QFileDialog.getExistingDirectory(self, "Select Folder", currentPath)
        textDirec = current.relativeFilePath(dir)
        self.textEdit.setText(textDirec)

    def Sciprint(self,str):

        #getting selected combobox options string
        cur_txt = str
        #connect to different graph functions based on selected options
        if cur_txt == 'Boxplots of Observed SC Vmin by Process and Temperature':
            try:
                #disconnect previous pushButton status subscribtion
                self.pushButton_Sci.clicked.disconnect()
            except:
                pass
            self.pushButton_Sci.clicked.connect(self.ml)
        if cur_txt == 'Boxplots of Observed SC Vmin by Library and Temperature':
            self.groupBox_Sci.show()
            try:
                self.pushButton_Sci.clicked.disconnect()
            except:
                pass
            self.pushButton_Sci.clicked.connect(self.ml2)
        else:
            self.groupBox_Sci.hide()

        if cur_txt == 'Std Cell Vmin Correlation Matrix':
            try:
                self.pushButton_Sci.clicked.disconnect()
            except:
                pass
            self.pushButton_Sci.clicked.connect(self.ml3)
        if cur_txt == 'Leakage Relation Graph':
            try:
                self.pushButton_Sci.clicked.disconnect()
            except:
                pass
            self.pushButton_Sci.clicked.connect(self.ml4)

        return

    def print(self,str):

        #getting selected combobox options string
        cur_txt = str
        #connect to different graph functions based on selected options
        if cur_txt == 'Stdcell Yield Data':
            self.groupBox_StdYield.show()
            try:
                #disconnect previous pushButton status subscribtion
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

    def load(self):

            #global parameters passed to different graph functions
            global df,df2,dfstd,dfmem,dfmemckb,temp_list,voltage_list,library_names_list,ema_list_yield,volmem_list
            global mainlib_list_f,vt_block_f,transistor_size_f,split_list,split_list_vmin,mem_list,ema_list_vmin,emapredict,ken

            #read postprocessed csv vminStd file
            dfstd = pd.read_csv('resultsPerDir/vminStd.csv')

            #drop duplicated temperature options based on inputs
            temp_list = list(dfstd['Chip Temp'].unique())
            temp_list_string = [str(i) for i in temp_list]
            # add list to ComboBox
            self.comboBox_Temp.addItems(temp_list_string)
            self.comboBox_Temp_P.addItems(temp_list_string)
            self.comboBox_Temp_P_2.addItems(temp_list_string)

            #drop duplicated split type options based on inputs
            split_list_vmin = list(dfstd['Chip Type'].unique())
            split_list_vmin_string = [str(i) for i in split_list_vmin]
            self.comboBox_Split.addItems(split_list_vmin_string)
            self.comboBox_SciSplit.addItems(split_list_vmin_string)
            self.comboBox_SP.addItems(split_list_vmin_string)

            #drop duplicated voltage options based on inputs
            voltage_list = list(dfstd['VDD (Range)'].unique())
            voltage_list_string = [str(i) for i in voltage_list]
            # add list to ComboBox
            self.comboBox_Voltage_StdYield.addItems(voltage_list_string)

            #drop duplicated library options based on inputs
            library_names_list = list(dfstd['Test Item'].unique())
            library_names_list_string = [str(i) for i in library_names_list]
            # add list to ComboBox
            self.comboBox_Lib.addItems(library_names_list_string)

            mainlib_list=[]
            subset_library = []
            vt_block = []
            transistor_size = []

            #regex out different sub sections as inputs for data science
            for i in library_names_list:
                tmp_list = re.split('_', i)
                mainlib_list.append(tmp_list[0])
                subset_library.append(tmp_list[1])
                vt_block.append(tmp_list[2])
                transistor_size.append(tmp_list[3])

            #create option lists
            mainlib_list_f = list(dict.fromkeys(mainlib_list))
            mainlib_list_string = [str(i) for i in mainlib_list_f]
            subset_library_f=list(dict.fromkeys(subset_library))
            subset_library_string = [str(i) for i in subset_library_f]
            vt_block_f=list(dict.fromkeys(vt_block))
            vt_block_string = [str(i) for i in vt_block_f]
            transistor_size_f=list(dict.fromkeys(transistor_size))
            transistor_size_string = [str(i) for i in transistor_size_f]

            #add lists to ComboBox
            self.comboBox_Mainlib.addItems(mainlib_list_string)
            self.comboBox_Sublib.addItems(subset_library_string)
            self.comboBox_Vt.addItems(vt_block_string)
            self.comboBox_Size.addItems(transistor_size_string)

            #data science Relation graphs filtering on csvs
            df=dfstd.copy()
            df.dropna(subset=['Shmoo Value'], inplace = True)
            df.drop(['File Index', 'Test Number', 'Period (Range)', 'DVDD (Range)', 'VDD (Range)', 'Result'], axis=1, inplace = True)
            df.columns = ['Process', 'Temperature', 'Library', 'Vmin']
            df['Temperature'] = pd.to_numeric(df['Temperature'], errors = 'coerce').fillna(-40.0).astype(float)

            df2 = pd.read_csv('resultsPerDir/leakage.csv')
            df2.drop(['File Index', 'DVDD (Range)', 'Period (Range)', 'VDD (Range)'], axis=1, inplace = True)
            df2['Value'] = df2['Value'].map(lambda x: x.rstrip('uA'))
            df2['Value'] = pd.to_numeric(df2['Value']).astype(float)


            #read postprocessed csv mem file
            dfmem = pd.read_csv('resultsPerDir/mem.csv',dtype={"Chip Temp": str})

            #drop duplicated emas for mem yield options based on inputs
            ema_list_yield = list(dfmem['EMA#1'].unique())
            ema_list_string = [str(i) for i in ema_list_yield]
            # add list to ComboBox
            self.comboBox_EmaYield.addItems(ema_list_string)



            df_ema_temp_samev = dfmem.loc[dfmem['VDDPE (Range)'] == dfmem['VDDCE (Range)']]
            #drop duplicated voltage list options for mem yield options based on inputs
            volmem_list= list(df_ema_temp_samev['VDDPE (Range)'].unique())
            volmem_list_string = [str(i) for i in volmem_list ]
            # add list to ComboBox
            self.comboBox_Voltage_MemYield.addItems(volmem_list_string)




            #read postprocessed csv vminckb file
            dfmemckb = pd.read_csv('resultsPerDir/vminCkb.csv')

            #drop duplicated split list options for mem shmoo options based on inputs
            split_list = list(dfmemckb['Chip Type'].unique())
            split_list_string = [str(i) for i in split_list]
            # add lists to ComboBox
            self.comboBox_SplitVmin.addItems(split_list_string)
            self.comboBox_Split_2.addItems(split_list_string)
            self.comboBox_SP_2.addItems(split_list_string)

            #drop duplicated architecture list options for mem vmin options based on inputs
            mem_list = list(dfmemckb['Architecture'].unique())
            mem_list_string = [str(i) for i in mem_list ]
            # add list to ComboBox
            self.comboBox_Instance.addItems(mem_list_string)

            #drop duplicated ema list options for mem vmin options based on inputs
            ema_list_vmin= list(dfmemckb['EMA#1'].unique())
            ema_list_vmin_string = [str(i) for i in ema_list_vmin ]
            # add list to ComboBox
            self.comboBox_EmaVmin.addItems(ema_list_vmin_string)



            #add ema options for memory prediction to comboBox
            emapredictf = list(map(lambda x : x.lstrip('A'),ema_list_vmin))
            emapredict = list(map(int,emapredictf))
            emapredict_string = [str(i) for i in emapredict]
            self.comboBox_EMA1.addItems(emapredict_string)

            #add ken options for memory prediction to comboBox
            ken= list(dfmemckb['KEN'].unique())
            ken_string = [str(i) for i in ken]
            self.comboBox_KEN.addItems(ken_string)

            return
    def memsel(self):
        #memory voltage prediction section display
        radioButton_Mem = self.sender()
        if radioButton_Mem.isChecked():
            self.groupBox_Pmem.show()
            self.groupBox_Pstd.hide()
            try:
                #disconnect previous pushButton status subscribtion
                self.pushButton_5.clicked.disconnect()
            except:
                pass
            self.pushButton_5.clicked.connect(self.mempredict)
        return
    def scsel(self):
        #std cell voltage prediction section display
        radioButton_SC = self.sender()
        if radioButton_SC.isChecked():
            self.groupBox_Pstd.show()
            self.groupBox_Pmem.hide()
            try:
                #disconnect previous pushButton status subscribtion
                self.pushButton_5.clicked.disconnect()
            except:
                pass
            self.pushButton_5.clicked.connect(self.scpredict)
        return
    def mempredict(self):
        global emapredict,temp_list,split_list,ken

        #read inputs from the comboBox
        inxTemp = self.comboBox_Temp_P_2.currentIndex()
        temperature = temp_list[inxTemp]

        inxSplit = self.comboBox_SP_2.currentIndex()
        process = split_list[inxSplit]

        inxEma = self.comboBox_EMA1.currentIndex()
        EMA1 = emapredict[inxEma]

        inxKen = self.comboBox_KEN.currentIndex()
        KEN = ken[inxKen]

        architecture = self.lineEdit.text()

        clf = load('RFVminMemShort (1).joblib')

        EMA1Vals = list(np.zeros(len(emapredict), dtype = int))

        architectureTrimmed = re.search('[A-Za-z0-9]+', architecture).group(0)
        archTypes = ['RA1HD', 'RA1HDA', 'RA1UHD', 'RA1UHDA', 'RA2PUHD', 'RA2PUHDA', 'RADPUHD', 'RF1HD','RF1HDA'
         , 'RF1UHD', 'RF2AHS', 'RF2HS','ROV', 'ROVA', 'SRAMSPHD', 'SRAMSPUHD', 'cln16ffcll']


        processValues = list(np.zeros(len(split_list), dtype = int))
        # processValues = [0,0,0,0,0]

        oneHotArch = np.zeros(17)

        # initialize with temperature
        inputVector = [float(temperature)/150.0]

        for i in range(len(archTypes)):
          if archTypes[i] == architectureTrimmed:
            oneHotArch[i] = 1

        inputVector.extend(oneHotArch)

        # process
        if process == 'FF':
          processValues[0] = 1
        elif process == 'FS':
          processValues[1] = 1
        elif process == 'SF':
          processValues[2] = 1
        elif process == 'SS':
          processValues[3] = 1
        else:
          processValues[4] = 1
        inputVector.extend(processValues)

        if EMA1 == 2:
          EMA1Vals[0] = 1
        elif EMA1 == 3:
          EMA1Vals[1] = 1
        else:
          EMA1Vals[2] = 1
        inputVector.extend(EMA1Vals)

        if KEN == 99:
          inputVector.extend([0,1])
        else:
          inputVector.extend([1,0])




        inputVector = np.asarray(inputVector)

        inputVector = inputVector.reshape(1, -1)

        result = float(clf.predict(inputVector))


        img1 = plt.imread('Screenshot 1.png', 0)
        img2 = plt.imread('Screenshot 2.png', 0)
        plt.subplot(2,1,1)
        plt.imshow(img1)
        plt.subplot(2,1,2)
        plt.imshow(img2)
        plt.show()
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Result')
        msg.setText('The Predicted Mem Voltage Value is '+ str(result)+' V')

        msg.setStandardButtons(QMessageBox.Cancel)
        exe = msg.exec_()


        return
    def scpredict(self):
        # global dfstd,library_names_list
        global temp_list,mainlib_list_f,vt_block_f,transistor_size_f,split_list_vmin

        # reading inputs from the comboBox
        inxTemp = self.comboBox_Temp_P.currentIndex()
        temperature = temp_list[inxTemp]
        if temperature == 'M40':
           temperature = -40.0

        inxLib = self.comboBox_Mainlib.currentIndex()
        mainLib = mainlib_list_f[inxLib]

        inxVt = self.comboBox_Vt.currentIndex()
        transistorVtBlock = vt_block_f[inxVt]

        inxSize = self.comboBox_Size.currentIndex()
        transistorSize = transistor_size_f[inxSize]

        inxSplit = self.comboBox_SP.currentIndex()
        process = split_list_vmin[inxSplit]
        clf = load('RFVminBasic (2).joblib')
        # initialize with temp
        processValues = [0,0,0,0,0]
        transistorVtBlockValues = [0,0,0]
        inputVector = [float(temperature)/150.0]

        # main lib
        if mainLib == 'sc7p5mcpp96p':
          inputVector.append(1)
        else:
          inputVector.append(0)

        # size
        if transistorSize == 'c16':
          inputVector.append(0)
        elif transistorSize == 'c18':
          inputVector.append(1)
        elif transistorSize == 'c20':
          inputVector.append(2)
        else:
          inputVector.append(3)

        # process
        if process == 'FF':
          processValues[0] = 1
        elif process == 'FS':
          processValues[1] = 1
        elif process == 'SF':
          processValues[2] = 1
        elif process == 'SS':
          processValues[3] = 1
        else:
          processValues[4] = 1
        inputVector.extend(processValues)

        # Vt block
        if transistorVtBlock == 'lvt':
          transistorVtBlockValues[0] = 1
        elif transistorVtBlock == 'svt':
          transistorVtBlockValues[1] = 1
        else:
          transistorVtBlockValues[2] = 1
        inputVector.extend(transistorVtBlockValues)

        a = np.asarray(inputVector)
        a = a.reshape(1, -1)
        result = float(clf.predict(a))

        #img_file = os.path.expanduser("tulip.png")

        #figure(figsize = (10,20))
        img = plt.imread('model1summary.png', 0)
        imgplot = plt.imshow(img)
        plt.show()

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)
        msg.setWindowTitle('Result')
        msg.setText('The Predicted SC Voltage Value is '+ str(result)+' V')

        msg.setStandardButtons(QMessageBox.Cancel)
        exe = msg.exec_()
        return
    def ml(self):
        global df


        # boxplot -> process comparison
        flatui = ["#9b59b6", "#34495e", "#95a5a6", "#e74c3c"]
        plt.figure(figsize=(13,10))
        sns.boxplot(x='Process', y='Vmin', data=df, hue='Temperature', showmeans=True, palette = flatui)
        plt.title('Boxplots of observed Vmin by Process and Temperature', fontsize=22)
        plt.show()


        return

    def ml2(self):
        global df
        # boxplot -> library comparison

        # reading inputs from the comboBox
        inxSplit = self.comboBox_SciSplit.currentIndex()
        split = split_list_vmin[inxSplit]
        libPlot = df.loc[df['Process'] == split]

        plt.figure(figsize=(20, 10))
        sns.boxplot(x='Library', y='Vmin', data=libPlot, hue = 'Temperature', showmeans=True)
        plt.xticks(rotation=60)
        plt.title('Vmin by library for the ' + split + ' process.', fontsize=22)
        plt.show()

        return

    def ml3(self):
        global df
        nominal.associations(df, nominal_columns=['Process','Library'], theil_u= True)
        return
    def ml4(self):
        global df2
        # scatter plot

        sns.catplot(x="Chip Type", y="Value", data=df2, col = 'Chip Temp', hue = 'Leakage Test Type')
        plt.show()

        return

    """
    used to calculate prob. of pass
    """
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

    """
    inputs: temperature,library name,chip type
    x-axis:vdd
    y-axis:probability of pass
    """
    def sc_vmin_data(self):
           global temp_list,dfstd,library_names_list

           # reading inputs from the comboBox
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
           plt.plot(vol_list, prob_list, 's-')

           df_tt = dftemp_lib.loc[dftemp['Chip Type'] == 'TT']
           prob_list,vol_list = self.calc_prob(df_tt)
           plt.plot(vol_list, prob_list, 's-')

           df_ss = dftemp_lib.loc[dftemp['Chip Type'] == 'SS']
           prob_list,vol_list = self.calc_prob(df_ss)
           plt.plot(vol_list, prob_list, 's-')

           df_sf = dftemp_lib.loc[dftemp['Chip Type'] == 'SF']
           prob_list,vol_list = self.calc_prob(df_sf)
           plt.plot(vol_list, prob_list, 's-')

           df_fs = dftemp_lib.loc[dftemp['Chip Type'] == 'FS']
           prob_list,vol_list = self.calc_prob(df_fs)
           plt.plot(vol_list, prob_list, 's-')

           plt.axvline(x=spec_vol,linestyle='dashed')
           plt.legend(['FF','TT', 'SS','SF','FS','operating Spec'], loc='right')

           plt.show()
           return

    """
    inputs: voltage,temperature,chip type
    x-axis:library name
    y-axis:yield
    """

    def std_cell_yield(self):

        global temp_list,dfstd
        # reading inputs from the comboBox
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

    """
    inputs:voltage, temperature,ema
    x-axis:library names
    y-axis:yield

    """
    def memory_yield_summary(self):

        global temp_list,dfmem,ema_list_yield,volmem_list
        # reading inputs from the comboBox
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

    """
    inputs: memory instance,temperature
    x-axis:vdd
    y-axis:probability of pass
    plots for different emas
    """
    def mem_vmin_data_ema(self):
        global temp_list,dfmem,dfmemckb,mem_list,split_list

        #finding required data frame based on inputs
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

    '''
    inputs: ema = default(A2),temperature
    x-axis:vdd
    y-axis:probability of pass
    plots for different memory instance
    '''
    def mem_vmin_data_instance(self):
        global temp_list,dfmem,dfmemckb,ema_list_vmin,split_list

        #finding required dataframe based on inputs

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



        mem_list = list(dftemp_ema['Architecture'].unique())

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

    """
    inputs:temperature,dataset,start voltage,end voltage
    rows:library names
    columns:voltage range,step is 20mV(default)
    cell_text: p/f
    """
    def sc_shamoo_data(self):
        global dfstd,temp_list,split_list_vmin

        #finding required dataframe based on inputs

        v1 = self.v1std.value()
        v2 = self.v2std.value()
        inxSplit = self.comboBox_Split.currentIndex()
        split = split_list_vmin[inxSplit]
        df = dfstd.loc[dfstd['Chip Type'] == split]
        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df.loc[df['Chip Temp'] == temp]

        #obtain rows

        library_list = list(dfstd['Test Item'].unique())
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

    """
    inputs:temperature,dataset,start voltage,end voltage
    rows:memory instances
    columns:voltage range,step is 20mV(default)
    cell_text: p/f
    """
    def memory_shamoo_data(self):
        global dfmemckb,temp_list,split_list

        #finding required dataframe based on inputs

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

        mem_instances_list =list(df['Architecture'].unique())
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
