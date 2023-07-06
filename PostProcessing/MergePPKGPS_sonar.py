"""Converted from MergePPKGPS_sonar.m by Spicer Bak and Chat GPT conversion on 3 July 2023.
This takes input from readNMEAfiles_lib.py (writes gnssraw.h5) and reads500pingsonardata_wts_gw_ct.py"""

import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime, timedelta
from scipy.interpolate import interp1d
import h5py
import pandas as pd
import PostProcessing.yellowfinLib as yellowfinLib
import datetime as DT
dirstr = '01-11-2023'
dirstr = '12-21-2022'  # with emlid ppk GPS saved and processed
dirstr = '01-05-2023'
dirstr = '20230327'  # has post processed Emlid data in folder. (*.pos file, maybe multiple)

GPSfname = f"/data/yellowfin/{dirstr}/{dirstr}_gnssRaw.h5" # comes from readNMEAfiles.py
PPKGPSfname = f"/data/yellowfin/{dirstr}/{dirstr}_ppkRaw.h5" # comes from read_emlid_LLH_raw.py
S1fname = f"/data/yellowfin/{dirstr}/{dirstr}_sonarRaw.h5" # comes from reads500pingsonardata_wts_gw_ct.py
ET2UTC = 4*60*60 # time in seconds to adjust to UTC from ET (varies depending on time of year)
# load all files
GPS = yellowfinLib.load_h5_to_dictionary(GPSfname)
ppkGPS = pd.read_hdf(PPKGPSfname)
S1 = yellowfinLib.load_h5_to_dictionary(S1fname)

# Compare GPS data to make sure timing is ok
plt.figure()
# plt.plot(GPS['gps_time'], '.')
# hr = np.floor(GPS['gps_time'] / 10000)
# mm = np.floor((GPS['gps_time'] / 10000) % 1 * 100)
# ss = ((GPS['gps_time'] / 100) % 1) * 100
# GPS_mat_time = np.array([datetime(int(dirstr[-4:]), int(dirstr[0:2]), int(dirstr[3:5]), int(h), int(m), int(s)) for h, m, s in zip(hr, mm, ss)])
pc_time_off = GPS['pc_time_gga'] + ET2UTC  - GPS['gps_time']
plt.plot(GPS['gps_time'], pc_time_off, '.')
plt.title('time offset between pc time and GPS time')
plt.xlabel('gps time')
plt.ylabel('time offset')

# plt.plot(GPS['gps_time'], GPS['lat'], '.') # what does this tell me
gps_leap_offset = DT.timedelta(seconds=18)  # should be 19 but 18 lines it up!
plt.plot(ppkGPS['datetime'] - gps_leap_offset, ppkGPS['lat'], 'r')
# plt.plot(ppkGPS['datetime_ppk'] - gps_leap_offset, ppkGPS['lat_ppk'], 'g')

# Use the cerulean instantaneous bed detection since not sure about delay with smoothed
sonar_time = S1['time'] + ET2UTC  # DT.timedelta(hours=5)  # convert to UTC
print('warning yellowfin computer time is not on UTC!!!!!! conversion assumes rigid offset')
sonar_range = S1['this_ping_depth_m']
smooth_sonar_range = S1['smooth_depth_m']

# plot ALLLL data
plt.figure(figsize=(16, 4))
plt.plot(sonar_time, sonar_range, 'b.', label='sonar instant depth')
# plt.plot(sonar_time, smooth_sonar_range, 'r.')
plt.plot(GPS['gps_time'], GPS['altMSL'], '.g', label='L1 GPS elev (MSL)')
ppk_gpstime = ppkGPS['datetime'].apply(lambda x: x.timestamp()) - 18 # seconds -- not in datetime as gps_leap_offset is
plt.plot(ppk_gpstime, ppkGPS['height'] + 40, '.r', label=' ppk GPS elipsoid (+40 for scale)')
plt.ylim([0, 20])
plt.legend()

print('need good way to identify indicies of interest')

# plot sonar and zoomed in
plt.figure(figsize=(18,4))
plt.subplot(211)
plt.title('all data, select start/end point for measured depths\nadd extra time for PPK offset')
plt.plot(sonar_range)
d = plt.ginput(2)
plt.subplot(212)
sonarIndicies = np.arange(np.floor(d[0][0]).astype(int), np.ceil(d[1][0]).astype(int))  # using ginput to select these
# points
plt.plot(sonar_range[sonarIndicies])
plt.title('my selected data to proceed with')
plt.tight_layout()

# now identify corresponding times from ppk GPS.
indsp = np.where((ppk_gpstime >= sonar_time[sonarIndicies[0]]) & (ppk_gpstime <= sonar_time[sonarIndicies[-1]]))

# Interpolate sonar_range_i and GPS data
sonar_range_i = interp1d(sonar_time, sonar_range)(GPS['pc_time_gga'][sonarIndicies])
lati = GPS['lat'][sonarIndicies]
loni = GPS['lon'][sonarIndicies]

plt.figure(40)
ws = np.arange(2100, 2400)  # pick a nice section with heave effects visible in the echodata and GPS
ws2 = np.arange(2000, 2500)
csonar_range_i = sonar_range_i.copy()
csonar_range_i[ws] = csonar_range_i[ws] + 0.3 * np.sin(ws / 10)

#sdhc=detrend(chc(ws2)+.3*sin(ws2/10+shift)','const')

ssr = np.polyfit(ws2, csonar_range_i[ws2], 0)[0] + 0.3 * np.sin(ws2 / 10)
plt.subplot(412)
plt.plot(sdhc)
plt.hold(True)
plt.plot(ssr)

chc = ppkGPS['height'][indsp]
shift = 0 * np.pi / 4
chc[ws] = chc[ws] + 0.3 * np.sin(ws / 10 + shift)

sdhc = np.polyfit(ws2, chc[ws2] + 0.3 * np.sin(ws2 / 10 + shift), 0)[0]
plt.subplot(411)
plt.plot(csonar_range_i)
plt.hold(True)
plt.plot(chc)

plt.subplot(413)
r = np.correlate(ssr, sdhc, mode='full')
lags = np.arange(-200, 201)
plt.plot(lags, r)

mx, mi = np.max(r), np.argmax(r)
ml = lags[mi]
s_ssr = np.interp(np.arange(len(ssr)), np.arange(len(ssr)) + ml, ssr)
shifted_sonar_range_i = np.interp(np.arange(len(sonar_range_i)), np.arange(len(sonar_range_i)) + ml, sonar_range_i)

plt.subplot(414)
plt.plot(sdhc)
plt.hold(True)
plt.plot(s_ssr)

plt.figure(4)
plt.scatter(loni, lati, 16, sonar_range_i)
cc = plt.get_cmap('turbo')
cc = cc.reversed()
plt.colormap(cc)
plt.colorbar()
plt.clim(7, 13)

antenna_offset = 0.25
x = loni.flatten()
y = lati.flatten()
z = -sonar_range_i.flatten() + PPKGPS['height_ell_ppk'][indsp].flatten() - antenna_offset
dx = 0.000005
xnodes = np.arange(np.min(x) - dx, np.max(x) + dx, dx)
ynodes = np.arange(np.min(y) - dx, np.max(y) + dx, dx)
sff = 2e-04

# Perform the RegularizeData3D operation (needs to be implemented separately)
def RegularizeData3D(x, y, z, xnodes, ynodes, smoothness):
  # Implement the RegularizeData3D operation here
  pass

Zg3, Xg3, Yg3 = RegularizeData3D(x, y, z, xnodes, ynodes, sff)

plt.figure(22)
plt.scatter3D(x, y, z, 12, z, cmap='turbo')
plt.view_init(elev=0, azim=0)
plt.hold(True)
k = np.convex_hull(x, y, z)
plt.plot_trisurf(x[k], y[k], z[k], color='k', linewidth=3)

[m, n] = Zg3.shape
BW = plt.roipoly(Xg3[0, :], Yg3[:, 0], Zg3, x[k], y[k])
BW = np.array(BW, dtype=float)
BW[BW == 0] = np.nan

# Use GRIDobj to represent DEM (needs to be implemented separately)
class GRIDobj:
  def __init__(self, Xg, Yg, Zg):
    self.Xg = Xg
    self.Yg = Yg
    self.Zg = Zg
  
  # Implement other methods as required


DEM = GRIDobj(Xg3, Yg3, Zg3 * BW)
plt.gca().set_aspect('equal', adjustable='box')

plt.figure(31)
cm = plt.get_cmap('broc')
wgsz = 32
dataMax = -1 - wgsz
dataMin = -14 - wgsz
centerPoint = -10 - wgsz
scalingIntensity = 4
xm = np.arange(1, 513)
xm = xm - (centerPoint - dataMin) * len(xm) / (dataMax - dataMin)
xm = scalingIntensity * xm / np.max(np.abs(xm))
xm = np.sign(xm) * np.exp(np.abs(xm))
xm = xm - np.min(xm)
xm = xm * 511 / np.max(xm) + 1
ncm = np.interp(np.arange(1, 513), xm, cm)

# Use tanakacontour function (needs to be implemented separately)
def tanakacontour(DEM, levels):
  # Implement the tanakacontour function here
  pass

tanakacontour(DEM, np.arange(-14, -2, 0.25) - wgsz)
plt.title('Yellow Fin survey')
plt.hold(True)
sf = 10
hs = plt.scatter(x[::sf], y[::sf], 12, z[::sf], 'o', edgecolors='k')
hc = plt.colorbar()
hc.set_label('Depth (m)')
plt.xlabel('Lon (Deg)')
plt.ylabel('Lat (Deg)')
plt.show()
plt.savefig('goodwill_pond.png')
