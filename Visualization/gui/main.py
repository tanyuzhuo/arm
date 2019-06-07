from PyQt5.QtWidgets import*
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi

#from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

temp_list=[]
voltage_list=[]
df = pd.DataFrame()
class mainWindow(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        loadUi("first.ui",self)

        self.setWindowTitle("Arm Workflow Data Visualisation GUI V0.3")
        self.toolButton.clicked.connect(self.files)

        self.pushButton_Process.clicked.connect(self.preprocessing)
        self.comboBox.activated[str].connect(self.group_sel)
        #self.comboBox_Temp.activated.connect(self.vol_sel)
        self.pushButton.clicked.connect(self.update_graph)

    def preprocessing(self):

        global temp_list,df,voltage_list
        df = pd.read_csv('sample.csv')
        dftempf = df.drop_duplicates(['Chip Temp'])
        dftemplib = dftempf['Chip Temp']
        # transform into list
        temp_list = dftemplib.values.tolist()
        
        temp_list_string = [str(i) for i in temp_list]

        # add list to ComboBox
        self.comboBox_Temp.addItems(temp_list_string)



        dflibf = df.drop_duplicates(['VDD (V)'])
        dflib = dflibf['VDD (V)']
        # transform into list
        voltage_list = dflib.values.tolist()
        voltage_list_string = [str(i) for i in voltage_list]
        # add list to ComboBox
        self.comboBox_Voltage_StdYield.addItems(voltage_list_string)


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


    def update_graph(self):

        global temp_list,df,voltage_list
        # user selection

        inxTemp = self.comboBox_Temp.currentIndex()
        temp = temp_list[inxTemp]
        dftemp = df.loc[df['Chip Temp'] == temp]
        inxVol = self.comboBox_Voltage_StdYield.currentIndex()
        voltage = voltage_list[inxVol]
        dftemp_volt = dftemp.loc[df['VDD (V)'] == voltage]

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



app = QApplication([])
window = mainWindow()
window.show()
app.exec_()
