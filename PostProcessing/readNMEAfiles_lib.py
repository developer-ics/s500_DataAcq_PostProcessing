## code converted from matlab to python on 19 feb 2023 by ChatGPT
# Note that the above code uses NumPy and Matplotlib libraries to perform the same operations as the MATLAB code.
# Also, the output format of the data is changed to a NumPy .npz file instead of a MATLAB .mat file.
# You can modify the output format based on your requirements.
from PostProcessing.yellowfinLib import load_yellowfin_NMEA_files

timeString = "20230327"
fpath = f'/data/yellowfin/{timeString}/nmeaData'  # load NMEA data from this location
saveFname = f'/data/yellowfin/{timeString}/{timeString}_gnssRaw.h5'  # save nmea data to this location
load_yellowfin_NMEA_files(fpath, saveFname=saveFname,
                          plotfname='/data/yellowfin/20230327/figures/GPSpath.png')