%%


outname=[odir 's1_NMEA_GNSS_DATA_' fs2]
GPS=load(outname);

GPS.pc_time_gga=datetime(GPS.pc_time_gga,'TimeZone',YF_timezone);
%GPS.gps_utc_time=GPS.gps_utc_time+processing_time;

% use the matlab bed detection from profile data..not fully supported yet




if Use_Realtime_Bed_Detection % use the cerulean instantaenous bed detection . Not sure about delay with smoothed
    S1=load([odir 's2_s500_DETECTED_RANGE_' fs2 '.mat']);
    sonar_time_rp=S1.dt_txt(:)-processing_time;
    sonar_range=S1.txt_depth(:);

    ping_conf=S1.ping_conf;
    smooth_ping_conf=S1.smooth_ping_conf;
else
    % use the matlab bed detection from profile data..not fully supported yet

    S1=load([odir  's3_profile_detections_' fs2]);
    sonar_time=S1.dt_profile(:);
    sonar_time_rp=S1.dt_profile(:)-processing_time;
    ping_conf=ones(size(sonar_time));
    smooth_ping_conf=ping_conf;
    sonar_range=S1.bed_detect_range_comb(:);
end

%sonar_time_rp=S1.dt_txt(:)

;


%% Plot Altitude from NMEA
figure(7);clf
subplot(311)
plot(GPS.gps_utc_time,GPS.altMSL,'m')
hold on
plot(GPS.gps_utc_time,GPS.altMSL,'b')

title('GPS altitude')

subplot(312)
sonar_time_rp_utc=datetime(datetime(sonar_time_rp,'TimeZone',YF_timezone),'TimeZone','UTC');
%this could be off if clock not set correctly..not from gps
hb=plot(sonar_time_rp_utc,sonar_range);
hold on
hr =plot(sonar_time_rp_utc,movstd(sonar_range,50),'m');
yaxis([prctile(sonar_range,1)-.1  prctile(sonar_range,99)+.5])
title('Sonar depth')

%% pick out start and end times
% GPS based start is when boat drops below 2 m MSL, end is when goes above
% 2m



start_ind_gps=find(GPS.altMSL(100:end)<GPS_thresh,1,'first')+100;
start_time_gps=GPS.gps_utc_time(start_ind_gps)+seconds(30); %offset till the boat is in the water
end_ind_gps=length(GPS.gps_utc_time)-find(GPS.altMSL(end:-1:1)<GPS_thresh,1,'first');
end_time_gps=GPS.gps_utc_time(end_ind_gps)-seconds(30);; %offset from when the boat boat left  the water
subplot(311)
yl=ylim;

plot([ start_time_gps start_time_gps] ,yl,'g','LineWidth',3);
text( start_time_gps,yl(2)-.5,['start time = ' datestr(start_time_gps)]);
plot([ end_time_gps end_time_gps] ,yl,'m','LineWidth',3);
text( end_time_gps,yl(2)-.5,['end time= ' datestr(end_time_gps)]);

% sonar based start is when running std  drops below 2 m
start_ind_sonar=find(movstd(sonar_range,100)<SONAR_thresh,1,'first');
start_time_sonar=sonar_time_rp(start_ind_sonar); %offset till the boat is in the water
start_time_sonar=datetime(start_time_sonar,'TimeZone',YF_timezone);
end_ind_sonar=length(sonar_time_rp)-find(movstd(sonar_range(end:-1:1),50)<SONAR_thresh,1,'first');
end_time_sonar=sonar_time_rp(end_ind_sonar);; %offset from when the boat boat left  the water
end_time_sonar=datetime(end_time_sonar,'TimeZone',YF_timezone);

subplot(312)
yl=ylim;

plot([ start_time_sonar start_time_sonar] ,yl,'g','LineWidth',3)
text( start_time_sonar,yl(2)-.5,['start time sonar = ' datestr(start_time_sonar)])
plot([ end_time_sonar end_time_sonar] ,yl,'m','LineWidth',3)
text( end_time_sonar,yl(2)-.5,['end time sonar= ' datestr(end_time_sonar)])


%final time is innerof the two
start_time=max(datetime(start_time_sonar,'TimeZone','UTC'),start_time_gps)+sonar_start_time_adjust;
end_time=min(datetime(end_time_sonar,'TimeZone','UTC'),end_time_gps)+sonar_end_time_adjust;

legend([hb hr],'SonarDepth','moving std filter')




%%  fit gps time to rasb pi time
gps_ind_st=near(GPS.gps_utc_time,start_time);
gps_ind_en=near(GPS.gps_utc_time,end_time);
gps_ind=gps_ind_st:gps_ind_en;

sonar_ind_st=near(sonar_time_rp_utc,start_time)-20;% 100 is make it abit longer for avoidng nans in time syncing later
sonar_ind_en=near(sonar_time_rp_utc,end_time)+20;
sonar_ind=sonar_ind_st:sonar_ind_en;



figure(6);clf
subplot(311)
plot(datetime(GPS.pc_time_gga(gps_ind),'timezone',YF_timezone),datetime(GPS.gps_utc_time(gps_ind),'timezone','UTC'),'.')
xlabel('Raspbi time');ylabel('NMEA Gps time')

subplot(312)
plot(fillmissing(datenum(GPS.pc_time_gga(gps_ind)-GPS.pc_time_gga(gps_ind(1))),'linear'),fillmissing(datenum(GPS.gps_utc_time(gps_ind)-GPS.pc_time_gga(gps_ind(1))),'linear'))

%plot(datenum(GPS.pc_time_gga),datenum(GPS.gps_utc_time),'.r');
hold on
%plot(fillmissing(datenum(GPS.pc_time_gga),'linear'),fillmissing(datenum(GPS.gps_utc_time),'linear'),'.g')
%yaxis([-1 1])

[pp,~,mu]=polyfit(fillmissing(datenum(GPS.pc_time_gga(gps_ind)),'linear'),fillmissing(datenum(GPS.gps_utc_time(gps_ind)),'linear'),3);
%[pp,~,mu]=polyfit(datenum(GPS.pc_time_gga),datenum(GPS.gps_utc_time),3);


xlabel('Raspbi time (Days)');ylabel('NMEA Gps time (Days)')
subplot(313)
plot(datetime(GPS.pc_time_gga(gps_ind),'TimeZone',YF_timezone),seconds(datetime(GPS.pc_time_gga(gps_ind),'TimeZone',YF_timezone)-GPS.gps_utc_time(gps_ind)),'.')
testpred_mtime=polyval(pp,datenum(GPS.pc_time_gga(gps_ind)),[],mu);
testpred_dtime=datetime(testpred_mtime,'convertFrom','datenum','TimeZone','UTC');
hold on
ydata=seconds(datetime(GPS.pc_time_gga(gps_ind),'TimeZone',YF_timezone)-testpred_dtime);
plot(datetime(GPS.pc_time_gga(gps_ind),'TimeZone',YF_timezone),ydata,'.')
sonar_mtime_utc_gps=polyval(pp,datenum(sonar_time_rp),[],mu);
sonar_dtime_utc_gps=datetime(sonar_mtime_utc_gps,'convertFrom','datenum','TimeZone','UTC');
title('Difference NMEA Gps time -  Rasbpi time')
yaxis([min(ydata) max(ydata)])



save([odir 's4_s500_DETECTED_RANGE_synced_' fs2],'sonar_dtime_utc_gps','sonar_mtime_utc_gps','sonar_range','ping_conf','smooth_ping_conf')


%% exclusion periods
exinds=ones(size(sonar_range));

% ii=2
% exclusion_start_time(ii)=datetime('2024/02/09 16:32:20','InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC')
% exclusion_end_time(ii)=datetime('2024/02/09 16:37:15','InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC')

figure(7)
subplot(313)
yaxis([2 15])
hold on
for ii=1:num_exclusions
    exclusion_start_ind(ii)=near(sonar_time_rp_utc,exclusion_start_time(ii));
    exclusion_end_ind(ii)=near(sonar_time_rp_utc,exclusion_end_time(ii));
    exinds(exclusion_start_ind(ii):exclusion_end_ind(ii))=NaN;
    plot([ exclusion_start_time(ii) exclusion_start_time(ii)] ,yl,'y','LineWidth',2)
    plot([ exclusion_end_time(ii) exclusion_end_time(ii)] ,yl,'c','LineWidth',2)

end


plot([ start_time start_time] ,yl,'--g','LineWidth',3)
text( start_time,yl(2)-2,['start time combined = ' datestr(start_time_sonar)])
plot([ end_time end_time] ,yl,'--m','LineWidth',3)
text( end_time,yl(2)-2,['end time combined= ' datestr(end_time_sonar)])


sonar_ind_st=near(sonar_time_rp_utc,start_time);% 100 is make it abit longer for avoidng nans in time syncing later
sonar_ind_en=near(sonar_time_rp_utc,end_time);
exinds(1:sonar_ind_st)=NaN;
exinds(sonar_ind_en:end)=NaN;



hb=plot(sonar_time_rp_utc,sonar_range.*exinds);
yaxis([prctile(sonar_range,1)-.1  prctile(sonar_range,99)+.5])
xzoom
save([odir 's4_START_END_TIMES_' fs2],'start_time','end_time','exinds')