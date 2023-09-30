"""This file is an evolution of reads500pingsonar.py a little tightened up and functions are ready to migrate to
library"""
from datetime import datetime
import matplotlib
from PostProcessing.yellowfinLib import loadSonar_s500_binary
# matplotlib.use('Agg')
from matplotlib import pyplot as plt
import numpy as np
import tqdm
import netCDF4 as nc
import h5py
fpath = '/data/yellowfin/20230327/s500' # reads sonar from here
sonarH5 = '/data/yellowfin/20230327/20230327_sonarRaw.h5' #saves sonar file here

loadSonar_s500_binary(fpath, outfname=sonarH5, verbose=False)
#sonarData = loadSonarH5(sonarH5)
#
# # sub parse data to make sense
# startTime = datetime(2023, 3, 27, 14, 40)
# endTime =  datetime(2023, 3, 27, 15)
#
# # unpack loaded sonar data
# time = nc.num2date(sonarData['time'], 'seconds since 1970-01-01', only_use_cftime_datetimes=False,
#                    only_use_python_datetimes=True)  # nc.num2date(sonarData['time'], 'seconds since 1970-01-01')
# subset = np.argwhere((time > startTime) & (time < endTime)).squeeze()
# time = time[subset]
# profile_data = sonarData['profile_data'][:, subset].T
# smooth_depth_m = sonarData['smooth_depth_m'][subset]
# smooth_depth_confidence = sonarData['smoothed_depth_measurement_confidence'][subset]
# this_ping_depth_m = sonarData['this_ping_depth_m'][subset]
# this_ping_depth_confidence = sonarData['this_ping_depth_measurement_confidence'][subset]
# analog_gain = sonarData['analog_gain'][subset]
# sonarRange = sonarData['range_m'][subset, :]
# # subset data to interesting
# # for i in tqdm.tqdm(range(len(time))):
# #     fname = f'/data/yellowfin/20230327/figures/sonar_{time[i].strftime("%Y%m%dT%H%M%S.%f")}.png'
# #     plot_single_backscatterProfile(fname, time, sonarRange, profile_data, this_ping_depth_m, smooth_depth_m, index=i)
#
# # plotting figures
# i = 3000
#
# plt.gca().invert_yaxis()
# plt.ylabel('Depth (m)')
# plt.xlabel('Time (hh:mm)')
# plt.plot(dt_profile, smooth_depth_m, '.k', ms=3)
# plt.savefig(f'profile_data_{datestring}_python.png')
#
#
# plt.figure(5)
# plt.pcolormesh(dt_profile, rangev[2] / 1000, filt_prof_data.T, shading='auto')
# plt.plot(dt_profile, smooth_depth_m, '.k', ms=3)
# plt.title('filtered version of profile plot')
# plt.ylabel('Depth (m)')
# plt.ylim([0, 12])
# plt.xlabel('Time (hh:mm)')
# plt.colorbar()
# plt.tight_layout()
# plt.savefig(f'profile_data_{datestring}_Cleaned_python.png')
#
# # spicer stopped conversion here as smooth depth provided by manufacturer looked good enough compared to below
# # filtering.  Nothing further was tested, but inital conversion from chatGPT provided for anyone who want's to proceed.
