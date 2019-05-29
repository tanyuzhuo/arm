import pandas as pd
import numpy as np

# read Harry's CSV file
data = pd.read_csv("vminStd.csv")

# convert string to integer, and replace M40
data['Chip Temp'] = pd.to_numeric(data['Chip Temp'], errors='coerce').fillna(-40).astype(np.int64)
final_data = data.copy()

# concatenate columns to get library name 
final_data['Test Item'] = final_data['Test Item'].str.cat(data['Library #1'],sep="_")
final_data['Test Item'] = final_data['Test Item'].str.cat(data['Library #2'],sep="_")
final_data['Test Item'] = final_data['Test Item'].str.cat(data['Library #3'],sep="_")
del final_data['Library #1']
del final_data['Library #2']
del final_data['Library #3']

# convert voltages into floats
final_data['VDD (Range)'] = final_data['VDD (Range)'].map(lambda x: x.rstrip('V'))
final_data['DVDD (Range)'] = final_data['DVDD (Range)'].map(lambda x: x.rstrip('V'))
final_data.rename(columns={'VDD (Range)': 'VDD (V)', 'DVDD (Range)': 'DVDD (V)'}, inplace=True)

final_data['VDD (V)'] = pd.to_numeric(final_data['VDD (V)'], errors='coerce').fillna(0.0).astype(np.double)
final_data['DVDD (V)'] = pd.to_numeric(final_data['DVDD (V)'], errors='coerce').fillna(0.0).astype(np.double)

final_data2 = final_data.sort_values(by=['File Index', 'Chip Temp', 'Test Item', 'VDD (V)', 'DVDD (V)'], ascending=[True, True, True, True, True])

print(final_data2.head())
print(final_data2['Test Item'].value_counts())
print(final_data2['Chip Type'].value_counts())
print(final_data2['Chip Temp'].value_counts())

final_data2.to_csv('sortedVminStd.csv', index=False, mode='w')
