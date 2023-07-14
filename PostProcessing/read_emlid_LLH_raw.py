import os
import matplotlib.pyplot as plt
from PostProcessing.yellowfinLib import loadLLHfiles, loadPPKdata

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
ppkOutPath=f'/data/yellowfin/{folderstr}/{folderstr}_ppkRaw.h5'
# find folders that have name rinex in it and aren't zip files (these contain the pos files)
fldrlistLLH, fldrlistPPK = [], []
[fldrlistPPK.append(os.path.join(rootDir,fname))  for fname in os.listdir(rootDir) if 'RINEX' in fname and '.zip' not in
                    fname]
[fldrlistLLH.append(os.path.join(rootDir, fname))  for fname in os.listdir(rootDir) if 'LLH' in fname and '.zip' not in
                    fname]

# now load  Post processed kinematic PPK files from the pos file that was post processed in emlid
T_LLH = loadLLHfiles(fldrlistLLH)
T_ppk = loadPPKdata(fldrlistPPK)
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

T_ppk.to_hdf(ppkOutPath, 'ppk')
print(f'saved {ppkOutPath}')
