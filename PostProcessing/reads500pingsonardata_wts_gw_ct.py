import os
import struct
from datetime import datetime
from matplotlib import pyplot as plt
import numpy as np
# dirstr = '01-11-2023'  # a small grid of goodwill pond in falmouth
# dirstr = '12-21-2022'  # with emlid ppk GPS saved and processed
dirstr = '01-05-2023'  # alos with emlid ppk GPS saved and processed

dd = os.listdir(os.path.join('SampleData', dirstr))  # find dat files for sonar
# loop through files
# for ii in range(len(dd)):
#     print(str(ii + 1) + ' ' + dd[ii])
#
# https://docs.ceruleansonar.com/c/v/s-500-sounder/appendix-f-programming-api
ij, i3 = 0, 0
# initialize variables for loop
distance, confidence, transmit_duration, ping_number, scan_start, scan_length = [], [], [], [], [], []
start_mm, length_mm, start_ping_hz, end_ping_hz, adc_sample_hz, timestamp_msec, spare2 = [], [], [], [], [], [], []
ping_duration_sec, analog_gain, profile_data_length, txt, dt_txt, dt = [], [], [], [], [], []
min_pwr, step_db, smooth_depth_m, fspare2, is_db, gain_index, profile_data = [], [], [], [], [], [], []
max_pwr, num_results, rangev, gain_setting, dt_profile, decimation, reserved = [], [], [], [], [], [], []
for fi in range(len(dd)):
    with open(os.path.join('SampleData', dirstr, dd[fi]), 'rb') as fid:
        xx = fid.read()
        st = [i + 1 for i in range(len(xx)) if xx[i:i+2] == b'BR']
        # initalize variables for loop
        packet_len, packet_id = np.zeros(len(st)), np.zeros(len(st))
        for ii in range(len(st)-1):
            fid.seek(st[ii] + 1, os.SEEK_SET)
            datestring = fid.read(26).decode('utf-8', 'replace')  # 'replace' causes a replacement marker (such as '?')
                                                                    # to be inserted where there is malformed data.
            try:
                dt.append(datetime.strptime(datestring, '%Y-%m-%d %H:%M:%S.%f'))
            except:
                continue
            packet_len[ii] = struct.unpack('<H', fid.read(2))[0]
            packet_id[ii] = struct.unpack('<H', fid.read(2))[0]
            r1 = struct.unpack('<B', fid.read(1))[0]
            r2 = struct.unpack('<B', fid.read(1))[0]
            if packet_id[ii] == 1300:
                ij += 1
                distance.append(struct.unpack('<I', fid.read(4))[0])  # mm
                confidence.append(struct.unpack('<H', fid.read(2))[0])  # mm
                transmit_duration.append(struct.unpack('<H', fid.read(2))[0])  # us
                ping_number.append(struct.unpack('<I', fid.read(4))[0])  # #
                scan_start.append(struct.unpack('<I', fid.read(4))[0])  # mm
                scan_length.append(struct.unpack('<I', fid.read(4))[0])  # mm
                gain_setting.append(struct.unpack('<I', fid.read(4))[0])
                profile_data_length.append(struct.unpack('<I', fid.read(4))[0])
                for jj in range(200):
                    tmp = struct.unpack('<B', fid.read(1))[0]
                    if tmp:
                        profile_data[ij, jj] = tmp
            if packet_id[ii] == 3:
                txt.append(fid.read(int(packet_len[ii])).decode('utf-8'))
                dt_txt.append(dt)
            if packet_id[ii] == 1308:
                ij += 1
                
                dtp = dt
                #https://docs.ceruleansonar.com/c/v/s-500-sounder/appendix-f-programming-api#ping-response-packets
                ping_number.append(struct.unpack('<I', fid.read(4))[0])  # mm
                
                start_mm.append(struct.unpack('<I', fid.read(4))[0])  # mm
                length_mm.append(struct.unpack('<I', fid.read(4))[0])  # mm
                start_ping_hz.append(struct.unpack('<I', fid.read(4))[0])  # us
                end_ping_hz.append(struct.unpack('<I', fid.read(4))[0])  # #
                adc_sample_hz.append(struct.unpack('<I', fid.read(4))[0])  # mm
                timestamp_msec.append(struct.unpack('I', fid.read(4))[0])
                spare2.append(struct.unpack('I', fid.read(4))[0])
                
                ping_duration_sec.append(struct.unpack('f', fid.read(4))[0])
                analog_gain.append(struct.unpack('f', fid.read(4))[0])
                max_pwr.append(struct.unpack('f', fid.read(4))[0])
                min_pwr.append(struct.unpack('f', fid.read(4))[0])
                step_db.append(struct.unpack('f', fid.read(4))[0])
                smooth_depth_m.append(struct.unpack('f', fid.read(4))[0])
                fspare2.append(struct.unpack('f', fid.read(4))[0])
       
                is_db.append(struct.unpack('B', fid.read(1))[0])
                gain_index.append(struct.unpack('B', fid.read(1))[0])
                decimation.append(struct.unpack('B', fid.read(1))[0])
                reserved.append(struct.unpack('B', fid.read(1))[0])
                num_results.append(struct.unpack('H', fid.read(2))[0])
                rangev.append(np.linspace(start_mm[-1], start_mm[-1] + length_mm[-1], num_results[-1]))
                print(ii)
                dt_profile.append(dt[ii])
                
                profile_data_single = [] #= np.empty((num_results[-1], ), dtype=np.uint16)
                for jj in range(num_results[-1]):
                    tmp = struct.unpack('<H', fid.read(2))[0]
                    if tmp:
                        profile_data_single.append(tmp)
                profile_data.append(profile_data_single)
# Plotting figures
plt.figure(1)
plt.clf()
plt.plot(smooth_depth_m, '.')
plt.ylim([0, 900])

plt.figure(4)
plt.clf()
plt.pcolor(dt_profile, rangev[2] / 1000, profile_data[0:len(timestamp_msec), 0:len(rangev[2])].T)
plt.shading = 'flat'
plt.colorbar()
plt.gca().invert_yaxis()
plt.ylabel('Depth (m)')
plt.xlabel('Time (hh:mm)')
plt.hold(True)
plt.plot(dt_profile - seconds(2.7), smooth_depth_m, '.k')
plt.savefig('profile_data.png')

# Filtering and bed detection
filt_prof_data = profile_data.T
filt_prof_data = hmf(filt_prof_data, 13)

plt.figure(5)
plt.clf()
plt.pcolor(timestamp_msec / 1000 - timestamp_msec[0] / 1000, rangev[2] / 1000,
           imfilter(filt_prof_data, np.ones((5, 1)) / 5).T)
plt.shading = 'flat'
plt.gca().invert_yaxis()

blank = 100
thr = np.percentile(filt_prof_data[blank:, :], 90, axis=0)
[m, n] = filt_prof_data.shape
bed_detect_ind = np.zeros((n,))
for ii in range(n):
    tmp = np.argmax(imfilter(filt_prof_data[blank:, ii], np.ones((10, 1)) / 10) > thr[ii])
    if tmp.size > 0:
        bed_detect_ind[ii] = tmp
    else:
        bed_detect_ind[ii] = 0

plt.figure(50)
plt.imshow(imfilter(filt_prof_data, np.ones((10, 1)) / 10) > np.mean(thr), aspect='auto', origin='lower')
plt.plot(bed_detect_ind + blank, 'r')

plt.figure(5)
plt.hold(True)
bed_detect_range = rangev[2][bed_detect_ind + blank] / 1000
plt.plot(timestamp_msec / 1000 - timestamp_msec[0] / 1000, bed_detect_range, 'r')

# Save data
# np.savez('profile_data.npz', dt_profile=dt_profile, range_bins=rangev[2] / 1000,
#          profile_int_matrix=profile_data.T, bed)
#########################################
# clear
# %dirstr='01-11-2023'%  a small gird of goodwil pond in falmouth
# dirstr='12-21-2022' % with emlid ppk GPS saved and processed
# dirstr='01-05-2023' % alos with emlid ppk GPS saved and processed
#
#
# if ispc
#     slash = '\';
# else
#     slash = '/';
# end
#
# dd=dir(['SampleData' slash dirstr slash '*.dat'])
# for ii=1:length(dd)
#     disp([num2str(ii) ' ' (dd(ii).name)])
# end
#
# %%
# ij=0;i3=0
# for fi=1:length(dd) %5  20201218-101925265.bin ios new 500 khz
#     ['.\' dirstr '\' dd(fi).name]
#     fid=fopen( ['.\' dirstr '\' dd(fi).name]);
#
#     frewind(fid);
#     xx=fread(fid,'uchar');
#     %char(xx')
#     st=findstr('BR',char(xx'));
#     %https://ceruleansonar.com/pages/cerulean-sounder-api
#
#     for ii=1:(length(st)-2)
#         %for ii=1:114
#
#         fseek(fid,st(ii)+1,-1);
#         datestring{ii}=fread(fid,26,'char');
#         try
#             dt(ii)=datetime(char(datestring{ii}'),'InputFormat','yyyy-MM-dd HH:mm:ss.SSSSSS');
#         catch
#             continue
#         end
#         packet_len(ii)=fread(fid,1,'uint16');
#         packet_id(ii)=fread(fid,1,'uint16');
#         r1=fread(fid,1,'uint8');
#         r2=fread(fid,1,'uint8');
#         if packet_id(ii)==1300
#             %  disp('pid=1300')
#             ij=ij+1;
#             distance(ij)=fread(fid,1,'uint32');%mm
#             confidence(ij)=fread(fid,1,'uint16');%mm
#             transmit_duration(ij)=fread(fid,1,'uint16');%us
#             ping_number(ij)=fread(fid,1,'uint32');%#
#             scan_start(ij)=fread(fid,1,'uint32');%mm
#             scan_length(ij)=fread(fid,1,'uint32');%mm
#             gain_setting(ij)=fread(fid,1,'uint32');%
#             profile_data_length(ij)=fread(fid,1,'uint32');%
#             %if profile_data_length(ij)<300
#             for jj=1:200
#                 tmp=fread(fid,1,'uint8');
#                 if ~isempty(tmp)
#                     profile_data(ij,jj)=tmp;
#                 end
#             end
#             %end
#         end
#         if packet_id(ii)==3
#
#             i3=i3+1;
#             txt{i3}=fread(fid, packet_len(ii),'char');%mm
#             dt_txt(i3)=dt(ii);
#         end
#         if packet_id(ii)==1308
#             % disp('pid=1308')
#             ij=ij+1;
#             dtp(ij)=dt(ii);
#             ping_number(ij)=fread(fid,1,'uint32');%mm
#
#             start_mm(ij)=fread(fid,1,'uint32');%mm
#             length_mm(ij)=fread(fid,1,'uint32');%mm
#             start_ping_hz(ij)=fread(fid,1,'uint32');%us
#             end_ping_hz(ij)=fread(fid,1,'uint32');%#
#             adc_sample_hz(ij)=fread(fid,1,'uint32');%mm
#             timestamp_msec(ij)=fread(fid,1,'uint32');%mm
#             spare2(ij)=fread(fid,1,'uint32');%mm
#
#             ping_duration_sec(ij)=fread(fid,1,'float');%
#             analog_gain(ij)=fread(fid,1,'float');%
#             max_pwr(ij)=fread(fid,1,'float');%
#             min_pwr(ij)=fread(fid,1,'float');%
#             step_db(ij)=fread(fid,1,'float');%
#             smooth_depth_m(ij)=fread(fid,1,'float');%
#             fspare2(ij)=fread(fid,1,'float');%
#             is_db(ij)=fread(fid,1,'uint8');%
#
#             gain_index(ij)=fread(fid,1,'uint8');%
#             decimation(ij)=fread(fid,1,'uint8');%
#             reserved(ij)=fread(fid,1,'uint8');%
#             num_results(ij)=fread(fid,1,'uint16');%
#             rangev{ij}=linspace( start_mm(ij),start_mm(ij)+length_mm(ij),num_results(ij));
#             dt_profile(ij)=dt(ii);
#             %if profile_data_length(ij)<300
#             for jj=1:   num_results(ij)
#                 tmp=fread(fid,1,'uint16');
#                 if ~isempty(tmp)
#                     profile_data(ij,jj)=tmp;
#                 end
#             end
#             %end
#         end
#
#     end
#     fclose('all')
# end
# if 0
#     %%
#     figure(1);clf
#     plot(distance,'.')
#     yaxis([ 0 900])
#
#     figure(2);clf
#     plot(ping_number,'.')
#     figure(3);clf
#     plot(packet_id,'.')
#     yaxis([0 2000])
#
#     %%
#     % figure(4);clf
#     % %pcolor(log10(profile_data'))
#     % pcolor(timestamp_msec/1000,rangev{1},log10(profile_data'))
#     %
#     % shading flat
#     % caxis([-3 4])
#     % colorbar
# end
#
# %%
# figure(1);clf
# plot(smooth_depth_m,'.')
# yaxis([ 0 900])
#
# figure(4);clf
# %  pcolor(timestamp_msec/1000-timestamp_msec(1)./1000,rangev{1}/1000,(profile_data'))
# %pcolor(timestamp_msec/1000-timestamp_msec(1)./1000,rangev{3}/1000,profile_data(1:length(timestamp_msec),1:length(rangev{3}))')
# pcolor(dt_profile,rangev{3}/1000,profile_data(1:length(timestamp_msec),1:length(rangev{3}))')
#
# shading flat
# %caxis([-3 4])
# colorbar
# set(gca,'ydir','reverse')
# ylabel('Depth (m)');xlabel('Time (hh:mm)')
# hold on
# plot(dt_profile-seconds(2.7),smooth_depth_m,'.k')
# % this 10 sample delay is due to some lag in the smoothed depth output
# % presumably due to the smoothing filter they use.
#
#
# print('-dpng',[ 'profile_data' , dirstr])
# range_bins=rangev{3}/1000;
# profile_int_matrix=profile_data(1:length(timestamp_msec),1:length(rangev{3}))';
# %% some filtering and bed detection
# filt_prof_data=profile_data(1:length(timestamp_msec),1:length(rangev{3}))';
# filt_prof_data = hmf(filt_prof_data,13);% hyrbrid median filter for noise reduction
# %https://www.mathworks.com/matlabcentral/fileexchange/25825-hybrid-median-filtering?s_tid=srchtitle
# %%
# figure(5);clf
# %   pcolor(timestamp_msec/1000-timestamp_msec(1)./1000, rangev{3}/1000,  imfilter(filt_prof_data,ones(20,1)./20)  )
# pcolor(timestamp_msec/1000-timestamp_msec(1)./1000, rangev{3}/1000,  imfilter(filt_prof_data,ones(5,1)./5)  )
#
# shading flat
# set(gca,'ydir','reverse')
# % A simple 99th percentile threshold detector for each ping bed detector
# figure(50);clf
# %imagesc(diff( imfilter(filt_prof_data,ones(10,1)./10),1,1)>3000)
#
# blank=100;
# thr=prctile(filt_prof_data(blank:end,:),90);
# [m,n]=size(filt_prof_data(blank:end,:));
# for ii =1:n
#     tmp= find(imfilter(filt_prof_data(blank:end,ii),ones(10,1)./10)>thr(ii),1,'first');
#     if ~isempty(tmp)
#         bed_detect_ind(ii)=tmp;
#     else
#         bed_detect_ind(ii)=0;   %zero is bad data value
#     end
# end
# imagesc( imfilter(filt_prof_data,ones(10,1)./10)>mean(thr))
#
# hold on
# plot(bed_detect_ind+blank,'r')
# figure(5);hold on
# bed_detect_range=rangev{3}(bed_detect_ind+blank)./1000;
# plot(timestamp_msec/1000-timestamp_msec(1)./1000,  bed_detect_range,'r')
# save( [ 'profile_data' , dirstr], 'dt_profile', 'range_bins',  'profile_int_matrix', 'bed_detect_range')
#
# %%
# figure(6);clf
# subplot(211)
# plot(seconds(diff(dtp)))
# mean(seconds(diff(dtp)))
# hold on
# plot(diff( timestamp_msec./1e3))
# subplot(212)
# plot(second(dtp))
#
#
# figure(7);clf
# plot(length_mm./1000)
#
#
# drawnow
# %pause
#
# %% look at the id=3 text packets
# for ii=1:length(txt)
#     % txt strings with depths and smooth depths
#     char(txt{ii})'
#     ind=strfind(char(txt{ii})','thisd');
#     txt_depth(ii)=str2num(char(txt{ii}(ind+[6:10])'));
#     inds=strfind(char(txt{ii})','smoothd');
#     txt_smooth_depth(ii)=str2num(char(txt{ii}(inds+[8:12])'));
# end
# %.107/450 =.2 kb per ping
# %%
# figure(7);clf
# plot(dt_txt,txt_depth,'b');
# hold on
# plot(dt_txt(1:end)+(dt_txt(1)-dt_txt(10)),txt_smooth_depth(1:end),'r')% note delay of 10 samples to account for smoothing filter
# %plot(dt_txt(1:end)+seconds(2),txt_smooth_depth(1:end),'m')% note delay of 10 samples to account for smoothing filter
#
# plot( dt_profile,bed_detect_range,'g')
# % the cerulean bed detection looks roughly similar to my 99% thershold detector
# save([ 'detected_range' , dirstr],  'dt_txt' ,'txt_smooth_depth', 'txt_depth');