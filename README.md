# ARM Data Visualization and Data Science
This repository contains an improved and automated approach to improve ARM's chip data workflow and with provide further data insights analysis.

Arm is the world’s leading semiconductor IP company, with 125 billion chips shipped to date and these devices are used by over 70% of the global population. 

Today, several large-scale data analysis systems exist for product test data, but extracting the useful information from these data in a timely manner saves both engineering effort and reduces human errors which may affect the customer. Currently, engineers need to manually analyse these files and create reports for Arm and customers. Using individual perl scripts demand a lot of work to extract data and navigation through the files is extremely difficult since the work is done through perl and excel. This process is laborious and leads to a high degree of error in the existing scheme of data extraction.

Therefore, we propose an automated solution which will yield substantial acceleration and reduce testing efforts and costs. The goal is to validate Arm IP using a combination of Test data and target silicon data received from the foundry to confirm the chip was manufactured within a reasonable range of the expected process target window.
## Getting Started

Clone the repository into your local directory to get the source code.

### Prerequisites

You will need [Python 3](https://www.python.org) installed, a data folder provided by ARM that contains all the raw ASCII data txt files.

### Installing

Install the necessary packages:
```
pip install pandas
pip install numpy
pip install pyqt5
pip install dython
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
## GUI Design
## Data Visualiztion
## Data Science
## Contributing

As the project is part of the EE3-DTPRJ Design and Build Project (2018-2019) at Imperial College London, we do not accept external pull requests.

## Authors

* **Harrison Ankers** - [github.com/haankers](https://github.com/haankers)
* **Yuzhuo Tan** - [github.com/tanyuzhuo](https://github.com/tanyuzhuo)
* **Stevan Vukmirovic** - [github.com/VStevan](https://github.com/VStevan)
* **Zhendong Fu** - [github.com/LYZFU](https://github.com/LYZFU)
* **Rymon Yu** - [github.com/rymonyu](https://github.com/rymonyu)
