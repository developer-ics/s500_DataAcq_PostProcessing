import os
import pandas as pd
import datetime
import matplotlib.pyplot as plt
import glob
## converted read_emlid_LLH_raw.m in chatGPT on 19 February 2023

#Note that in Python, the code needs to explicitly import the necessary libraries and functions,
# unlike MATLAB which has them preloaded. Additionally, Python uses different syntax and naming
# conventions compared to MATLAB, so some modifications were made to convert the code.
# Emlid's software (free) emlid studio
# ubx -> rinex
# Will ask for base station file too (Should be also rinex) then it'll do processing and spit out text file
# (23B/o/P) are rinex files  -> built on RTK_Lib as processing engine open source GPS processing package
# Rinex files go to emlid studio
# pos file is output from emlid studio file (text file)
#
#
# fs = '20221221165017'
# fs = '20230105141705'
folderstr = 20230327
rootDir = f'/data/yellowfin/{folderstr}'
# find folders that have name rinex in it and aren't zip files (these contain the pos files)
fldrlistLLH, fldrlistPPK = [], []
[fldrlistPPK.append(fname)  for fname in os.listdir(rootDir) if 'RINEX' in fname and '.zip' not in fname]
[fldrlistLLH.append(fname)  for fname in os.listdir(rootDir) if 'LLH' in fname and '.zip' not in fname]


# first load the LLH quick processed data
T_LLH = pd.DataFrame()
for fldr in sorted(fldrlistLLH):
    # this is before ppk processing so should agree with nmea strings
    fn = glob.glob(os.path.join(rootDir, fldr, "*"))[0]
    try:
        T = pd.read_csv(fn, delimiter='  ', header=None, engine='python')
        print(f'loaded {fn}')
        if all(T.iloc[-1]):  #if theres nan's in the last row
            T = T.iloc[:-1] # remove last row
        T_LLH = pd.concat([T_LLH, T]) # merge multiple files to single dataframe
        
    except:
        continue

T_LLH['datetime'] = pd.to_datetime(T_LLH[0], format='%Y/%m/%d %H:%M:%S.%f')
T_LLH['lat'] =  T_LLH[1]
T_LLH['lon'] = T_LLH[2]


# now load  Post processed kinematic PPK files from the pos file that was post processed in emlid

T_ppk = pd.DataFrame()
for fldr in sorted(fldrlistPPK):
    # this is before ppk processing so should agree with nmea strings
    fn = glob.glob(os.path.join(rootDir, fldr, "*.pos"))[0]
    try:
        colNames = ['datetime', 'lat', 'lon', 'height', 'Q', 'ns', 'sdn(m)',  'sde(m)', 'sdu(m)', \
                    'sdne(m)', 'sdeu(m)',  'sdun(m)', 'age(s)',  'ratio']
        Tpos = pd.read_csv(fn, delimiter=r'\s+ ', header=10, names=colNames, engine='python')
        print(f'loaded {fn}')
        if all(Tpos.iloc[-1]):  #if theres nan's in the last row
            Tpos = Tpos.iloc[:-1] # remove last row
        T_ppk = pd.concat([T_ppk, Tpos]) # merge multiple files to single dataframe
        
    except:
        continue
T_ppk['datetime'] = pd.to_datetime(T_ppk['datetime'], format='%Y/%m/%d %H:%M:%S.%f')


# now make plot of both files
# first llh file
plt.plot(T_LLH['lon'], T_LLH['lat'], '.-m', label = 'LLH file')
plt.xlabel('longitude')
plt.ylabel('latitude')
# fir
plt.plot(T_ppk['lon'], T_ppk['lat'], '.-g', label = 'PPK file')
plt.xlabel('longitude')
plt.ylabel('latitude')
plt.legend()
plt.tight_layout()


fig = plt.figure()
plt.plot(T_ppk['datetime'], T_ppk['height'], label='elevation')
plt.plot(T_ppk['datetime'], 10 * T_ppk['Q'], '.', label='quality factor')
plt.plot(T_ppk['datetime'], 10000 * (T_ppk['lat'] - T_ppk['lat'].iloc[0]), label='lat from original lat')
plt.xlabel('time')
plt.legend()
plt.tight_layout()
# plt.savefig(f'PPK{fs}.png')

T_ppk.to_hdf(f'{folderstr}_ppkRaw.h5')

