from PyQt5.QtWidgets import*
from PyQt5 import QtWidgets, QtCore
from PyQt5.uic import loadUi

from matplotlib.backends.backend_qt5agg import (NavigationToolbar2QT as NavigationToolbar)
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt


class MatplotlibWidget(QMainWindow):

    def __init__(self):

        QMainWindow.__init__(self)

        loadUi("first.ui",self)

        self.setWindowTitle("Arm Workflow Data Visualisation GUI V0.2")
        self.toolButton.clicked.connect(self.files)
        self.pushButton.clicked.connect(self.update_graph)

        self.addToolBar(NavigationToolbar(self.MplWidget.canvas, self))

        # set slot for when option of combobox A is changed
        self.comboBox.currentIndexChanged[int].connect(self.comboOptionChanged)


        self.comboBox_Lib.addItem('lib1')
        self.comboBox_Lib.addItem('lib2')
        self.comboBox_Lib.addItem('lib3')
        self.comboBox_Lib.addItem('lib4')

        self.comboBox_Split.addItem('SS')
        self.comboBox_Split.addItem('TT')
        self.comboBox_Split.addItem('FF')

        self.comboBox_Ema.addItem('Ema1')
        self.comboBox_Ema.addItem('Ema2')
        self.comboBox_Ema.addItem('Ema3')
        # use a stacked layout to view only one of two combo box at a time
        self.combo_container_layout = QStackedLayout()

        self.combo_container_layout.addWidget(self.comboBox_Voltage)
        self.combo_container_layout.addWidget(self.comboBox_Lib)
        self.combo_container_layout.addWidget(self.comboBox_Split)
        self.combo_container_layout.addWidget(self.comboBox_Ema)










    def preprocessing(self):

        df = pd.read_csv('sample.csv')
        dftempf = df.drop_duplicates(['Chip Temp'])
        dftemplib = dftempf['Chip Temp']
        # transform into list
        temp_list = dftemplib.values.tolist()

        # add list to ComboBox
        #self.combo.addItems(temp_list)
        # user selection
        temp = temp_list[0]
        dftemp = df.loc[df['Chip Temp'] == temp]


        dflibf = dftemp.drop_duplicates(['VDD (V)'])
        dflib = dflibf['VDD (V)']
        # transform into list
        voltage_list = dflib.values.tolist()
        voltage_list_string = [str(i) for i in voltage_list]
        # add list to ComboBox
        self.comboBox_Voltage.addItems(voltage_list_string)


    def files(self):
        fileName, _ = QtWidgets.QFileDialog.getOpenFileName(None, "Select Datalogs", "", "Datalog Files (*.txt *.csv)") # Ask for file

    def comboOptionChanged(self, idx):
        ''' gets called when option for combobox A is changed'''

        # check which combobox_a option is selected ad show the appropriate combobox in stacked layout
        self.combo_container_layout.setCurrentIndex(idx)

    def update_graph(self):



        # user selection
        temp = temp_list[0]
        dftemp = df.loc[df['Chip Temp'] == temp]
        voltage = voltage_list[0]
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


        # self.MplWidget.canvas.axes.clear()
        # self.MplWidget.canvas.axes.plot(df_pivot.index,df_pivot.values)
        #
        # #self.MplWidget.canvas.axes.legend(('cosinus', 'sinus'),loc='upper right')
        # self.MplWidget.canvas.axes.set_title('Stdcell Yield at ' + str(voltage) + ' V / ' + str(temp) + chr(176) + 'C')
        # self.MplWidget.canvas.axes.xticks(np.arange(0, df_pivot.shape[0]), df_pivot.index,rotation = 45)
        # self.MplWidget.canvas.figure.autofmt_xdate()
        # self.MplWidget.canvas.draw()


app = QApplication([])
window = MatplotlibWidget()
window.show()
app.exec_()
