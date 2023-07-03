import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt

## converted read_emlid_LLH_raw.m in chatGPT on 19 February 2023

#Note that in Python, the code needs to explicitly import the necessary libraries and functions, unlike MATLAB which has them preloaded. Additionally, Python uses different syntax and naming conventions compared to MATLAB, so some modifications were made to convert the code.
# Emlid's software (free) emlid studio
# ubx -> rinex
# Will ask for base station file too (Should be also rinex) then it'll do processing and spit out text file
# (23B/o/P) are rinex files  -> built on RTK_Lib as processing engine open source GPS processing package
# Rinex files go to emlid studio
# pos file is output from emlid studio file (text file)
#

fs = '20221221165017'
fs = '20230105141705'
dirnm = f'YF2Reachm2_solution_{fs}_LLH'

dd = os.listdir(dirnm)
fn = os.path.join(dirnm, dd[2])  # this is before ppk processing so should agree with nmea strings
T = pd.read_csv(fn, delimiter='\s+', header=None)
T.columns = ['Var1', 'Var2', 'Var3', 'Var4']
T['date'] = pd.to_datetime(T['Var1'], format='%Y/%m/%d')
T['datetime'] = T['date'] + pd.to_timedelta(T['Var2'])
datetime1 = T['datetime']
lat = T['Var3']
lon = T['Var4']
fig = plt.figure(10)
fig.clf()
plt.plot(lon, lat, 'o-m')

dirnm = f'.\\YF2Reachm2_raw_{fs}_RINEX_3_03'

dd = os.listdir(dirnm)
fn = os.path.join(dirnm, 'YF2Reachm2_raw_' + fs + '.pos')  # note the e-file has a slightly modifed header to allow matlab to read the variable names
T2 = pd.read_csv(fn, skiprows=10)
T2.rename(columns={'x_': 'Date'}, inplace=True)
T2['date'] = pd.to_datetime(T2['Date'], format='%Y/%m/%d')
T2['datetime'] = T2['date'] + pd.to_timedelta(T2['GPST'])
datetime_ppk = T2['datetime']
lat_ppk = T2['latitude_deg_']
lon_ppk = T2['longitude_deg_']
fig = plt.figure(10)
plt.plot(lon_ppk, lat_ppk, '.-g')

fig = plt.figure(11)
fig.clf()
height_ell_ppk = T2['height_m_']
plt.plot(height_ell_ppk)
plt.hold(True)
plt.plot(10 * T2['Q'])
plt.plot(10000 * (T2['latitude_deg_'] - T2['latitude_deg_'].iloc[0]))
plt.savefig(f'PPK{fs}.png')

T2.to_csv(f'PPK{fs}.csv', index=False)
