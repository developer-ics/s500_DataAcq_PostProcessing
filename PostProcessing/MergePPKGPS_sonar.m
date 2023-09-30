
% MERGEGPS_SONAR Summary of this function goes here
dirstr='01-11-2023'
dirstr='12-21-2022' % with emlid ppk GPS saved and processed
dirstr='01-05-2023'

GPS=load(['nmea' dirstr '.mat']) % comes from readNMEAfiles.m

PPKGPS=load('PPK20230105141705.mat'); % comes from read_emlid_LLH_raw.m

%% compare gps data to make sure timing is ok
figure(1);clf
plot(GPS.gps_time)
hr=floor(GPS.gps_time(:)/10000);
mm=floor(rem(GPS.gps_time(:)./10000,1).*100);
ss=rem(GPS.gps_time(:)./100,1).*100;
GPS.mat_time=datetime(str2num(dirstr(end-3:end)),str2num(dirstr(1:2)),str2num(dirstr(4:5)),...
    hr,mm,ss);

pc_time_off=GPS.pc_time_gga(1)-GPS.mat_time(1)

plot(GPS.mat_time,GPS.lat,'.')
hold on
gps_leap_offset=seconds(18);%should be 19 but 18 lines it up!
plot(PPKGPS.datetime1-gps_leap_offset,PPKGPS.lat,'r')
plot(PPKGPS.datetime_ppk-gps_leap_offset,PPKGPS.lat_ppk,'g')


%%

if 0 % use the matlab bed deection from profile data
S=load(['profile_data' dirstr '.mat'])
sonar_time=S.dt_profile
sonar_range=S.bed_detect_range';
end

if 1 % use the cerulean instantaenous bed detection since not sure about delay with smoothed
S1=load(['detected_range' dirstr '.mat'])
sonar_time=S1.dt_txt(:)+hours(5);%convert to UTC
sonar_range=S1.txt_depth(:);
end
%%
figure(2);clf
plot(sonar_time,sonar_range,'b')
hold on
plot(GPS.mat_time,GPS.altWGS84,'.g')
hold on
ppk_gpstime=PPKGPS.datetime_ppk-gps_leap_offset;
plot(ppk_gpstime,PPKGPS.height_ell_ppk,'.r')

figure(3);clf
subplot(211)
plot(sonar_range)

subplot(212)
inds=(900:5210)% need to set this manually for each data set
plot(sonar_range(inds))
indsp=near(ppk_gpstime,sonar_time(inds(1))):near(ppk_gpstime,sonar_time(inds(end)));
%%

% code gps
%sonar_range_i=interp1(sonar_time,sonar_range,GPS.pc_time_gga(inds));
%lati=GPS.lat(inds);loni=GPS.lon(inds);

% ppk gps
sonar_range_i=interp1(sonar_time,sonar_range,ppk_gpstime(indsp));
lati=PPKGPS.lat_ppk(indsp);loni=PPKGPS.lon_ppk(indsp);


%% another time sync here by correlating time
figure(40);clf
ws=2100:2400 ;% pick a nice section with a heave effects visble in the echodata and gps

ws2=2000:2500 ;%
% this data doesn't have it so adding artficially
csonar_range_i=sonar_range_i;
csonar_range_i(ws)=csonar_range_i(ws)+.3*sin(ws/10)';

ssr=detrend(csonar_range_i(ws2),'const')+.3*sin(ws2/10)'
hold on
chc=PPKGPS.height_ell_ppk(indsp);
shift=0*pi/4
chc(ws)=(chc(ws)+.3*sin(ws/10+shift)');

sdhc=detrend(chc(ws2)+.3*sin(ws2/10+shift)','const')
subplot(412)
plot(sdhc);
hold on
plot(ssr);
subplot(411)
plot(csonar_range_i)
hold on
plot(chc)


subplot(413)
[r,lags]=xcorr(ssr,sdhc,200,'coeff');
plot(lags,r)

[mx,mi]=max(r);
ml=lags(mi)
s_ssr=interp1(1:length(ssr),ssr,[1:length(ssr) ]+ml);
shifted_sonar_range_i=interp1(1:length(sonar_range_i),sonar_range_i,[1:length(sonar_range_i) ]+ml);

subplot(414)
plot(sdhc);
hold on
plot(s_ssr);
%%
figure(4) ;clf
scatter(loni,lati,16,sonar_range_i)
cc=turbo;
cc=flipud(cc);
colormap(cc)
colorbar
hold on
caxis([7 13])

%%
antenna_offset=.25;
x=loni(:);
y=lati(:);
z=-sonar_range_i(:)+PPKGPS.height_ell_ppk(indsp)-antenna_offset;
dx=.000005;
xnodes=(min(x)-dx):dx:(max(x)+dx);
ynodes=(min(y)-dx):dx:(max(y)+dx);
sff= 2e-04;
[Zg3,Xg3,Yg3]=RegularizeData3D(x ,y,z,xnodes,ynodes,'smoothness',sff);
% RegularizeData3D needs to be downloaded from the matlab file exchange
%%
figure(22);clf
scatter3(x,y,z,12,z,'filled');
view(2)
hold on
% hold on
% sl=600
% for ii=1:(floor(length(x)/sl)-3)
%     fit_inds=[1:sl]+sl+sl*ii
%     scatter(x(fit_inds),y(fit_inds),12,z(fit_inds),'or');
%     pause(.1)
% end
k=boundary(x,y,.3);%x and y are track line coordinate vectors in UTM, z is the surface re navd88
plot(x(k),y(k),'k','linewidth',3)
[m,n]=size(Zg3)
BW=roipoly(Xg3(1,:),Yg3(:,1),Zg3,x(k),y(k));
BW=double(BW);
BW(BW==0)=NaN;


DEM=GRIDobj(Xg3,Yg3,Zg3.*BW);
set(gca,'dataaspectratio',[1 1 1])


%%
figure(31);clf
cm=(ttscm('broc'));
%cm=ttcmap('etopo1')
wgsz=32
  dataMax = -1-wgsz;
  dataMin = -14-wgsz;
  centerPoint = -10-wgsz;
  scalingIntensity = 4;
%Then perform some operations to create your colormap. I have done this by altering the indices “x” at which each existing color lives, and then interpolating to expand or shrink certain areas of the spectrum.
  xm = 1:length(cm);
  xm = xm - (centerPoint-dataMin)*length(xm)/(dataMax-dataMin);
  xm = scalingIntensity * xm/max(abs(xm));
%Next, select some function or operations to transform the original linear indices into nonlinear. In the last line, I then use “interp1” to create the new colormap from the original colormap and the transformed indices.
  xm = sign(xm).* exp(abs(xm));
  xm = xm - min(xm); xm = xm*511/max(xm)+1;
  ncm = interp1(xm, cm, 1:512);

%contour(DEM,[],'caxis',[-18 -7],'colorbar',1,'colormap',cm,'ticklabels','nice','exaggerate',1,...
 %   'colorbarylabel','Elevation (M)')
tanakacontour(DEM,[-14:.25:-2]-wgsz)
%caxis([-14 -3]-wgsz)
title('Yellow Fin survey')
hold on
%plot(x,y,'.k');
sf =10;
hs=scatter(x(1:sf:end),y(1:sf:end),12,z(1:sf:end),'o')
hs.MarkerEdgeColor='k'
%cc=flipud(cc);
colormap(ncm)
hc=colorbar
hc.Label.String='Depth (m)'
xlabel('Lon (Deg)')
ylabel('Lat (Deg)')
print -dpng goodwill_pond