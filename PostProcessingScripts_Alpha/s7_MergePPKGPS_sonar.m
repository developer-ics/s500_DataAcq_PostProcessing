
PPKGPS=load([odir 's5_PPK_GNSS_DATA_' fs2]);
%PPKGPS=load([odir 's5_Qintertia_PPK_GNSS_DATA_' fs2]);
S1=load([odir 's4_Cleaned_synced_s500_data_' fs2]);
load([odir 's3_START_END_TIMES_' fs2]);

outname=[odir 's1_NMEA_GNSS_DATA_' fs2];
GPS=load(outname);


%% compare gps data to make sure timing is ok
figure(19);clf
gps_total_offset=gps_leap_offset-processing_delay;%
hold on
plot(PPKGPS.datetime_ppk_g-gps_leap_offset,PPKGPS.lat_ppk,'.g')
%plot(datetime(GPS.gps_utc_time,'TimeZone','UTC'),GPS.lat,'m')
plot(GPS.gps_utc_time,GPS.lat,'m')

figure(20);clf
subplot(211)
plot(S1.sonar_dtime_utc_gps_g,S1.clean_sonar_range,'.-b')
hold on
%plot(GPS.mat_time(50:end-30),GPS.altWGS84(50:end-30),'.g')
hold on

plot(PPKGPS.datetime_ppk_g-gps_total_offset,PPKGPS.clean_height_datum_ppk-sync_vert_offset,'.-r')

%xaxis(xl)
clean_sonar_range_i=interp1(S1.sonar_dtime_utc_gps_g,S1.clean_sonar_range,PPKGPS.datetime_ppk_g-gps_total_offset);
yl =ylim;
plot([xl(1) xl(1)],yl,'-g')
plot([xl(2) xl(2)],yl,'-r')
text(xl(1),mean(yl),'Sync Region')



subplot(212)

plot(S1.sonar_dtime_utc_gps_g,S1.clean_sonar_range,'.-b')
hold on
%plot(GPS.mat_time(50:end-30),GPS.altWGS84(50:end-30),'.g')
hold on

plot(PPKGPS.datetime_ppk_g-gps_total_offset,PPKGPS.clean_height_datum_ppk-sync_vert_offset,'.-r')

%xaxis(xl)
clean_sonar_range_i=interp1(S1.sonar_dtime_utc_gps_g,S1.clean_sonar_range,PPKGPS.datetime_ppk_g-gps_total_offset);
yl =ylim;
xaxis(xl)


% another time sync here by correlating time
figure(21);clf
ws1=near(PPKGPS.datetime_ppk_g,xl(1));
ws2=near(PPKGPS.datetime_ppk_g,xl(2));

chc=(PPKGPS.clean_height_datum_ppk(ws1:ws2))-smoothdata(PPKGPS.clean_height_datum_ppk(ws1:ws2),'movmean',500,'omitnan');

subplot(411)
shc=clean_sonar_range_i(ws1:ws2)-smoothdata(clean_sonar_range_i(ws1:ws2),'movmean',200,'omitnan');
plot(shc,'r')
hold on
plot(chc,'b')
 title("heave and echosounder data before resync")
subplot(412)
[r,lags]=xcorr(fillmissing(shc,'linear'),chc,50,'unbiased');
plot(lags,r)
 title("Correlation function ouput)")

[mx,mi]=max(r);
%s_ssr=interp1(1:length(ssr),ssr,[1:length(ssr) ]+ml);


if use_resync
    ml=lags(mi);
    disp(['Used resyncing with lag of ' num2str(ml) ' samples'])
else
    ml=0;
end
shifted_sonar_range_i=interp1(1:length(clean_sonar_range_i),clean_sonar_range_i,[1:length(clean_sonar_range_i) ]+ml);

subplot(413)
plot(chc+4,'b')
hold on
plot(shifted_sonar_range_i(ws1:ws2),'r');
 title("heave and shifted echosounder data after resync")

subplot(414)
plot(chc-shifted_sonar_range_i(ws1:ws2)')
 title("heave - shifted echosounder residual after resync")

%%

figure(22) ;clf
scatter(PPKGPS.lon_ppk,PPKGPS.lat_ppk,16,shifted_sonar_range_i)
cc=turbo;
cc=flipud(cc);
colormap(cc)
colorbar
hold on
%caxis([2 13])

%%
gpsantenna_offset_waterline=.15;
sonar_waterline_offset=.10;%sonar to waterline
x=PPKGPS.lon_ppk;
y=PPKGPS.lat_ppk;
z=-shifted_sonar_range_i(:)+PPKGPS.clean_height_datum_ppk-(sonar_waterline_offset+gpsantenna_offset_waterline);
%

longitude=x;latitude=y;
z_water_surf=-(shifted_sonar_range_i(:) +sonar_waterline_offset);
z_gps_datum=PPKGPS.clean_height_datum_ppk(:);
z_seafloor_datum=z_water_surf  + z_gps_datum - sonar_waterline_offset;

To=table(longitude(:),latitude(:),z_seafloor_datum(:),z_water_surf(:),z_gps_datum(:));
writetable(To,[odir 'PPK_Heave_Corrected_Trackline_Data' fs2 '.txt'])


if make_maps_ppk
    %%



   

    % RegularizeData3D needs to be downloaded from the matlab file exchange
    %
    figure(22);clf
    scatter3(x,y,z,12,z,'filled');
    view(2)
    hold on
    colorbar
   cm1=bone(64);
   cm2=flipud(pink(40));
  cm=[cm1(1:58,:);(cm2(6:40,:))];
  colormap(cm)
    caxis([prctile(fillmissing(z,'linear'),1) prctile(fillmissing(z,'linear'),99) ])
    % hold on
    % sl=600
    % for ii=1:(floor(length(x)/sl)-3)
    %     fit_inds=[1:sl]+sl+sl*ii
    %     scatter(x(fit_inds),y(fit_inds),12,z(fit_inds),'or');
    %     pause(.1)
    % end
    k=boundary(x(:),y(:),.4);%x and y are track line coordinate vectors in UTM, z is the surface re datum
    plot(x(k),y(k),'k','linewidth',3)
title('PPK GNSS Heave Corrected Trackline Data with boundary for fitting')
    %%
    dx=.00005/4;
    xnodes=(min(x)-dx):dx:(max(x)+dx);
    ynodes=(min(y)-dx):dx:(max(y)+dx);


    sff= 6e-04;
     %  sff=3e-04;
    [Zg3,Xg3,Yg3]=RegularizeData3D(x ,y,z,xnodes,ynodes,'smoothness',sff);
    [m,n]=size(Zg3);
    BW=roipoly(Xg3(1,:),Yg3(:,1),Zg3,x(k),y(k));
    BW=double(BW);
    BW(BW==0)=NaN;


    DEM=GRIDobj(Xg3,Yg3,Zg3.*BW);
    set(gca,'dataaspectratio',[1 1 1])
    %%
    figure(23);clf
    pf=.0015;
    [A,RA,attribA] = readBasemapImage("satellite",[min(ynodes)-pf max(ynodes)+pf],[min(xnodes)-pf max(xnodes)+pf],20);
    mapshow(A,RA);
    hold on
    tag = struct("ImageDescription",attribA);
    [xx,yy]=meshgrid(RA.XWorldLimits(1):RA.CellExtentInWorldX:RA.XWorldLimits(2),[RA.YWorldLimits(1):RA.CellExtentInWorldY:RA.YWorldLimits(2)]');
    [lat,lon] = projinv(RA.ProjectedCRS,xx,yy);
    %
    figure(23);clf
    surf(lon,flipud(lat),-10*ones(size(lat)),'FaceColor','texturemap','EdgeColor','none','CData',A);
    shading flat
    view(2)
    %
    %figure(31);clf
    hold on

    %surf(DEM,[-15:.25:0])

    caxis([prctile(fillmissing(z,'linear'),1) prctile(fillmissing(z,'linear'),99) ])
    title(['Survey ' fs]);
    hold on
    %plot(x,y,'.k');
    sf =1;
    hs=scatter(x(1:sf:end),y(1:sf:end),4,z(1:sf:end),'o');
    %hs.MarkerEdgeColor='k'
    %cc=flipud(cc);
    colormap(cm);
    hc=colorbar;
    hc.Label.String='Z re datum (m)';
    xlabel('Lon (Deg)');
    ylabel('Lat (Deg)');
    %print -dpng Dem&Track_5_5_23
    mrg=.0005;
    xaxis([min(xnodes)-mrg max(xnodes)+mrg]);
    yaxis([min(ynodes)-mrg max(ynodes)+mrg]);
    map_aspect_ratio(gca);
    print('-dpng',[godir 's6_Track_only_5_5_23'  fs2]);

    %%
    figure(25);clf


    %contour(DEM,[],'caxis',[-18 -7],'colorbar',1,'colormap',cm,'ticklabels','nice','exaggerate',1,...
    %   'colorbarylabel','Elevation (M)')
    zl=([prctile(fillmissing(z,'linear'),1) prctile(fillmissing(z,'linear'),99) ]);

    tanakacontour(DEM,[zl(1):.5:zl(2)])
    %caxis([-14 -3]-wgsz)
    caxis(zl);
    title(['Yellow Fin Survey ' fs] )
    hold on
    %plot(x,y,'.k');
    contour(DEM,[0 0],'R');

    sf =20;
    %hs=scatter(x(1:sf:end),y(1:sf:end),4,z(1:sf:end),'o')
    %hs.MarkerEdgeColor='k'
    %cc=flipud(cc);
    colormap(cm);
    hc=colorbar;
    hc.Label.String='Z re datum (m)';
    xlabel('Lon (Deg)');
    ylabel('Lat (Deg)');
    print('-dpng',[godir 's6_PPK_Contours_'  fs2]);




    %%
    fn=[ 's6_PPK_GPS_DEM_' fs2 '.tif'];
    save([odir fn(1:end-4), 'DEM'])


    GRIDobj2geotiff(DEM,[godir fn])	;
    [A,R] = readgeoraster([godir fn]);
    GRIDobj2geotiff(DEM,[godir fn])	;

    %geotiffwrite('Truro_HOM_topobathy_March2020',A,R,'CoordRefSysCode',26919)%PCS_NAD83(2011)_UTM_zone_19N =	6348,VerticalDatumGeoKey Vertical CS Type Codes:VertCS_North_American_Vertical_Datum_1988 =	5103
    %  DD=GRIDobj('sea2dunet.tif')
    geotiffwrite([godir fn],A,R,'CoordRefSysCode',6318);
end