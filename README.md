# ARM Data Visualization and Data Science
This repository contains an improved and automated approach to improve ARM's chip data workflow and provides further chip data insight analysis.

Arm is the world’s leading semiconductor IP company, with 125 billion chips shipped to date and these devices are used by over 70% of the global population. 

Today, several large-scale data analysis systems exist for product test data, but extracting the useful information from these data in a timely manner saves both engineering effort and reduces human errors which may affect the customer. Currently, engineers need to manually analyse these files and create reports for Arm and customers. Using individual perl scripts demand a lot of work to extract data and navigation through the files is extremely difficult since the work is done through perl and excel. This process is laborious and leads to a high degree of error in the existing scheme of data extraction.

Therefore, we propose an automated solution which will yield substantial acceleration and reduce testing efforts and costs. The goal is to validate Arm IP using a combination of Test data and target silicon data received from the foundry to confirm the chip was manufactured within a reasonable range of the expected process target window.
## Getting Started

Clone the repository into your local directory to get the source code.

### Prerequisites

You will need [Python 3](https://www.python.org) installed, a data folder provided by ARM that contains all the raw ASCII data txt files(NDA needed).

### Installing

Install the necessary packages:
```
git clone https://github.com/shakedzy/dython.git
pip install ./dython

pip install pandas
pip install numpy
pip install pyqt5
pip install joblib
```



## Deployment

Move the data folder in to the gui folder with the same directory as main.cpp
From the root folder, access the gui folder and run the GUI application:
```
cd Visualization/gui
python3 main.py
```
## Preprocessing

### Importance
Data preprocessing was a fundamental aspect of the project in the regard of without it functioning well the processing, analysis, and visualization could be either non-existent or unreliable. Thus, the data must first be manually analyzed for format to allow for an understanding of the file structure. This structure must then be implemented in an effective and easy to understand manner. After a working product is produced it must then be analyzed for performance and errors of which should be fixed. In final the ease of use for the product should be considered and the product evaluated for its compatibility to the next area of the project.

### Formatting
The data provided was given in the form of 5,339,362 lines of data across 410 files. Each file was formatted as a .txt document in ASCII-text form. The documents were composed of various types and variations of tests. Through practical analysis it was discovered that the tests were formatted in 6 different segments: pin test data, leakage test data, standard cell VMin data, memory yield data, memory VMin data, and shmoo only. These tests were formatted over overwhelmingly on a singular line, however, tests featuring shmoo components or tests with failed pins can feature data over multiple lines. Each tests data is separated through various combinations of space-related characters and underscores. In order to characterize the 5,339,362 lines of data, significant hours were needed to be delegated to analyzing files and creating scripts to check files for discrepancies and variations (manually or automatically created).

### Strategies
Various approaches were considered for preprocessing, the two dominant ones being: using iterative char if statements on strings to capture tests and using a regular expression library (regex) to analyse strings. In result, regex was used for its quicker developer time, a library that processes strings through lexing-like processing. The library was predominantly used to extract and match strings. The matching predominantly allowed test and test variance (shmoo and pin failures) detections and data segmentation capabilities. The extracting was used to output and separate finalized segmented data. All line by line analysis was segmented into data types (e.g. memory yield).

### Implementation and Optimisation
The portion of the project was initially created around a randomly chosen example file with indications of what differences would later be included noted. This file naturally grew to input a file name and output several CSV files corresponding to that file. In an attempt to encapsulate the code for ease of use a separate python script was created that would scan an inputted directory for formatted .txt data files and run the initial CSV conversion on each file. When first successfully done this was found to complete the whole process on 410 files in 15.17 minutes with each file taking an average time of 2.205 seconds. This was seen as excessive for preprocessing; thus, serious optimizations were needed. Also, noted on the first run, after meeting with the project advisor, was incorrect and self-assumed data formatting. Thus, the best-considered option was to rewrite the first CSV converting python file with the final design knowledge of the first file. This newly created file was heavily inspired by the first file, but relied on significantly less string mutation functions, if statements, and situational specific status flags. This new design was able to process all files in 6.97 minutes and an average file time of 1.022 seconds per file (roughly -54% completion time).

### Output Customisation 
How the output was formatted was also considered as it could take on various forms. Specifically, how outputted CSV files should be organized was considered. Initially, all files were designated to a new subfolder located in files matching the .txt origin file name in a larger directory created from the temperature and process type. These files consisted of all 6 data types as a separate CSV file. Additionally, a metadata sub CSV file for cautionary purposes was created (containing the intro and final bits of data on items like total test time) and an unused CSV file (containing unmatched (error) data that was created). The file structure of a CSV format was chosen by the industry advisor. However, after careful consideration, the second iteration consisted of combining all data to 6 CSV files in a singular directory. These CSV files featured additional columns to indicate which file they were from (their index, temperature tested, and their process type). This design was chosen as it was considered to be significantly easier to operate on during visualization and processing. However, it showed serious data size drawbacks needed for the extra columns and processing time drawbacks for finding the desired subsets of data. Also, if the data was much larger than we worked with it may pose challenges. Finally, a data structure combining test indexes and separating temperature tested and their process type were seen as the best alternative. This was viewed as a compromising median between the two extremes.

## GUI Design

### Language

The choice of GUI/Application design requires a systematic and easy-to-edit approach. Python is chosen in order to keep the whole GUI design written in the same format with the preprocessing part to be executed in a collective way. Moreover, the use of open source [Pandas](https://pandas.pydata.org) and [NumPy](https://www.numpy.org) library embedded in Python provides an effective way of data manipulation and analysis. In particular, Pandas offers data structures and operations for manipulating numerical tables which is crucial given the particular column-based format that those 8 CSVs generated after the pre-processing part. 
### PyQt5 X Qt Designer

There has been a number of Python GUI design frameworks: Tkinter, WxPython, PySide, PyGUI, PyQt, etc. Out of all those frameworks, [PyQt](https://pypi.org/project/PyQt5/) is chosen because of the simplicity and lightweight it brings, regarding the single one-click automation purpose which the client needs for the final application. [Qt Designer](https://doc.qt.io/qt-5/qtdesigner-manual.html) is the Qt tool for designing and building graphical user interfaces (GUIs) with Qt Widgets. The user is able to compose and customize windows or dialogs in a what-you-see-is-what-you-get (WYSIWYG) manner, and test them using different styles and resolutions. Widgets and forms created with Qt Designer integrate seamlessly with programmed code, using Qt's signals and slots mechanism, so that the user can easily assign behavior (different types of plots) to various graphical elements. Then the .ui format GUI desgined using the Qt Designer can be loaded using: 
```
from PyQt5.uic import loadUi
def __init__(self):
  loadUi("vis.ui",self)
```
in the Python main source code. All properties set in Qt Designer can be changed dynamically within the Python code using PyQt5 bindings. PyQt5, which is a comprehensive set of Python bindings for Qt version 5, is used in the final application framework. It is implemented as more than 35 extension modules and enables Python to be used as an alternative application development language to C++ on all supported platforms.

### Initial Version(up to 24th of May)
![First GUI Version](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/First%20GUI.jpg)
The initial GUI design comprises of a data input section, three parameter selection fields, a tool bar for navigating and manipulating the result plot and a graph canvas generated from matplotlib and embedded in the main window.

### Second Version(up to 3rd of June)
![Second GUI Version](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/Second%20GUI.png)
The second version of GUI improves on the visibility of showing different parameter option group boxes based on the type of graph selected:
```
StdCell Yield Data
StdCell Vmin Data
StdCell Shmoo Data
Memory Yield Data
Memory Vmin Data(EMA)
Memory Vmin Data(Instance)
Memory Shmoo Data
```
The graph canvas which is embedded in the main window is replaced by outputting graphs in separate windows for clearer visibility, better graph size adjustment, and a graph-to-graph comparison purpose.

### Final Demo Version(up to 14th of June)
![Final GUI Version Input](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/Input.jpg)
The final demo version creates three tabs for Input Options, Data Visualization and Data Science accordingly. Users will be allowed to select raw data files and perform preprocessing by click ‘PreProcess’ button, a progress bar is added to show the preprocessing progress which takes about 7 and half minutes. After the preprocessing is done, users will be able to press ‘Load’ button to load all the parameters extracted from the data logs into the selection fields in Data Visualization and Data Science tabs simultaneously. The whole loading process is subject to take 17-20 seconds.

![Final GUI Version Vis](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/DataVis.jpg)
A separate Data Science tab is added to provide more data insights. There are two sections in the main window: Data Correlation Graphs and Voltage Prediction.

![Final GUI Version Data Sci](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/data%20science.jpg)
Four different insights graphs are available upon selection under Data Correlation Graphs section:
```
Boxplots of Observed SC Vmin by Process and Temperature
Boxplots of Observed SC Vmin by Library and Temperature
Std Cell Vmin Correlation Matrix 
Leakage Relation Graph
```
In terms of the Voltage Prediction section, users will be able to select the type of voltage prediction(Std Cell or Memory) and thus select the relevant parameter options to predict the voltage result. A separate QmessageBox class will pop up as a message window to show the final prediction result.

![Final GUI Version Message](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/message.jpg)

#### Test Result of Plotting Standard Cell Vmin(Selecting sc7p5mcpp96p_sfk_lvt_c16 at 125° for a voltage spec input of 0.3V)
![Std vmin result](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/stdcell%20vmin.png)
 
#### Test Result of Plotting Memory Yield(Selecting EMA = A0 at 125° under 0.6V)
![Std vmin result](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/yield.jpg)
#### Test Result of Data Science Box Plot of Vmin by Process and Temperature
![Box result](https://github.com/tanyuzhuo/arm/blob/master/Visualization/GUI%20Graphs/boxplot.png)

#### Functions and Reference to Furture Upgrades

As mentioned above, the application uses 'loadui' imported from PyQt5.uic library to load the GUI framework. The application is able to take all the required parameteres from the preprocessed CSVs and add them into combo boxes and other selection fields using 
```
def load(self)
```
This function reads all the related CSV files from the root directory and uses, for example:
```
# drop duplicated voltage options based on inputs
  voltage_list = list(dfstd['VDD (Range)'].unique())
  voltage_list_string = [str(i) for i in voltage_list]
# add list to ComboBox
  self.comboBox_Voltage_StdYield.addItems(voltage_list_string)
```
to add unique and non-repetitive parameters to different selection fileds. By passing different global lists into various plotting functions while sharing the same list index as the string lists added to the combo boxes, the plotting functions will be able to correctly take in the different inputs required.

The plotting functionality is achieved by passing each particular type of graph strings when index is changed with the use of [Qt ComboBox](https://doc.qt.io/qt-5/qcombobox.html). Different graphs are selected from the combo box and are assigned to different plotting functions in Data Visualization and Data Science using:
```
self.comboBox.currentIndexChanged[str].connect(self.print)
self.comboBox_3.currentIndexChanged[str].connect(self.Sciprint)
```
Further future graph types can be added inside vis.ui file using [Qt Desginer](https://doc.qt.io/qt-5/qtdesigner-manual.html)
and are able to pass strings in the same method stated below to plot more types of graph required.

In this case, each string will be connected to different plotting functions for visulization and different graphs will be generated when the button is pressed by connecting the [Qt push button signals](https://wiki.qt.io/Qt_for_Python_Tutorial_ClickableButton) to each function.

```
def print(self, str):

        # getting selected combobox options string
        cur_txt = str
        # connect to different graph functions based on selected options
        if cur_txt == 'Stdcell Yield Data':
            self.groupBox_StdYield.show()
            try:
                # disconnect previous pushButton status subscribtion
                self.pushButton.clicked.disconnect()
            except:
                pass
            self.pushButton.clicked.connect(self.std_cell_yield)

        else:
            self.groupBox_StdYield.hide()
        if cur_txt =='......'
        # add future graph plotting types here
```
Overall, the demo GUI/application includes a general template/baseline as a reference to a further powerful automation workflow improvement that can be used in Data Analysis and Visualization.




## Data Visualization
After extracting core information about the data, this part of the project aims to display the data as the client required. Two python library(pandas and matplotlib) are exploited at this part. Different type of graphs can be displayed simultaneously, therefore the client can make a comparison on them. Generally, it has 7 different kinds of graphs with different inputs:

**1.standard cell yield data(inputs: voltage, temperature)**

summary and analysis: The standard cell yield for 'SS/SF/FS/FF/TT' process is  'xxx'% for all the tested libraries at the tested voltage and temperature conditions.

**2.probability plot for standard cell vmin test data(inputs: library name, temperature, operating specification voltage)**

summary and analysis: At all process corners, Vmin of all standard cell libraries are lower than  the specification at all temperatures, which is the expected trend.

**3.standard cell shamoo data for SS/SF/FS/FF/TT process(inputs: temperature)**

This section shows the standard cell functional shmoo data for SS process.Tests were performed between start voltage and end voltage defined by the client in 20mV increments. 

**4.memory yield summary(inputs: voltage, temperature)**

summary and analysis: The memory yield 'xxx'% at all process corners, for all the tested libraries at the tested voltage, temperature and EMA conditions

**5.probability plot for memory vmin test data for SS/SF/FS/FF/TT process(inputs: memory instance, temperature,operating specification voltage)**

summary and analysis: All memory instances meet the Vmin specification at SS/SF/FS/FF/TT corner.

**6.probability plot for memory vmin test data for SS/SF/FS/FF/TT process(inputs:EMA, temperature )**

summary and analysis: All memory instances meet the Vmin specification at SS/SF/FS/FF/TT corner.

**7.memory shamoo data for SS/SF/FS/FF/TT process(inputs: temperature)**

This section shows memory shmoo test for SS process at different temperatures.  


Displayed graphs on GUI can be found in [data visualization graphs](https://github.com/tanyuzhuo/arm/tree/master/Visualization/data%20visualization%20graphs) folder.
The hard part of data visualization is when plotting the probability of pass of standard cell vmin data and memory vmin data. Each percentage of the pass is calculated by number of shamoo value smaller than each voltage divided by the total number of shamoo value. This algorithm is used several times throughtout plotting.
Following is the algorithm used for plotting probability of pass:


```
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
```
Another issue that happened when implementing plotting is that the Mac OS X system crashed when trying to display graphs. This is due to the matplotlib library have conflicts with the GUI system. The solution to solve this is setting 'Qt5Agg' backend, and following is the code which implements this:
```buildoutcfg
import matplotlib
matplotlib.use("Qt5Agg")

```
## Data Science

This part of the project focused on extracting knowledge from the data and displaying it in a practical way. ARM's current process focuses on vizualization of the tesdatat results. However, little insight is gained into the relationships between the cells' (and wafers') parameters and their behaviours under different testing conditions. This part was also done using the  python programming language, and the `.ipynb` notebooks are available in this github repository for more information about the implementation of the machine learning section, whilst the first part of data science is included within the dashboard's code in the `main.py`.

First of all, boxplots and correlation matrices were built to explore Standard Cell behaviour as a function of temperature, process split, and design (library, size, etc) as can be seen in the example below. After these were analysed, key features for predicting Vmin were selected (Yield was 100% in the given dataset, hence no conclusions could be made). The goal was to design and train a Machine Learning model to predict Vmin values based on the variable parameters using in the chip testing process.

![Boxplot](https://github.com/tanyuzhuo/arm/blob/master/Images/boxplot.png)

The initial step when tackling this problem was to better understand the dataset available to build the model. The "vminStd.csv" file contained 9696 Vmin test results, and included all the parameters relevant to predicting Vmin. The data was split into a training set of 8196 datapoints, and was tested on a dataset of dimension 1500. Features used to train the model were selected by eliminating unuseful data (such as the test number, which is randomly assigned to each line of the datalog, and hence the .csv file). Then, the correlation data previously cited was used to narrow down the list.

The following step consisted of training different models and comparing their performances to select the optimal one, which would be incorporated to the dashboard discussed previously. Three very different model types were explored: a Random Forest regressor, a Perceptron and a Gaussian Process regressor. More information about how these models were implemented in practice can be found in the jupyter notebooks in this repository. The organic way in which categorical data in handled by decision trees made Random Forests the obvious choice for the first attempt. The performance was more than correct, since the mean absolute error on the test set was of 1.9%. The two other models were built for comparison purposes. The perceptron was used as a benchmark, linear regression being the go-to model in regression. Finally, the Gaussian Process route was explored according to suggestions from an ARM data scientist. None performed as well as the Random Forest did, which confirmed our initial assumption.

#### Comparison of the error plots for the SGD Regressor (left) and the Random Forest (right).
![SGD](https://github.com/tanyuzhuo/arm/blob/master/Images/SGD.png)
![RF](https://github.com/tanyuzhuo/arm/blob/master/Images/RF.png)

The same process was applied to `vminCkb.csv` to predict Vmin for memory cells, as can be seen on the dashboard itself.

Finally, pin leakage in the test chips was analysed using scatter plots, as can be seen in the image below. Clearly, the leakage is strongly influenced by the test parameters, as shown in the plot below. We explored the relationships between the current leakage and pin voltage tests but did not manage to obtain any useful information. A potential next step in the project would be to explore this further as there might be a way to incorporate that data in the Machine Learning models to increase their performance.

![Leakage](https://github.com/tanyuzhuo/arm/blob/master/Images/leakage.png)

## Contributing

As the project is part of the EE3-DTPRJ Design and Build Project (2018-2019) at Imperial College London, we do not accept external pull requests.

## Authors

* **Harrison Ankers** - [github.com/haankers](https://github.com/haankers)
* **Yuzhuo Tan** - [github.com/tanyuzhuo](https://github.com/tanyuzhuo)
* **Stevan Vukmirovic** - [github.com/VStevan](https://github.com/VStevan)
* **Zhendong Fu** - [github.com/LYZFU](https://github.com/LYZFU)
* **Rymon Yu** - [github.com/rymonyu](https://github.com/rymonyu)
