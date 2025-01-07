outname=[odir 's1_NMEA_GNSS_DATA_' fs2]
GPS=load(outname);


load([odir 's4_s500_DETECTED_RANGE_synced_' fs2])
load([odir 's4_START_END_TIMES_' fs2 '.mat'])

%% use start and end times to set inds
gps_ind_st=near(GPS.gps_utc_time,start_time);
gps_ind_en=near(GPS.gps_utc_time,end_time);
gps_ind=gps_ind_st:gps_ind_en;

sonar_ind=ones(size(exinds));
sonar_ind(isnan(exinds))=0;
sonar_ind=logical(sonar_ind);



%% three stages of cleaning here

% use ping conf 1st

figure(8);clf

subplot(311)
hb=plot(sonar_range(sonar_ind),'o-b');
%dsonar_range=sonar_range;
%dsonar_range(ping_conf==0)=sonar_range(ping_conf==0);;
%dsonar_range(ping_conf<50)=NaN;
%sonar_range=dsonar_range;
hold on
plot(ping_conf(sonar_ind)./100,'.g')
hb=plot(sonar_range(sonar_ind),'.-r');
yaxis([prctile(sonar_range(sonar_ind),1)-.1  prctile(sonar_range(sonar_ind),99)+.5])

subplot(312)



hb=plot(sonar_range(sonar_ind),'.-b');
yaxis([prctile(sonar_range(sonar_ind),1)-.1  prctile(sonar_range(sonar_ind),99)+.5])

hold on
%dsonar_range=despike1(sonar_range(sonar_ind),3)
%dsonar_range=hampel(sonar_range(sonar_ind),100,3);
if despike_on
dsonar_range=filloutliers(sonar_range(sonar_ind),'linear',"movmedian",100,'threshold',[3]);
else
    dsonar_range=sonar_range(sonar_ind);
end
%dsonar_range=spikeRemoval(sonar_range(sonar_ind),'nbins',12, 'wnsz',300, 'nstd',0,'debug','','npass',1,'ndata',5);
%dsonar_range=spikeRemoval(dsonar_range,'nbins',12, 'wnsz',300, 'nstd',1,'debug','','npass',3);

hr=plot(dsonar_range,'.r');

title('1st stage of sonar data cleaning using filloutliers')
legend([hb hr],'raw bottom dection','After 1st stage cleaning')

%hr1= plot(smoothdata(filloutliers(sonar_range(sonar_ind),'linear',"movmedian",70,'threshold',1.0),20),'.-r');
title('2nd stage of sonar data cleaning using filloutliers')
%legend([hb1 hr1],'raw bottom dection','After 2nd stage cleaning')
if despike_on
    rej_thr=.1;
else
        rej_thr=5;

end
sdsonar_range= dsonar_range-smoothdata(filloutliers(sonar_range(sonar_ind),'linear',"movmedian",50,'threshold',1.0),20);

subplot(313)
plot( sdsonar_range,'ob')
ninds=abs(sdsonar_range)> rej_thr;
hold on
sdsonar_range(ninds)=NaN;
plot(sdsonar_range,'.r')
dsonar_range(ninds)=NaN;
clean_sonar_range=dsonar_range;
title('3rd stage of sonar data cleaning using filloutliers..this is with low pass removed')


%clean_sonar_range=dsonar_range;

%fdsonar_range2=spikeRemoval(fdsonar_range);

sonar_dtime_utc_gps_g=sonar_dtime_utc_gps(sonar_ind);
sonar_mtime_utc_gps_g=sonar_mtime_utc_gps(sonar_ind);

%% The following lines allow manual cleaning of sonar data using the matlab brush data giu if desired
% figure(9);clf;plot(clean_sonar_range,'.b')
% bdata=gca().Children.YData
%save([odir 's4_brushed_data_' fs2] ,'bdata')
%load([odir 's4_brushed_data_' fs2])
%clean_sonar_range=bdata


%% Scatter Plot
%load bdata


%sonar_range_i=interp1(sonar_dtime_utc_gps(sonar_ind),clean_sonar_range,GPS.gps_utc_time(gps_ind));
%isonar_dtime_gps=GPS.gps_utc_time(gps_ind);
%lati=GPS.lat(gps_ind);
%loni=GPS.lon(gps_ind);
lati=interp1(fillmissing(GPS.gps_utc_time,'linear'),GPS.lat,sonar_dtime_utc_gps(sonar_ind));
loni=interp1(fillmissing(GPS.gps_utc_time,'linear'),GPS.lon,sonar_dtime_utc_gps(sonar_ind));



figure(10) ;clf
clean_sonar_range(clean_sonar_range>5)=NaN;
scatter(loni,lati,16,clean_sonar_range);
title({'Scatter plot of merged NMEA GNSS data',' and Sonar Depths after 3 stages of cleaning','and Border for not extrapolating'} )
xlabel('Long');ylabel("lat");
cc=turbo;cc=flipud(cc);
colormap(cc);
hc=colorbar;
hold on
    caxis([prctile(clean_sonar_range,1) prctile(clean_sonar_range,99)]);
hc.Label.String='Depth (M)';

mkdir(godir)
print('-dpng',[godir 's4_Initial Scatter Plot Survey' fs2]);


longitude=loni;
latitude=lati;
depth_from_xducer_no_heave_comp=clean_sonar_range;
sonar_time=sonar_dtime_utc_gps_g;
To=table(sonar_time,longitude,latitude,depth_from_xducer_no_heave_comp);
writetable(To,[odir 'No_Heave_Correction_Trackline_Data' fs2 '.txt'])

%% the following fits a surface and makes a contour and  geotiff..probabaly should wait to after ppk in most cases
% now include a cleaning set based on spatial smooting 
if make_maps
    %%
 %   disp('starting reg')
    x=loni(:);
    y=lati(:);
    z=-smoothdata(clean_sonar_range,20);
    ni=isnan(x);
    x(ni)=[];
    y(ni)=[];
    z(ni)=[];



    dx=.00005/4;

    gdx=50*dx;
    xnodes=(min(x)-gdx):dx:(max(x)+gdx);
    ynodes=(min(y)-gdx):dx:(max(y)+gdx);

    sff= 2e-04;
 %       sff= 20e-04;

    [Zg3,Xg3,Yg3]=RegularizeData3D(x ,y,z,xnodes,ynodes,'smoothness',sff);
    % RegularizeData3D needs to be donwloaded from the matlab file exchange
    %
   % scatter3(x,y,z,12,z,'filled');
   % view(2)
    % hold on
    % sl=600
    % for ii=1:(floor(length(x)/sl)-3)
    %     fit_inds=[1:sl]+sl+sl*ii
    %     scatter(x(fit_inds),y(fit_inds),12,z(fit_inds),'or');
    %     pause(.1)
    % end
    sf=10
    xsf=x(1:sf:end);
   ysf=y(1:sf:end);
    k=boundary(xsf,ysf,.95);%this makes the border/mask for not extrapolating
    figure(10);hold on
    plot(xsf(k),ysf(k),'k','linewidth',3);
    if 1
        [m,n]=size(Zg3);
        BW=roipoly(Xg3(1,:),Yg3(:,1),Zg3,xsf(k),ysf(k));
        BW=double(BW);
        BW(BW==0)=NaN;
    end

    DEM=GRIDobj(Xg3,Yg3,Zg3.*BW);
    set(gca,'dataaspectratio',[1 1 1]);

    %% interpolation of track from spatially smoothed data
    zi = interp(DEM,loni,lati); 

    %
    figure(11); clf;%more cleaning
    subplot(211)
   hr2= plot(sonar_time,zi,'.r');
    hold on
    hb2=plot(sonar_time,-clean_sonar_range,'b');
    title('Spatially smoothed data from surface fit  and cleaned data input into surface fitting ')
    legend([hr2 hb2],'Spatially smoothed data from surface fit','cleaned data input into surface fitting')
    subplot(212)
    plot(sonar_time,zi+clean_sonar_range,'.')
title("difference of above quatities..Data above and below red lines (spatial_reject_thr) is rejected ")
    zc=-clean_sonar_range;
        
hold on
xl=xlim;
        plot(xl,[spatial_reject_thr spatial_reject_thr],'r');      
 plot(xl,-[spatial_reject_thr spatial_reject_thr],'r')
if spatial_filter_rejection
    zc(abs(zi+clean_sonar_range)>spatial_reject_thr)=NaN; % reject outlier based on differecne with a therhold of 0.4 m from spatially smoothed results'
end
    %% Scatter plot of merged NMEA GNSS data and Sonar Depths after 4 stages of cleaning including spatial smoothing outlier rejection
    figure(12);clf

    scatter3(loni,lati,zc,12,zc,'filled');
    view(2);
    colorbar;
   caxis([prctile(zc,1)-.5 prctile(zc,99)+.5]);
      %  caxis([-8 prctile(zc,99)]);

    clean_sonar_range=-zc;;
title({'Final  Scatter plot of merged NMEA GNSS data',' and Sonar Depths after 4 stages of cleaning','Holes tend to be regions of consistent wave breaking'} )
    %% Contour plot
    figure(13);clf
   % cm=(ttscm('broc'));
   cm1=bone(64);
   cm2=flipud(pink(40));
  cm=[cm1(1:58,:);(cm2(6:40,:))];
  zlim=[prctile(zc,1)-1, prctile(zc,99)+1];
  zlim(1)=-8
 % tanakacontourLL(DEM,[zlim(1):.05:zlim(2)]);
imagesc(DEM);

    caxis(zlim);
    title(['YellowFin survey ' fs ]);
    hold on;
    %plot(x,y,'.k');
    sf =2;
    %hs=scatter(x(1:sf:end),y(1:sf:end),12,z(1:sf:end),'-');
    hs=plot(x(1:sf:end),y(1:sf:end),'-r');

    hs.MarkerEdgeColor='k';
    %cc=flipud(cc);
    colormap(cm);
    hc=colorbar;
    hc.Label.String='Depth (m)';
    xlabel('Lon (Deg)');
    ylabel('Lat (Deg)');
    print('-dpng',[godir 's4_Initial Contours, Survey' fs2]);

    %% Make geotiff
    fn=['s4_NMEA_GPS_DEM_' fs2 '.tif']
    save([odir fn(1:end-4)])
    GRIDobj2geotiff(DEM,[godir fn])	;
    [A,R] = readgeoraster([godir fn] );
    GRIDobj2geotiff(DEM,[godir fn])	;


    %geotiffwrite([godir fn],A,R,'CoordRefSysCode',26986);
end

    save([odir 's4_Cleaned_synced_s500_data_' fs2],'clean_sonar_range','sonar_dtime_utc_gps_g','sonar_mtime_utc_gps_g')

