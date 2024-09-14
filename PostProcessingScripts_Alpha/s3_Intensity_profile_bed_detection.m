load([odir  's2_profile_data_' fs2])



%%
figure(101);clf
pcolor(dt_profile,range_bins,profile_int_matrix)
shading flat
colorbar
caxis([4e4 6e4])
colormap(jet)
set(gca,'ydir','rev')
title('Raw_profile_data - Use this to set blanking and max range','Interpreter','none')
 ylabel('Depth (m)');xlabel('Time (hh:mm)')
%%
blank_r=.4;
max_r=1.8;
blank_ind=near(range_bins,blank_r);
max_ind=near(range_bins,max_r);
%%
reduced_range_bins=range_bins(blank_ind:max_ind);
filt_prof_data=profile_int_matrix(blank_ind:max_ind,:);
filt_prof_data = hmf(filt_prof_data,13);
%%
figure(102);clf
subplot(211)
pcolor(dt_profile,range_bins(blank_ind:max_ind),( profile_int_matrix(blank_ind:max_ind,:)))
shading flat
 set(gca,'ydir','reverse')
colorbar
caxis([3e4 6e4])
title('profile_data - with blanking and max range applied','Interpreter','none')
 ylabel('Depth (m)');xlabel('Time (hh:mm)')
;% hyrbrid median filter for noise reduction
%https://www.mathworks.com/matlabcentral/fileexchange/25825-hybrid-median-filtering?s_tid=srchtitle
subplot(212)
pcolor(dt_profile,reduced_range_bins, filt_prof_data)
shading flat
 set(gca,'ydir','reverse')
colorbar
caxis([3e4 6e4])
title('hybrid median filtered profile_data - with blanking and max range applied','Interpreter','none')
 ylabel('Depth (m)');xlabel('Time (hh:mm)')

    %%
    % A simple xxth percentile threshold detector for each ping bed detector
    figure(103);clf

subplot(211)
    thr=prctile(filt_prof_data,93);
    [m,n]=size(filt_prof_data);
    for ii =1:n
        tmp1= find(imfilter(filt_prof_data(:,ii),ones(10,1)./10)>thr(ii),1,'first');
        tmp2= find(imfilter(filt_prof_data(:,ii),ones(10,1)./10)>thr(ii),1,'last');

        if ~isempty(tmp1)
            bed_detect_ind1(ii)=tmp1;
        else
            bed_detect_ind1(ii)=NaN;   %zero is bad data value
        end

        if ~isempty(tmp2)
            bed_detect_ind2(ii)=tmp2;
        else
            bed_detect_ind2(ii)=NaN;   %zero is bad data value
        end
    end
     bed_detect_ind1= round(fillmissing(bed_detect_ind1,'linear'));
          bed_detect_ind2= round(fillmissing(bed_detect_ind2,'linear'));

    %  imagesc( imfilter(filt_prof_data(blank:maxsr,:),ones(10,1)./10)>mean(thr))
    pcolor(1:length(dt_profile),reduced_range_bins, filt_prof_data)
    shading flat
    hold on
    colormap(jet)
    plot(range_bins(bed_detect_ind1+blank_ind),'g')
    plot(range_bins(bed_detect_ind2+blank_ind),'b')
    caxis([3e4 6e4])
    set(gca,'ydir','rev')
title('hybrid median filtered profile_data - with 1st and last thershold detections','Interpreter','none')


    subplot(212)
     bed_detect_range1=clean0(range_bins(bed_detect_ind1+blank_ind),13,.25);
    bed_detect_range2=clean0(range_bins(bed_detect_ind2+blank_ind),13,.25);
     %    bed_detect_range1=spikeRemoval(range_bins(bed_detect_ind1+blank_ind),'wnsz',50,'nstd',.5,'npass',2,'debug',0);
%   bed_detect_range2=spikeRemoval(range_bins(bed_detect_ind2+blank_ind),'wnsz',50,'nstd',.5,'npass',2,'debug',0);
    pcolor(dt_profile,reduced_range_bins, filt_prof_data)
    shading flat
    hold on
    colormap
    plot(dt_profile,  bed_detect_range1,'g')
    plot(dt_profile,  bed_detect_range2,'b')
    caxis([3e4 6e4])
    set(gca,'ydir','rev')
    title('hybrid median filtered profile_data - with cleaned 1st and last thershold detections','Interpreter','none')

%figure(104)
dd=(smooth(diff([ bed_detect_range1 ; bed_detect_range2]),1000));% this should be the thickness of the bottom return
    plot(dt_profile,  (bed_detect_range1+(bed_detect_range2-dd'))./2 ,'c')
bed_detect_range_comb=(bed_detect_range1+(bed_detect_range2-dd'))./2
    print('-dpng',[godir  's2_s500_profile_data_w_realtime_detections' ,fs2])

    save([odir  's3_profile_detections_' fs2], 'dt_profile','bed_detect_range1','bed_detect_range2','bed_detect_range_comb')
