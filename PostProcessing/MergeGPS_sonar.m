
% MERGEGPS_SONAR Summary of this function goes here
dirstr='01-11-2023'
dirstr='12-21-2022' % with emlid ppk GPS saved and processed
dirstr='01-05-2023'

GPS=load(['nmea' dirstr '.mat'])
if 0 % use the matlab bed deection from profile data
S=load(['profile_data' dirstr '.mat'])
sonar_time=S.dt_profile
sonar_range=S.bed_detect_range';
end

if 1 % use the cerulean instantaenous bed detection . Not sure about delay with smoothed
S1=load(['detected_range' dirstr '.mat'])
sonar_time=S1.dt_txt(:);
sonar_range=S1.txt_depth(:);
end
%%
figure(1);clf
plot(sonar_time,sonar_range)
hold on
plot(GPS.pc_time_gga,GPS.altMSL)


figure(2);clf
subplot(211)
plot(sonar_range)

subplot(212)
inds=(900:5210)% need to set this manually for each data set
plot(sonar_range(inds))
%%

sonar_range_i=interp1(sonar_time,sonar_range,GPS.pc_time_gga(inds));

lati=GPS.lat(inds);loni=GPS.lon(inds);
figure(3) ;clf
scatter(loni,lati,16,sonar_range_i)
cc=turbo;
cc=flipud(cc);
colormap(cc)
colorbar
hold on
caxis([7 13])

%%
x=loni(:);
y=lati(:);
z=-sonar_range_i(:);
dx=.000005;
xnodes=(min(x)-dx):dx:(max(x)+dx);
ynodes=(min(y)-dx):dx:(max(y)+dx);
sff= 3e-04;
[Zg3,Xg3,Yg3]=RegularizeData3D(x ,y,z,xnodes,ynodes,'smoothness',sff);
% RegularizeData3D needs to be donwloaded from the matlab file exchange
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
  dataMax = -1;
  dataMin = -14;
  centerPoint = -10;
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
tanakacontour(DEM,[-14:.25:-2])
caxis([-14 -3])
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