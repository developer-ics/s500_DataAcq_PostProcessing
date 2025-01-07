clear;close('all')


inpar_ent='y' % hard codes y
%inpar_ent=input(['Accept default .\\InputParam.txt or enter input paramter file path\\name (y or path\\name):'] ,"s")
if inpar_ent=='y'
   % inpar=[pwd '\InputParamMAJd2.txt']
       inpar=[pwd '\InputParamMV_Oct28_2024.txt']

else
      inpar=inpar_ent;
end
disp(['trying to get input from: ' inpar])
%Ti=readtable("InputParam.txt",'Delimiter',',','ReadRowNames',1,'Format','%s %s %s');
Ti=readtable(inpar,'Delimiter',',','ReadRowNames',1,'Format','%s %s %s','CommentStyle',{'%'});

disp('Parameter file:')
disp(Ti)
T2 = rows2vars(Ti);

%pause
survey_day=datetime(T2.survey_day(2),'InputFormat','uuuu/MM/dd')

fs=char(datetime(survey_day,'Format','MM-dd-yyyy'));
fs2=char(datetime(survey_day,'Format','yyyyMMdd'));

%addpath('F:\GDriveICS\My Drive\IntegratedCoastalSolutions\SoftwareDevelopment\Yellowfin\ExampleDataPro\ProcessingScripts')
%data_dir='F:\GDriveICS\My Drive\IntegratedCoastalSolutions\SoftwareDevelopment\Yellowfin\ExampleDataPro\MVLPData'
data_dir=char(T2.data_dir(2))
odir=[data_dir '\matfiles_'  fs2 '\'];% location of matfiles that are stored in processing
godir=[data_dir '\image_files_'  fs2 '\'];% location of  graphicsfiles that are generated in processing
mkdir(odir)
mkdir(godir)
%% Step 1: reads NMEA gps data written to rasbpi logger
% these should be in dirstr = .\Data\nmeadata\MM-dd-yyyy\
% where data_dir =pwd is the location of this script
dirstr1=[data_dir '\Data\nmeadata\' fs]

enable_S1=str2num(cell2mat(T2.enable_S1(2)));
if enable_S1
    disp("Running Step 1")
s1_readNMEAfiles 
else
        disp("Skipped Step 1")
end

%no figures

 %% Step 2: reads s500 sonar data written to rasbpi logger
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2');
% % these should be in dirstr =  [data_dir '\Data\s500\MM-dd-yyyy\']
% % where data_dir =pwdis the location of this script
dirstr2=[data_dir  '\Data\s500\' fs]
%
int_pro=str2num(cell2mat(T2.echo_profile(2)));  % processing of full intensity profile, usually should be zero . built in bed detection is usually suffcient
 system_default_sound_speed=str2num(cell2mat(T2.system_default_sound_speed(2)));
%d=2
%p = 101.325+1025*9.81*d/1000
%s=35
%t=3
%c_water(t,p,s)
measured_sound_speed=str2num(cell2mat(T2.measured_sound_speed(2)));
use_txt_depth_strings=str2num(cell2mat(T2.use_txt_depth_string(2)));
%
enable_S2=str2num(cell2mat(T2.enable_S2(2)));
if enable_S2
        disp("Running Step 2")
s2_read_s500sonar
else
        disp("Skipped Step 2")
end
%
%  with profiles on creates figure 1 to 4. Otherwise just 5
%
%% Step 3:  s3_Intensity_profile_bed_detection
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2');
dirstr2=[data_dir  '\Data\s500\' fs]

enable_S3=str2num(cell2mat(T2.enable_S3(2)));

if enable_S3
        disp("Running Step 3")
s3_Intensity_profile_bed_detection
else
        disp("Skipped Step 3")
end
%% Step 4: Set Start and End time for processing and assign NMEA GGA sentence based time stamps to sonar data
%  this should eliminate any issues with data logger time set incorrectly
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2');
% % GPS based start is when gps drops below GPS_thresh m MSL, end is when goes above GPS_thresh m MSL
 


Use_Realtime_Bed_Detection=str2num(cell2mat(T2.Use_Realtime_Bed_Detection(2)));
use_forced_time=str2num(cell2mat(T2.use_forced_time(2)));

if use_forced_time
start_time_forced=datetime(T2.start_time_forced(2),'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC')
end_time_forced=datetime(T2.end_time_forced(2),'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC')
end

 GPS_thresh=str2num(cell2mat(T2.GPS_thresh(2)));

%  Sonar based start is when std(depth) drops below SONAR_thresh m , end is when it
%  goes above SONAR_thresh. It is very noisy out of the water so std is high
SONAR_thresh=str2num(cell2mat(T2.SONAR_thresh(2)));

%  you can change these manually by editing the generated
%  s3_START_END_TIMES_*.mat mat file or this"
 sonar_start_time_adjust=minutes(str2num(cell2mat(T2.sonar_start_time_adjust(2))));% delay the start5
 sonar_end_time_adjust=-minutes(str2num(cell2mat(T2.sonar_end_time_adjust(2))));% advance  the end


num_exclusions=sum(contains(T2.Properties.VariableNames,'exclusion_start'))
start_exclusion_ind=find(contains(T2.Properties.VariableNames,'exclusion_start'))
end_exclusion_ind=find(contains(T2.Properties.VariableNames,'exclusion_end'))

for ii=1:num_exclusions
exclusion_start_time(ii)=datetime(T2{2,start_exclusion_ind(ii)},'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC');
exclusion_end_time(ii)=datetime(T2{2,end_exclusion_ind(ii)},'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC');
end
%



% set the time zone of the rasbpi data logger
 %YF_timezone=char( T2.YF_timezone(2))

 processing_time=seconds(str2num(cell2mat(T2.processing_time(2))));

enable_S4=str2num(cell2mat(T2.enable_S4(2)));
if enable_S4
            disp("Running Step 4")

s4_Set_start_end_time_sync_MAJ
else
        disp("Skipped Step 4")

end
% % makes figures(6) and 7


 %% Step 5:  Merge NMEA GPS DATA and Sonar Data. Sonar Data is cleaned here
% % look at lines 29 thru 81 for 3 stages of time series cleaning
% %  look at lines 156 177 for rejection of outlier from a spatiall smoothed
% %  solution
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2','processing_time');



 % enables time series despking based on median filters
  despike_on=str2num(cell2mat(T2. despike_on(2)));

 %enables mapping output must  needs to be 1 for the next step (spatial_filter_rejection) to work
 make_maps=str2num(cell2mat(T2.make_maps(2)));
 spatial_filter_rejection=str2num(cell2mat(T2. spatial_filter_rejection(2)));
spatial_reject_thr=str2num(cell2mat(T2. spatial_reject_thr(2)));
enable_s5=str2num(cell2mat(T2.enable_S5(2)));
if enable_s5
                disp("Running Step 5")

s5_MergeNMEA_GPS_s500
else
        disp("Skipped Step 5")

end
% % makes figures(8) to (13)
%


%% Step 6: Load PPK GNSS data
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2')
%  LLH data from emlid studio should be in:
%  and PPK *.pos data in :

 %dirnm=[data_dir '\Reachr0_' fs2 '*']
ppk_gpsdata_pos_path=char(T2.ppk_gpsdata_pos_path(2))
ppk_gpsdata_LLH_path=char(T2.ppk_gpsdata_LLH_path(2))


% The PPK data should have 10 header lines with the
% the 10th having variable names as defined by Emlid Studio

% the below can be used to convert ellopsiodal height data to orthometric
% height with some small error due to spatial variablity
% Emlid data from Emlid studio is usually output in ellopsiodal height
% ell2ortho = 29.028 % from https://vdatum.noaa.gov/vdatumweb/
 %v ;% the Martha's Vineyard example data was processed in orthometric height
 ell2ortho =str2num(cell2mat(T2.ell2ortho(2)));
enable_S6=str2num(cell2mat(T2.enable_S6(2)));
if enable_S6
                    disp("Running Step 6")
    %s6_read_emlid_LLH_PPK
    s6_read_qinertia_LLH_PPK
    else
        disp("Skipped Step 6")
end
%
% % makes figures(14) to (15)
%
 %% Merge PPK GNSS data with  Sonar Data
% % another time sync step is perfromed here by sliding corelation of heave
% % in both sonar and PPK GNSS data
% % This is done on lines 11 through 64
% % the variable use_resync =1 will enable this feature,
% % gps_leap_offset =0 will disable this and use zero lag shift.
% % The top panal of figure(21) will show if this is ok as soanr and GNSS
% % heave should line up
%
% % gps_leap_offset = 18 seconds and  a processing delay of 0.7 should lead
% % zero lags. The processing delay of 0.7 might need to be adjusted slightly
% % to get 0 lags and allow disabling this resyncing.  other values are
% % accepatble as the code will use non-zero values.
% % Large values over 10 might  indicate a timing problem
%
 keep3('survey_day','fs','fs2','odir','godir','data_dir','T2');
 %use_resync=0;
  use_resync =str2num(cell2mat(T2.use_resync(2)));


 gps_leap_offset =seconds(str2num(cell2mat(T2. gps_leap_offset(2))));% usually 18

 processing_delay=seconds(0);% allows another processing delay, not needed. 
 sync_vert_offset =str2num(cell2mat(T2. sync_vert_offset(2)));% to make figure(20)  red and blue line overlap vertically

 %xl(1)=datetime(2023,5,5,17,7,0,'TimeZone','UTC') %pick a period with sonar variations due to heave not bed changes
% xl(2)=datetime(2023,5,5,17,11,0,'TimeZone','UTC')
 
xl(1)=datetime(T2.start_sync_time(2),'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC');
xl(2)=datetime(T2.end_sync_time(2),'InputFormat','uuuu/MM/dd HH:mm:ss','TimeZone','UTC');
if use_resync
disp("Re-Sync period start and end:)")
xl
  end
% 

   make_maps_ppk =str2num(cell2mat(T2.make_maps_ppk(2)));

enable_S7=str2num(cell2mat(T2.enable_S7(2)));
if enable_S7
     disp("Running Step 7")
 s7_MergePPKGPS_sonar
   else
        disp("Skipped Step 7")
end
% % makes figures (16) to (24)
disp('Done hit ctrl-c to exit if running complied version')
