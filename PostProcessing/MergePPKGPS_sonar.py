"""Converted from MergePPKGPS_sonar.m by Spicer Bak and Chat GPT conversion on 3 July 2023.
This takes input from readNMEAfiles_lib.py (writes gnssraw.h5) and reads500pingsonardata_wts_gw_ct.py"""

import numpy as np
import matplotlib.pyplot as plt
import tqdm
from scipy import interpolate
import h5py
import pandas as pd
import PostProcessing.yellowfinLib as yellowfinLib
import datetime as DT
from scipy import signal

dirstr = '01-11-2023'
dirstr = '12-21-2022'  # with emlid ppk GPS saved and processed
dirstr = '01-05-2023'
dirstr = '20230327'  # has post processed Emlid data in folder. (*.pos file, maybe multiple)
database = "/home/spike/repos/yellowFin_AcqProcessing/SampleData"
timeString = "20230105"  #""20230417" # "20230327"
datadir = os.path.join(database,timeString)
plotDir = os.path.join(datadir,'figures')
os.makedirs(plotDir, exist_ok=True)  # make folder structure if its not already made
# sonar data
fpathSonar = os.path.join(datadir, 's500') # reads sonar from here
saveFnameSonar = os.path.join(datadir, f'{timeString}_sonarRaw.h5') #saves sonar file here

#NMEA data from sonar, this is not Post Processed Kinematic (PPK) data.  It is used for only cursory or
# introductory look at the data
fpathGNSS = os.path.join(datadir, 'nmeaData')  # load NMEA data from this location
saveFnameGNSS = os.path.join(datadir, f'{timeString}_gnssRaw.h5')  # save nmea data to this location

# RINEX data
# look for all subfolders with RINEX in the folder name inside the "datadir" emlid ppk processor
saveFnamePPK = os.path.join(datadir, f'{timeString}_ppkRaw.h5')

########################################################################################################################
# GPSfname = f"/data/yellowfin/{dirstr}/{dirstr}_gnssRaw.h5" # comes from readNMEAfiles.py
# PPKGPSfname = f"/data/yellowfin/{dirstr}/{dirstr}_ppkRaw.h5" # comes from read_emlid_LLH_raw.py
# S1fname = f"/data/yellowfin/{dirstr}/{dirstr}_sonarRaw.h5" # comes from reads500pingsonardata_wts_gw_ct.py
ET2UTC = 4*60*60 # time in seconds to adjust to UTC from ET (varies depending on time of year)
# load all files
GPS = yellowfinLib.load_h5_to_dictionary(saveFnameGNSS)
ppkGPS = pd.read_hdf(saveFnamePPK)
ppkGPS['epochTime'] = ppkGPS['datetime'].apply(lambda x: x.timestamp()) - 18 # 18 is leap second
# adjustment
ppkGPS['datetime'] = ppkGPS['datetime'] - DT.timedelta(seconds=18) # making sure both are equal
S1 = yellowfinLib.load_h5_to_dictionary(saveFnameSonar)

ppkGPS['GNSS_elevation_NAVD88'] = yellowfinLib.convertEllipsoid2NAVD88(ppkGPS['lat'], ppkGPS['lon'], ppkGPS['height'],
                                                   geoidFile="/home/spike/repos/yellowFin_AcqProcessing/g2012bu0.bin")


# Compare GPS data to make sure timing is ok
plt.figure()
pc_time_off = GPS['pc_time_gga'] + ET2UTC  - GPS['gps_time']
plt.plot(GPS['gps_time'], pc_time_off, '.')
plt.title('time offset between pc time and GPS time')
plt.xlabel('gps time')
plt.ylabel('time offset')

# Use the cerulean instantaneous bed detection since not sure about delay with smoothed
# adjust time of the sonar time stamp with timezone shift (ET -> UTC) and the timeshift between the computer and GPS
S1['time'] = S1['time'] + ET2UTC - np.median(pc_time_off)  # DT.timedelta(hours=5)  # convert to UTC
print('warning yellowfin computer time is not on UTC!!!!!! conversion assumes rigid offset')
sonar_range = S1['smooth_depth_m'] # S1['this_ping_depth_m']
smooth_sonar_range = S1['smooth_depth_m']

# plot ALLLL data
plt.figure(figsize=(16, 4))
plt.plot(S1['time'], sonar_range, 'b.', label='sonar instant depth')
# plt.plot(sonar_time, smooth_sonar_range, 'r.')
plt.plot(GPS['gps_time'], GPS['altMSL'], '.g', label='L1 GPS elev (MSL)')

# gps_leap_offset is
plt.plot(ppkGPS['epochTime'], ppkGPS['GNSS_elevation_NAVD88'], '.r', label='ppk elevation [NAVD88 m]')
plt.ylim([0, 20])
plt.legend()


# plot sonar, select indices of interest, and then second subplot is time of interest
plt.figure(figsize=(18,4))
plt.subplot(211)
plt.title('all data, select start/end point for measured depths\nadd extra time for PPK offset')
plt.plot(sonar_range)
plt.ylim([0,10])
d = plt.ginput(2)

plt.subplot(212)
# Now pull corresponding indices for sonar data for same time
sonarIndicies = np.arange(np.floor(d[0][0]).astype(int), np.ceil(d[1][0]).astype(int))
plt.plot(sonar_range[sonarIndicies])
plt.title('my selected data to proceed with')
plt.tight_layout()
plt.ylim([0,10])

# now identify corresponding times from ppk GPS to those times of sonar that we're interested in
indsPPK = np.where((ppkGPS['epochTime'] >= S1['time'][sonarIndicies[0]]) &
                   (ppkGPS['epochTime'] <= S1['time'][sonarIndicies[-1]]))[0]

## now interpolate the lower sampled (sonar 3.33 hz) to the higher sampled data (gps 10 hz)
# 1. identify common timestamp to interpolate to at higher frequency
commonTime = np.linspace(ppkGPS['epochTime'][indsPPK[0]], ppkGPS['epochTime'][indsPPK[-1]],
                        int((ppkGPS['epochTime'][indsPPK[-1]] - ppkGPS['epochTime'][indsPPK[0]])/.1), endpoint=True)

f = interpolate.interp1d(S1['time'], sonar_range) #, fill_value='extrapolate')
sonar_range_i = f(commonTime)
f = interpolate.interp1d(ppkGPS['epochTime'], ppkGPS['height'])
ppkHeight_i = f(commonTime)
# now i have both signals at the same time stamps
phaseLagInSamps, phaseLaginTime = yellowfinLib.findTimeShiftCrossCorr(signal.detrend(ppkHeight_i),
                                                                      signal.detrend(sonar_range_i),
                                                                      sampleFreq=np.median(np.diff(commonTime)))

# now make figure where i have subset that only looks at sonar elevations and GPS elevations
plt.figure(figsize=(12,8))
plt.subplot(211)
plt.plot(S1['time'][sonarIndicies], sonar_range[sonarIndicies], label='sonar_raw')
plt.plot(ppkGPS['epochTime'][indsPPK], ppkGPS['GNSS_elevation_NAVD88'][indsPPK], label='ppk elevation NAVD88 m')
plt.legend()
plt.subplot(212)
plt.title(f"sonar data needs to be adjusted by {phaseLaginTime} seconds")
plt.plot(commonTime, signal.detrend(ppkHeight_i), label='ppk input')
plt.plot(commonTime, signal.detrend(sonar_range_i), label='sonar input')
plt.plot(commonTime+phaseLaginTime, signal.detrend(sonar_range_i), '.', label='interp _sonar shifted')
plt.legend()
plt.tight_layout()
print(f"sonar data needs to be adjusted by {phaseLaginTime} seconds")

## now process all data for saving to file
antenna_offset = 0.25 # meters between the antenna phase center and sounder head
sonar_time_out = S1['time'] + phaseLaginTime

## ok now put the sonar data on the GNSS timestamps which are decimal seconds.  We can do this with sonar_time_out,
# because we just adjusted by the phase lag to make sure they are timesynced.
timeOutInterpStart =  np.ceil(sonar_time_out.min() * 10)/10 # round to nearest 0.1
timeOutInterpEnd = np.floor(sonar_time_out.max() * 10)/10 # round to nearest 0.1
# create a timestamp for data to be output and in phase with that of the ppk gps data which are on the 0.1 s
time_out = np.linspace(timeOutInterpStart, timeOutInterpEnd, int((timeOutInterpEnd - timeOutInterpStart)/0.1),
                       endpoint=True)

print("here's where some filtering could be done, probably worth saving an intermediate product here for future "
      "revisit")
# # upsample interpolate sonar data to time resolution of gnss
# sonar_SmoothDepth_out = interpolate.interp1d(sonar_time_out, S1['smooth_depth_m'])(time_out)
# sonar_SmoothConfidence_out = interpolate.interp1d(sonar_time_out, S1['smoothed_depth_measurement_confidence'])(time_out)
# sonar_InstantDepth_out = interpolate.interp1d(sonar_time_out, S1['this_ping_depth_m'])(time_out)
# sonar_InstantConfidence_out = interpolate.interp1d(sonar_time_out, S1['this_ping_depth_measurement_confidence'])(time_out)
# sonar_backscatter_out = interpolate.interp2d(sonar_time_out, S1['range_m'], S1['profile_data'])(time_out, S1['range_m'])

# now put relevant GNSS and sonar on output timestamps
#initalize out variables
sonar_smooth_depth_out, sonar_smooth_confidence_out = np.zeros_like(time_out)*np.nan, np.zeros_like(time_out)*np.nan
sonar_instant_depth_out, sonar_instant_confidence_out  = np.zeros_like(time_out)*np.nan, np.zeros_like(time_out)*np.nan
sonar_backscatter_out = np.zeros((time_out.shape[0], S1['range_m'].shape[0]))*np.nan
lat_out, lon_out = np.zeros_like(time_out)*np.nan, np.zeros_like(time_out)*np.nan
elevation_out, fix_quality = np.zeros_like(time_out)*np.nan, np.zeros_like(time_out)*np.nan
for tidx, tt in tqdm.tqdm(enumerate(time_out)):
    idxTimeMatchGNSS, idxTimeMatchGNSS = None, None
    
    #first find if theres a time match for sonar
    sonarlogic = np.abs(np.ceil(tt * 10)/10 - np.ceil(sonar_time_out*10)/10)
    if sonarlogic.min() <= 0.2: # .101 handles weird float numerics
        idxTimeMatchSonar= np.argmin(sonarlogic)
    # then find comparable time match for ppk
    ppklogic = np.abs(np.ceil(tt * 10)/10 - np.ceil(ppkGPS['epochTime'].array*10)/10)
    if ppklogic.min() <= 0.101:  # .101 handles numerics
        idxTimeMatchGNSS = np.argmin(ppklogic)
    # if we have both, then we log the data
    if idxTimeMatchGNSS is not None and idxTimeMatchSonar is not None : # we have matching data
        if ppkGPS['Q'][idxTimeMatchGNSS] <=1 and S1['smoothed_depth_measurement_confidence'][idxTimeMatchSonar] > 60:
            sonar_smooth_depth_out[tidx] = S1['smooth_depth_m'][idxTimeMatchSonar]
            sonar_instant_depth_out[tidx] = S1['this_ping_depth_m'][idxTimeMatchSonar]
            sonar_smooth_confidence_out[tidx] = S1['smoothed_depth_measurement_confidence'][idxTimeMatchSonar]
            sonar_instant_confidence_out[tidx] = S1['this_ping_depth_measurement_confidence'][idxTimeMatchSonar]
            sonar_backscatter_out[tidx] = S1['profile_data'][:, idxTimeMatchSonar]
            lat_out[tidx] = ppkGPS['lat'][idxTimeMatchGNSS]
            lon_out[tidx] = ppkGPS['lon'][idxTimeMatchGNSS]
            elevation_out[tidx] = ppkGPS['GNSS_elevation_NAVD88'][idxTimeMatchGNSS] - antenna_offset - S1['smooth_depth_m'][
                idxTimeMatchSonar]
            fix_quality[tidx] = ppkGPS['Q'][idxTimeMatchGNSS]

# identify data that are not nan's to save
idxDataToSave = np.argwhere(~np.isnan(sonar_smooth_depth_out)) # identify data that are not NaNs

# make a final plot of all the processed data
plt.figure()
plt.scatter(lon_out[idxDataToSave], lat_out[idxDataToSave], c=elevation_out[idxDataToSave])
plt.colorbar()
plt.plot(ppkGPS['lon'], ppkGPS['lat'], 'k.', ms=0.1, alpha=.7)
plt.ylabel('latitude')
plt.xlabel('longitude')
plt.title('final data with elevations')
plt.tight_layout()

outputfile = 'finalDataProduct.h5'
with h5py.File(outputfile, 'w') as hf:
    hf.create_dataset('time', data=time_out[idxDataToSave])
    hf.create_dataset('longitude', data=lon_out[idxDataToSave])
    hf.create_dataset('latitude', data=lat_out[idxDataToSave])
    hf.create_dataset('elevation', data=elevation_out[idxDataToSave])
    hf.create_dataset('fix_quality', data=fix_quality[idxDataToSave])
    hf.create_dataset('sonar_smooth_depth', data=sonar_smooth_depth_out[idxDataToSave])
    hf.create_dataset('sonar_smooth_confidence', data=sonar_smooth_confidence_out[idxDataToSave])
    hf.create_dataset('sonar_instant_depth', data=sonar_instant_depth_out[idxDataToSave])
    hf.create_dataset('sonar_instant_confidence', data=sonar_instant_confidence_out[idxDataToSave])
    hf.create_dataset('sonar_backscatter_out', data=sonar_backscatter_out[idxDataToSave])
