
; % this variabe enabels processing of the full intensity profile, set to zero just uses the S500 estaimate of bed location
% much faster with it set to zero


dd=dir([dirstr2 '\*.dat']);

speed_scale=measured_sound_speed./system_default_sound_speed;

%dirstr2='01-11-2023'%  a small gird of goodwil pond in falmouth
disp('S500 files to be processed:')
for ii=1:length(dd)
    disp([num2str(ii) ' ' (dd(ii).name)])
end
%%
ij=0;i3=0;
for fi=1:length(dd) %5  20201218-101925265.bin ios new 500 khz
    disp([dirstr2 '\' dd(fi).name])
    fid=fopen( [dirstr2 '\' dd(fi).name]);

    frewind(fid);
    xx=fread(fid,'uchar');
    %char(xx')
    st=findstr('BR',char(xx'));
    %https://ceruleansonar.com/pages/cerulean-sounder-api

    for ii=1:(length(st)-2)
        %for ii=1:1000
        fseek(fid,st(ii)+1,-1);
        datestring{ii}=fread(fid,26,'char');
        try
            dt(ii)=datetime(char(datestring{ii}'),'InputFormat','yyyy-MM-dd HH:mm:ss.SSSSSS');
        catch
            continue
        end
        packet_len(ii)=fread(fid,1,'uint16');
        packet_id(ii)=fread(fid,1,'uint16');
        r1=fread(fid,1,'uint8');
        r2=fread(fid,1,'uint8');

        if packet_id(ii)==1300
            %  disp('pid=1300')
            ij=ij+1;
            distance(ij)=fread(fid,1,'uint32');%mm
            confidence(ij)=fread(fid,1,'uint16');%mm
            transmit_duration(ij)=fread(fid,1,'uint16');%us
            ping_number(ij)=fread(fid,1,'uint32');%#
            scan_start(ij)=fread(fid,1,'uint32');%mm
            scan_length(ij)=fread(fid,1,'uint32');%mm
            gain_setting(ij)=fread(fid,1,'uint32');%
            profile_data_length(ij)=fread(fid,1,'uint32');%
            %if profile_data_length(ij)<300
            for jj=1:200
                tmp=fread(fid,1,'uint8');
                if ~isempty(tmp)
                    profile_data(ij,jj)=tmp;
                end
            end
            %end
        end
        if use_txt_depth_strings==1
            if packet_id(ii)==3

                i3=i3+1;
                txt{i3}=fread(fid, packet_len(ii),'char');%mm
                dt_txt(i3)=dt(ii);
            end
        end
        if packet_id(ii)==1308
            % disp('pid=1308')
            ij=ij+1;
            dtp(ij)=dt(ii);
            ping_number(ij)=fread(fid,1,'uint32');%mm

            start_mm(ij)=fread(fid,1,'uint32');%mm
            length_mm(ij)=fread(fid,1,'uint32');%mm
            start_ping_hz(ij)=fread(fid,1,'uint32');%us
            end_ping_hz(ij)=fread(fid,1,'uint32');%#
            adc_sample_hz(ij)=fread(fid,1,'uint32');%mm
            timestamp_msec(ij)=fread(fid,1,'uint32');%mm
            spare2(ij)=fread(fid,1,'uint32');%mm

            ping_duration_sec(ij)=fread(fid,1,'float');%
            analog_gain(ij)=fread(fid,1,'float');%
            max_pwr(ij)=fread(fid,1,'float');%
            min_pwr(ij)=fread(fid,1,'float');%
          
                this_ping_depth_m(ij)=fread(fid,1,'float');%
                smooth_depth_m(ij)=fread(fid,1,'float');%
                fspare2(ij)=fread(fid,1,'float');%
                ping_conf(ij)=fread(fid,1,'uint8');%
                gain_index(ij)=fread(fid,1,'uint8');%
                decimation(ij)=fread(fid,1,'uint8');%
                smooth_ping_conf(ij)=fread(fid,1,'uint8');%
         
            num_results(ij)=fread(fid,1,'uint16');%
            rangev{ij}=speed_scale.*linspace( start_mm(ij),start_mm(ij)+length_mm(ij),num_results(ij));
            if int_pro
                dt_profile(ij)=dt(ii);
                if num_results(ij)==2222
                    for jj=1:   num_results(ij)
                        tmp=fread(fid,1,'uint16');
                        if ~isempty(tmp)
                            profile_data(ij,jj)=tmp;
                        end
                    end
                end
            end
        end

    end
    fclose('all');
end
if 0
    %%
    figure(1);clf
    plot(distance,'.')
    yaxis([ 0 900])

    figure(2);clf
    plot(ping_number,'.')
    figure(3);clf
    plot(packet_id,'.')
    yaxis([0 2000])

    %%
    % figure(4);clf
    % %pcolor(log10(profile_data'))
    % pcolor(timestamp_msec/1000,rangev{1},log10(profile_data'))
    %
    % shading flat
    % caxis([-3 4])
    % colorbar
end

%%
if int_pro
    figure(1);clf
    plot(smooth_depth_m,'.')
    yaxis([ 0 900])

    figure(2);clf
    %  pcolor(timestamp_msec/1000-timestamp_msec(1)./1000,rangev{1}/1000,(profile_data'))
    %pcolor(timestamp_msec/1000-timestamp_msec(1)./1000,rangev{3}/1000,profile_data(1:length(timestamp_msec),1:length(rangev{3}))')
    pcolor(dt_profile,rangev{3}/1000,profile_data(1:length(timestamp_msec),1:length(rangev{3}))')

    shading flat
    %caxis([-3 4])
    colorbar
    set(gca,'ydir','reverse')
    ylabel('Depth (m)');xlabel('Time (hh:mm)')
    hold on
    plot(dt_profile-seconds(2.7),smooth_depth_m,'.k')
    % this 10 sample delay is due to some lag in the smoothed depth output
    % presumably due to the smoothing filter they use.
    colormap(jet)

    print('-dpng',[godir  's2_s550_raw_profile_data' ,fs2])
    range_bins=rangev{3}/1000;
    profile_int_matrix=profile_data(1:length(timestamp_msec),1:length(rangev{3}))';

    %% some filtering and bed detection
    filt_prof_data=profile_data(1:length(timestamp_msec),1:length(rangev{3}))';
    filt_prof_data = hmf(filt_prof_data,13);% hyrbrid median filter for noise reduction
    %https://www.mathworks.com/matlabcentral/fileexchange/25825-hybrid-median-filtering?s_tid=srchtitle
    %%
    figure(3);clf
    %   pcolor(timestamp_msec/1000-timestamp_msec(1)./1000, rangev{3}/1000,  imfilter(filt_prof_data,ones(20,1)./20)  )
    % pcolor(timestamp_msec/1000-timestamp_msec(1)./1000, rangev{3}/1000,  imfilter(filt_prof_data,ones(5,1)./5)  )
    pcolor(dt_profile, rangev{3}/1000,  imfilter(filt_prof_data,ones(5,1)./5)  )

    shading flat
    set(gca,'ydir','reverse')
    colorbar
    caxis([3e4 6e4])
    % A simple 99th percentile threshold detector for each ping bed detector
    figure(50);clf
    %imagesc(diff( imfilter(filt_prof_data,ones(10,1)./10),1,1)>3000)

    blank=130;
    maxsr=1500
    thr=prctile(filt_prof_data(blank:maxsr,:),98);
    [m,n]=size(filt_prof_data(blank:maxsr,:));
    for ii =1:n
        tmp= find(imfilter(filt_prof_data(blank:end,ii),ones(10,1)./10)>thr(ii),1,'first');
        tmp2= find(imfilter(filt_prof_data(blank:end,ii),ones(10,1)./10)>thr(ii),1,'last');

        if ~isempty(tmp)
            bed_detect_ind(ii)=tmp;
        else
            bed_detect_ind(ii)=0;   %zero is bad data value
        end

        if ~isempty(tmp2)
            bed_detect_ind2(ii)=tmp2;
        else
            bed_detect_ind2(ii)=0;   %zero is bad data value
        end
    end
    imagesc( imfilter(filt_prof_data,ones(10,1)./10)>mean(thr))

    hold on
    plot(bed_detect_ind+blank,'r')
    plot(bed_detect_ind2+blank,'m')

    %
    figure(3);hold on
    bed_detect_range=rangev{3}(bed_detect_ind+blank)./1000;
    bed_detect_range2=rangev{3}(bed_detect_ind2+blank)./1000;

    plot(dt_profile,  bed_detect_range,'r')
    plot(dt_profile,  bed_detect_range2,'m')
    print('-dpng',[godir  's2_s550_filtered_profile_data_w_detections' ,fs2])

    save([odir  's2_profile_data' fs2], 'dt_profile', 'range_bins',  'profile_int_matrix', 'bed_detect_range','filt_prof_data')

    %%
    figure(4);clf
    subplot(211)
    plot(seconds(diff(dtp)))
    mean(seconds(diff(dtp)))
    hold on
    plot(diff( timestamp_msec./1e3))
    subplot(212)
    plot(second(dtp))


    figure(7);clf
    plot(length_mm./1000)


    drawnow
    %pause
end
%% look at the id=3 text packets
if use_txt_depth_strings==1
    for ii=1:length(txt)
        % txt strings with depths and smooth depths
        char(txt{ii})';
        ind=strfind(char(txt{ii})','thisd');
        txt_depth(ii)=speed_scale.*str2num(char(txt{ii}(ind+[6:10])'));
        inds=strfind(char(txt{ii})','smoothd');
        txt_smooth_depth(ii)=speed_scale.*str2num(char(txt{ii}(inds+[8:12])'));
    end
elseif use_txt_depth_strings==0
    txt_depth   =speed_scale.*this_ping_depth_m;
    txt_smooth_depth= speed_scale.*smooth_depth_m;
    dt_txt=dtp;
end
%%
figure(5);clf
hb=plot(dt_txt,txt_depth,'.-b');
hold on
hr=plot(dt_txt,txt_smooth_depth,'.-r');% note delay of 10 samples to account for smoothing filter

%hr=plot(dt_txt(1:end)+(dt_txt(1)-dt_txt(10)),txt_smooth_depth(1:end),'.r');% note delay of 10 samples to account for smoothing filter
%plot(dt_txt(1:end)+secon ds(2),txt_smooth_depth(1:end),'m')% note delay of 10 samples to account for smoothing filter
title('s500 built in detector depth')
ylabel('Meters')
legend([hb hr],'Instantaneous samples',' s500 internally smoothed')
%plot( dt_profile,bed_detect_range,'g')
% the cerulean bed detection looks roughly similar to my 99% thershold detector
save([odir 's2_s500_DETECTED_RANGE_' , fs2],  'dt_txt' ,'txt_smooth_depth','txt_depth','ping_conf','smooth_ping_conf' ); %
%dirstr2='s500'
yaxis([prctile(txt_smooth_depth,1)-.1  prctile(txt_smooth_depth,99)+.5])