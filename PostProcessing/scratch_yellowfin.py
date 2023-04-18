import os
import struct
from datetime import datetime
from datetime import timedelta
import matplotlib
matplotlib.use('Agg')
import cv2
from matplotlib import pyplot as plt
import numpy as np
import glob
import h5py
import tqdm
import netCDF4 as nc

def loadSonar_s500_binary(dataPath, outfname = 'myfile.h5'):
    """Loads and concatenates all of the binary files (*.dat) located in the dataPath location
    
    :param dataPath: search path for sonar data files
    :param outfname: string to save h5 file. If false it will skip this process. (Default = myfile.h5)
    :return:
    """
    dd = glob.glob(os.path.join(dataPath, "*.dat"))  # find dat files for sonar
    print(f'found {len(dd)} sonar files for procesing')# loop through files
    # https://docs.ceruleansonar.com/c/v/s-500-sounder/appendix-f-programming-api
    ij, i3 = 0, 0
    allocateSize = 50000
    # initialize variables for loop
    distance, confidence, transmit_duration = np.zeros(allocateSize),np.zeros(allocateSize),np.zeros(allocateSize) # [],
    ping_number, scan_start, scan_length = np.zeros(allocateSize), np.zeros(allocateSize), np.zeros(allocateSize)
    end_ping_hz, adc_sample_hz, timestamp_msec, spare2 = np.zeros(allocateSize), np.zeros(allocateSize), \
                                                         np.zeros(allocateSize), np.zeros(allocateSize)
    start_mm, length_mm, start_ping_hz = np.zeros(allocateSize), np.zeros(allocateSize), np.zeros(allocateSize),
    ping_duration_sec, analog_gain, profile_data_length, =  np.zeros(allocateSize), np.zeros(allocateSize), np.zeros(allocateSize)
    
    min_pwr, step_db, smooth_depth_m, fspare2 = np.zeros(allocateSize), np.zeros(allocateSize), \
                                                np.zeros(allocateSize),  np.zeros(allocateSize)
    is_db, gain_index, power_results = np.zeros(allocateSize), np.zeros(allocateSize), np.zeros(allocateSize)
    max_pwr, num_results  =  np.zeros(allocateSize), np.zeros(allocateSize, dtype=int)
    gain_setting,  decimation, reserved = np.zeros(allocateSize), np.zeros(allocateSize), np.zeros(allocateSize),
    # these are complicated preallocations
    txt, dt_profile, dt_txt, dt = np.zeros(allocateSize, dtype=object), np.zeros(allocateSize, dtype=object), \
                                  np.zeros(allocateSize, dtype=object), np.zeros(allocateSize, dtype=object)
    rangev = np.zeros((allocateSize, 100000))
    profile_data = np.zeros((allocateSize, allocateSize))
    for fi in tqdm.tqdm(sonarRange(len(dd))):
        with open(dd[fi], 'rb') as fid:
            fname = dd[fi]
            print(f'processing {fname}')
            xx = fid.read()
            st = [i + 1 for i in sonarRange(len(xx)) if xx[i:i + 2] == b'BR']
            # initalize variables for loop
            packet_len, packet_id = np.zeros(len(st)), np.zeros(len(st))
            for ii in sonarRange(len(st) - 1):
                fid.seek(st[ii] + 1, os.SEEK_SET)
                datestring = fid.read(26).decode('utf-8', 'replace')  # 'replace' causes a replacement marker (such as '?')
                                                                        # to be inserted where there is malformed data.
                try:
                    dt[ii] = datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S.%f')
                except:
                    continue
                packet_len[ii] = struct.unpack('<H', fid.read(2))[0]
                packet_id[ii] = struct.unpack('<H', fid.read(2))[0]
                r1 = struct.unpack('<B', fid.read(1))[0]
                r2 = struct.unpack('<B', fid.read(1))[0]
                if packet_id[ii] == 1300:
                    distance[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    confidence[ij] = struct.unpack('<H', fid.read(2))[0]  # mm
                    transmit_duration[ij] = struct.unpack('<H', fid.read(2))[0]  # us
                    ping_number[ij] = struct.unpack('<I', fid.read(4))[0]  # #
                    scan_start[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    scan_length[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    gain_setting[ij] = struct.unpack('<I', fid.read(4))[0]
                    profile_data_length[ij] = struct.unpack('<I', fid.read(4))[0]
                    for jj in sonarRange(200):
                        tmp = struct.unpack('<B', fid.read(1))[0]
                        if tmp:
                            profile_data[ij, jj] = tmp
                    ij += 1
    
                if packet_id[ii] == 3:
                    txt[ij] = fid.read(int(packet_len[ii])).decode('utf-8')
                    dt_txt[ij] = dt
                if packet_id[ii] == 1308:
                    dtp = dt
                    #https://docs.ceruleansonar.com/c/v/s-500-sounder/appendix-f-programming-api#ping-response-packets
                    ping_number[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    start_mm[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    length_mm[ij] = struct.unpack('<I', fid.read(4))[0]  # mm
                    start_ping_hz[ij] = struct.unpack('<I', fid.read(4))[0]  # us
                    end_ping_hz[ij] = struct.unpack('<I', fid.read(4))[0]  # #
                    adc_sample_hz[ij]= struct.unpack('<I', fid.read(4))[0]  # mm
                    timestamp_msec[ij] = struct.unpack('I', fid.read(4))[0]
                    spare2[ij] = struct.unpack('I', fid.read(4))[0]
                    
                    ping_duration_sec[ij] = struct.unpack('f', fid.read(4))[0]
                    analog_gain[ij] = struct.unpack('f', fid.read(4))[0]
                    max_pwr[ij] = struct.unpack('f', fid.read(4))[0]
                    min_pwr[ij] = struct.unpack('f', fid.read(4))[0]
                    step_db[ij] = struct.unpack('f', fid.read(4))[0]
                    smooth_depth_m[ij] = struct.unpack('f', fid.read(4))[0]
                    fspare2[ij] = struct.unpack('f', fid.read(4))[0]
           
                    is_db[ij] = struct.unpack('B', fid.read(1))[0]
                    gain_index[ij] = struct.unpack('B', fid.read(1))[0]
                    decimation[ij] = struct.unpack('B', fid.read(1))[0]
                    reserved[ij] = struct.unpack('B', fid.read(1))[0]
                    num_results[ij] = struct.unpack('H', fid.read(2))[0]
                    power_results[ij] = struct.unpack('H', fid.read(2))[0]
                    rangev[ij,0:num_results[ij]] = np.linspace(start_mm[ij], start_mm[ij] + length_mm[ij], num_results[ij])
                    dt_profile[ij] = dt[ii] # assign datetime from data written
                    # profile_data_single = [] #= np.empty((num_results[-1], ), dtype=np.uint16)
                    for jj in sonarRange(num_results[ij]):
                        # print(jj)
                        read = fid.read(2)
                        if read:
                            try: # data should be unsigned short
                                tmp = struct.unpack('<H', read)[0]
                            except: # when it's unsigned character
                                tmp = struct.unpack('B', read)[0]
                            if tmp:
                                profile_data[ij, jj] = tmp
                    ij += 1
    
    # clean up array's from over allocation to free up memory and data
    idxShort = np.argwhere(timestamp_msec!=0).max() # identify index for end of data to keep
    smooth_depth_m = smooth_depth_m[:idxShort]
    reserved = reserved[:idxShort]
    num_results = num_results[:idxShort]
    start_mm = start_mm[:idxShort]
    length_mm = length_mm[:idxShort]
    start_ping_hz = start_ping_hz[:idxShort]
    end_ping_hz = end_ping_hz[:idxShort]
    adc_sample_hz = adc_sample_hz[:idxShort]
    timestamp_msec = timestamp_msec[:idxShort]
    spare2 = spare2[:idxShort]
    ping_duration_sec = ping_duration_sec[:idxShort]
    analog_gain = analog_gain[:idxShort]
    max_pwr = max_pwr[:idxShort]
    min_pwr = min_pwr[:idxShort]
    step_db = step_db[:idxShort]
    fspare2 = fspare2[:idxShort]
    is_db = is_db[:idxShort]
    gain_index = gain_index[:idxShort]
    decimation = decimation[:idxShort]
    dt_profile = dt_profile[:idxShort]

    #rangev,  profile_data (maybe others) need to be handled
    rangev = rangev[:idxShort, :np.median(num_results).astype(int)]
    profile_data = profile_data[:idxShort, :np.median(num_results).astype(int)].T
    
    # now save output file
    with h5py.File(outfname, 'w') as hf:
        hf.create_dataset('min_pwr', data=min_pwr)
        hf.create_dataset('ping_duration', data=ping_duration_sec)
        hf.create_dataset('time', data=nc.date2num(dt_profile, 'seconds since 1970-01-01'))
        hf.create_dataset('smooth_depth_m', data=smooth_depth_m)
        hf.create_dataset('profile_data', data=profile_data.T) # putting time as first axis
        hf.create_dataset('num_results', data=num_results)
        hf.create_dataset('start_mm', data=start_mm)
        hf.create_dataset('length_mm', data=length_mm)
        hf.create_dataset('start_ping_hz', data=start_ping_hz)
        hf.create_dataset('end_ping_hz', data=end_ping_hz)
        hf.create_dataset('adc_sample_hz', data=adc_sample_hz)
        hf.create_dataset('timestamp_msec', data=timestamp_msec)
        hf.create_dataset('analog_gain', data=analog_gain)
        hf.create_dataset('max_pwr', data=max_pwr)
        hf.create_dataset('this_ping_depth_m', data=step_db)
        hf.create_dataset('this_ping_depth_measurement_confidence', data=is_db)
        hf.create_dataset('smoothed_depth_measurement_confidence', data=reserved)
        hf.create_dataset('gain_index', data=gain_index)
        hf.create_dataset('decimation', data=decimation)
        hf.create_dataset('range_m', data=rangev/1000)
        
def loadSonarH5(fname):
    """Loads already created H5 file from the sonar data. """
    hf = h5py.File(fname, 'r')
    dataOut = {}
    for key in hf.keys():
        dataOut[key] = np.array(hf.get(key))
    return dataOut
def plot_single_backscatterProfile(fname, time, sonarRange, profile_data, this_ping_depth_m, smooth_depth_m, index):
    """Create's a plot that shows full backscatter and individual profile  with identified depths
    
    :param fname:
    :param time:
    :param sonarRange:
    :param profile_data:
    :param this_ping_depth_m:
    :param smooth_depth_m:
    :param index:
    :return:
    """
    plt.figure(figsize=(12,8))
    ax1 = plt.subplot2grid((4,4), (0,1), colspan=3, rowspan=4)
    backscatter = ax1.pcolormesh(time, sonarRange[0], profile_data.T, shading='auto')
    ax1.plot(time, this_ping_depth_m, color='black', ms=0.1, label='instant depth', alpha=0.5)
    # ax1.plot(time, smooth_depth_m, 'black', ms=1, label='Smooth Depth')
    ax1.plot(time[index], smooth_depth_m[index], ms=15, marker='X', color='red')
    cbar = plt.colorbar(mappable=backscatter, ax=ax1)
    cbar.set_label('backscatter value')
    ax1.set_ylim([0,5])
    
    ax2 = plt.subplot2grid((4,4), (0,0), rowspan=4, sharey=ax1)
    ax2.plot(profile_data[index], sonarRange[0], alpha=1)
    ax2.plot(profile_data[index, np.argmin(np.abs(sonarRange[index] - this_ping_depth_m[index]))], this_ping_depth_m[
        index],'grey', marker='X', ms=10, label='this ping')
    ax2.plot(profile_data[index, np.argmin(np.abs(sonarRange[index] - smooth_depth_m[index]))], smooth_depth_m[index], \
             'black', marker='X', ms=10, label='smoothed bottom')
    ax2.legend()
    
    for ii in range(5):
        ax2.plot(profile_data[index-ii], sonarRange[0], alpha=.4 - ii * .07, color='k')
    ax2.set_ylabel('depth [m]')
    plt.tight_layout()
    plt.savefig(fname)
    plt.close()

fpath = '/data/yellowfin/20230327/s500'
sonarH5 ='/data/yellowfin/20230327/20230327_sonarRaw.h5'
# loadSonar_s500_binary(fpath, outfname=sonarH5)
sonarData = loadSonarH5(sonarH5)

# unpack loaded sonar data
time = nc.num2date(sonarData['time'], 'seconds since 1970-01-01', only_use_cftime_datetimes=False,
                   only_use_python_datetimes=True) #nc.num2date(sonarData['time'], 'seconds since 1970-01-01')
subset = np.argwhere((time > datetime(2023, 3, 27, 14, 40)) & (time < datetime(2023, 3, 27, 15))).squeeze()
time = time[subset]
profile_data = sonarData['profile_data'][:, subset].T
smooth_depth_m = sonarData['smooth_depth_m'][subset]
smooth_depth_confidence = sonarData['smoothed_depth_measurement_confidence'][subset]
this_ping_depth_m = sonarData['this_ping_depth_m'][subset]
this_ping_depth_confidence = sonarData['this_ping_depth_measurement_confidence'][subset]
analog_gain = sonarData['analog_gain'][subset]
sonarRange = sonarData['range_m'][subset, :]
# subset data to interesting
for i in tqdm.tqdm(range(len(time))):
    fname = f'/data/yellowfin/20230327/figures/sonar_{time[i].strftime("%Y%m%dT%H%M%S.%f")}.png'
    plot_single_backscatterProfile(fname, time, sonarRange, profile_data, this_ping_depth_m, smooth_depth_m, index=i)

# plotting figures
i = 3000


plt.gca().invert_yaxis()
plt.ylabel('Depth (m)')
plt.xlabel('Time (hh:mm)')
plt.plot(dt_profile, smooth_depth_m, '.k', ms=3)
plt.savefig(f'profile_data_{datestring}_python.png')

# Filtering and bed detection
filt_prof_data = cv2.blur(profile_data.copy(), ksize=(13,13)) ## couldn't find a hybrid median filter,ldata.erdc.dren.mil/
# used a bluring filter

plt.figure(5)
plt.pcolormesh(dt_profile, rangev[2] / 1000, filt_prof_data.T, shading='auto')
plt.plot(dt_profile, smooth_depth_m, '.k', ms=3)
plt.title('filtered version of profile plot')
plt.ylabel('Depth (m)')
plt.ylim([0,12])
plt.xlabel('Time (hh:mm)')
plt.colorbar()
plt.tight_layout()
plt.savefig(f'profile_data_{datestring}_Cleaned_python.png')

# plt.gca().invert_yaxis()

# spicer stopped conversion here as smooth depth provided by manufacturer looked good enough compared to below
# filtering.  Nothing further was tested, but inital conversion from chatGPT provided for anyone who want's to proceed.
#
# blank = 100
# thr = np.percentile(filt_prof_data[blank:, :], 90, axis=0)
# [m, n] = filt_prof_data.shape
# bed_detect_ind = np.zeros((n,))
# for ii in range(n):
#     tmp = np.argmax(cv2.filter2D(filt_prof_data[blank:, ii],ddepth=-1, kernel=np.ones((10, 1)) / 10) > thr[ii])
#     if tmp.size > 0:
#         bed_detect_ind[ii] = tmp
#     else:
#         bed_detect_ind[ii] = 0
#
# plt.figure(50)
# plt.imshow(imfilter(filt_prof_data, np.ones((10, 1)) / 10) > np.mean(thr), aspect='auto', origin='lower')
# plt.plot(bed_detect_ind + blank, 'r')
#
# plt.figure(5)
# plt.hold(True)
# bed_detect_range = rangev[2][bed_detect_ind + blank] / 1000
# plt.plot(timestamp_msec / 1000 - timestamp_msec[0] / 1000, bed_detect_range, 'r')
