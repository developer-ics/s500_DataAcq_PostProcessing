import os
import re
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

## code converted from matlab to python on 19 feb 2023 by ChatGPT
#Note that the above code uses NumPy and Matplotlib libraries to perform the same operations as the MATLAB code. Also, the output format of the data is changed to a NumPy .npz file instead of a MATLAB .mat file. You can modify the output format based on your requirements.

dirstr = '.\\01-11-2023\\'
dirstr = '.\\01-05-2023\\'

dd = [f for f in os.listdir(dirstr) if f.endswith('.dat')]
for ii, name in enumerate(dd, start=1):
    print(f'{ii} {name}')

ji = 0
gps_time, lat, lon, altWGS84, altMSL, pc_time_gga = [], [], [], [], [], []

for fi in range(1, len(dd)):
    file_path = os.path.join(dirstr, dd[fi])
    print(file_path)

    with open(file_path, 'r') as f:
        lns = f.readlines()

    for ln in lns:
        if ln.strip():
            datestring = ln[3:28]
            dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S.%f')
            nmcode = ln[30:35]

            if nmcode == 'GNGGA':
                ji += 1
                Str = ln[29:]
                str1 = re.sub('[,;=]', ' ', Str)
                str2 = re.sub('[^- 0-9.eE(,)/]', '', str1)
                str3 = re.sub('\.\s|\E\s|\e\s|\s\E|\s\e', ' ', str2)
                str4 = re.sub('E', '', str3)
                numArray = np.fromstring(str4, sep=' ')

                if len(numArray) >= 3:
                    gps_time.append(numArray[0])
                    lat.append(np.floor(numArray[1] / 100) + (numArray[1] - np.floor(numArray[1] / 100) * 100) / 60)
                    lon.append(-np.floor(numArray[2] / 100) - (numArray[2] - np.floor(numArray[2] / 100) * 100) / 60)
                    altWGS84.append(numArray[7])
                    altMSL.append(numArray[6])
                    pc_time_gga.append(dt)

lat = np.array(lat)
lon = np.array(lon)
lat[lat == 0] = np.nan
lon[lon == 0] = np.nan

plt.figure(10)
plt.clf()
plt.plot(lon, lat, 'o-')

plt.figure(11)
plt.clf()
plt.plot(pc_time_gga, altWGS84, '.-')
plt.plot(pc_time_gga, altMSL, '.-')

outname = f'nmea{dirstr[3:-1]}'
np.savez(outname, pc_time_gga=pc_time_gga, gps_time=gps_time, lat=lat, lon=lon, altMSL=altMSL, altWGS84=altWGS84)

