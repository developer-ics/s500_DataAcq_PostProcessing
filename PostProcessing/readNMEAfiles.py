import os
import re
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

## code converted from matlab to python on 19 feb 2023 by ChatGPT
#Note that the above code uses NumPy and Matplotlib libraries to perform the same operations as the MATLAB code.
# Also, the output format of the data is changed to a NumPy .npz file instead of a MATLAB .mat file.
# You can modify the output format based on your requirements.
dirstr = os.path.join('SampleData', '01-05-2023n')
verbose = True
dd = [f for f in os.listdir(dirstr) if f.endswith('.dat')]
# for ii, name in enumerate(dd, start=1):
#     print(f'{ii} {name}')

ji = 0
gps_time, lat, lon, altWGS84, altMSL, pc_time_gga = [], [], [], [], [], []
gps_time, lat, latHemi, lon, lonHemi, fixQuality, satCount, HDOP =  [] , [], [] ,[], [], [], [], []
elevationMSL, eleUnits, geoSep, geoSepUnits, ageDiffGPS, diffRefStation = [], [], [], [], [], []
for fi in range(1, len(dd)):
    file_path = os.path.join(dirstr, dd[fi])
    
    if verbose: print(file_path)

    with open(file_path, 'r') as f:
        lns = f.readlines()
    
    for ln in lns:
        if ln.strip():
            try:
                ss = ln.split('$')
                datestring = ss[0].strip('#')
                stringNMEA = ss[1].split(',')
            except IndexError:
                continue
            
            dt = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S.%f')
            nmcode = stringNMEA[0]
        
            
            if nmcode == 'GNGGA' and len(stringNMEA[2]) > 1:
                # Sentence Identifier: This field identifies the type of NMEA sentence and is represented by "$GPGGA" for the GGA sentence.
                # 1. UTC Time: This field provides the time in hours, minutes, and seconds in UTC.
                # 2. Latitude: This field represents the latitude of the GPS fix in degrees and minutes, in the format of
                #     ddmm.mmmm, where dd denotes degrees and mm.mmmm denotes minutes.
                # 3. Latitude Hemisphere: This field indicates the hemisphere of the latitude, either "N" for North or "S" for South.
                # 4. Longitude: This field represents the longitude of the GPS fix in degrees and minutes, in the format
                # of dddmm.mmmm, where ddd denotes degrees and mm.mmmm denotes minutes.
                # 5. Longitude Hemisphere: This field indicates the hemisphere of the longitude, either "E" for East or "W" for West.
                # 6. GPS Fix Quality: This field provides information about the quality of the GPS fix, represented by a
                # numeric value. Common values include 0 for no fix, 1 for GPS fix, and 2 for Differential GPS (DGPS) fix.
                # 7. Number of Satellites in Use: This field indicates the number of satellites used in the GPS fix represented by a numeric value.
                # 8. Horizontal Dilution of Precision (HDOP): This field represents the HDOP, which is a measure of the
                # horizontal accuracy of the GPS fix, represented by a numeric value.
                # 9 Altitude: This field provides the altitude above mean sea level (MSL) in meters, represented by a numeric value.
                # 10 Altitude Units: This field indicates the units used for altitude, typically "M" for meters.
                # 11 Geoidal Separation: This field represents the geoidal separation, which is the difference between
                # the WGS84 ellipsoid and mean sea level, in meters, represented by a numeric value.
                # 12Geoidal Separation Units: This field indicates the units used for geoidal separation, typically "M" for meters.
                # 13 Age of Differential GPS Data: This field provides the age of the DGPS data used in the GPS fix, represented by a numeric value.
                # 14 Differential Reference Station ID: This field indicates the identification number of the DGPS
                # reference station used in the GPS fix, represented by a numeric value.
                #
                # parse the individual string, add to list
                pc_time_gga.append(dt)
                gps_time.append(float(stringNMEA[1]))
                lat.append(float(stringNMEA[2][:2]) + float(stringNMEA[2][2:])/60)
                latHemi.append(stringNMEA[3])
                lona = float(stringNMEA[4][:3]) + float(stringNMEA[4][2:])/60
                lonHemi.append(stringNMEA[5])
                if lonHemi == 'W': lona = -lona
                lon.append(lona)
                fixQuality.append(int(stringNMEA[6])) # GPS Fix Quality: represented by anumeric value. Common values
                # include 0 for no fix, 1 for GPS fix, and 2 for Differential GPS (DGPS) fix.
                satCount.append(int(stringNMEA[7]))
                HDOP.append(float(stringNMEA[8])) #measure of the horizontal accuracy of the GPS fix, represented
                # by a numeric value.
                altMSL.append(float(stringNMEA[9]))
                eleUnits.append(stringNMEA[10])
                geoSep.append(float(stringNMEA[11]))
                geoSepUnits.append(stringNMEA[12])
                ageDiffGPS.append(float(stringNMEA[13]))
                diffRefStation.append(stringNMEA[14].strip())
                
lat = np.array(lat)
lon = np.array(lon)
lat[lat == 0] = np.nan
lon[lon == 0] = np.nan

# now plot data
plt.figure(10)
plt.plot(lon, lat, 'o-')
plt.figure()
#plt.plot(pc_time_gga, altWGS84, '.-')
plt.plot(pc_time_gga, geoSep, label='geoSep')
plt.plot(pc_time_gga, altMSL, '.-', label='altMSL')
# save data
outname = f'nmea{dirstr[3:-1]}'
np.savez(outname, pc_time_gga=pc_time_gga, gps_time=gps_time, lat=lat, lon=lon, altMSL=altMSL, altWGS84=geoSep)

