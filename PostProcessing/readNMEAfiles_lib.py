import os
from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt
import glob
import tqdm
import h5py
import datetime as DT


## code converted from matlab to python on 19 feb 2023 by ChatGPT
# Note that the above code uses NumPy and Matplotlib libraries to perform the same operations as the MATLAB code.
# Also, the output format of the data is changed to a NumPy .npz file instead of a MATLAB .mat file.
# You can modify the output format based on your requirements.
def mLabDatetime_to_epoch(dt):
    """Convert matlab datetime to unix Epoch time"""
    epoch = datetime(1970, 1, 1)
    delta = dt - epoch
    return delta.total_seconds()


def load_yellowfin_NMEA_files(fpath, saveFname, plotfname=False, verbose=False):
    """loads and possibly plots NMEA data from Emlid Reach M2 on yellowin
    
    :param fpath: location to search for NMEA data files
    :param saveFname: where to save the Hdf5 file
    :param plotfname: where to save plot showing path of yellowfin, if False, will not plot (default=False)
    :param verbose: will print more output when processing if True (default=False)
    :return:
    """
    dd = glob.glob(os.path.join(fpath, '*.dat'))
    if verbose: print(f'processing {len(dd)} GPS data files')
    
    ji = 0
    gps_time, lat, lon, altWGS84, altMSL, pc_time_gga = [], [], [], [], [], []
    gps_time, lat, latHemi, lon, lonHemi, fixQuality, satCount, HDOP = [], [], [], [], [], [], [], []
    elevationMSL, eleUnits, geoSep, geoSepUnits, ageDiffGPS, diffRefStation = [], [], [], [], [], []
    for fi in tqdm.tqdm(range(1, len(dd))):
        fname = dd[fi]
        
        if verbose: print(fname)
        
        with open(fname, 'r') as f:
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
                    lat.append(float(stringNMEA[2][:2]) + float(stringNMEA[2][2:]) / 60)
                    latHemi.append(stringNMEA[3])
                    lona = float(stringNMEA[4][:3]) + float(stringNMEA[4][2:]) / 60
                    lonHemi.append(stringNMEA[5])
                    if lonHemi == 'W': lona = -lona
                    lon.append(lona)
                    fixQuality.append(
                        int(stringNMEA[6]))  # GPS Fix Quality: represented by anumeric value. Common values
                    # include 0 for no fix, 1 for GPS fix, and 2 for Differential GPS (DGPS) fix.
                    satCount.append(int(stringNMEA[7]))
                    HDOP.append(float(stringNMEA[8]))  # measure of the horizontal accuracy of the GPS fix, represented
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
    # convert datetimes to epochs for file writing.
    gpstimeobjs = [DT.time(int(str(ii)[:2]), int(str(ii)[2:4]), int(str(ii)[4:6]), int(str(ii)[7:] + '00000')) for ii in
                   gps_time]
    aa = [DT.datetime.combine(pc_time_gga[ii].date(), gpstimeobjs[ii]) for ii in range(len(gpstimeobjs))]
    # now save output file
    with h5py.File(saveFname, 'w') as hf:
        hf.create_dataset('lat', data=lat)
        # hf.create_dataset('latHemi', data=latHemi)
        hf.create_dataset('lon', data=lon)
        # hf.create_dataset('lonHemi',data=lonHemi)
        hf.create_dataset('fixQuality', data=fixQuality)
        hf.create_dataset('satCount', data=satCount)
        hf.create_dataset('HDOP', data=HDOP)
        hf.create_dataset('pc_time_gga', data=[mLabDatetime_to_epoch(pc_time_gga[ii]) for ii in range(len(pc_time_gga))])
        hf.create_dataset('gps_time', data=[mLabDatetime_to_epoch(aa[i]) for i in range(len(aa))][0])
        hf.create_dataset('altMSL', data=altMSL)
        # hf.create_dataset('eleUnits', data=eleUnits) # putting time as first axis
        # hf.create_dataset('geoSepUnits', data=geoSepUnits)
        hf.create_dataset('ageDiffGPS', data=ageDiffGPS)
    # now plot data
    if plotfname is not False:
        plt.figure(figsize=(12, 4))
        plt.subplot(121)
        plt.plot(lon, lat, '-')
        plt.subplot(122)
        # plt.plot(pc_time_gga, altWGS84, '.-')
        # plt.plot(pc_time_gga, geoSep, label='geoSep')
        plt.plot(pc_time_gga, altMSL, '.-', label='altMSL')
        plt.savefig(plotfname)
        plt.close()

timeString = "20230327"
fpath = f'/data/yellowfin/{timeString}/nmeaData'  # load NMEA data from this location
saveFname = f'/data/yellowfin/{timeString}/{timeString}_gnss_raw.h5'  # save nmea data to this location
load_yellowfin_NMEA_files(fpath, saveFname=saveFname,
                          plotfname='/data/yellowfin/20230327/figures/GPSpath.png')