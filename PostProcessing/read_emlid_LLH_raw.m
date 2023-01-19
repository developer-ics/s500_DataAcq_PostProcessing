fs='20221221165017';
fs='20230105141705';
dirnm=['YF2Reachm2_solution_' fs '_LLH']

dd=dir(dirnm)
fn=[dirnm '\' dd(3).name]% this is before ppk processing so should agree with nmea strings
T=readtable(fn,'FileType','text');
T.date=datetime(T.Var1,'Inputformat','yyyy/MM/dd');
T.datetime=T.date+T.Var2;
datetime1=T.datetime;
lat=T.Var3;
lon=T.Var4;
figure(10);;clf
hold on
plot(lon,lat,'o-m')


%%
dirnm=['.\YF2Reachm2_raw_' fs '_RINEX_3_03']


dd=dir(dirnm)
fn=[dirnm '\YF2Reachm2_raw_' fs '.pos.txt']% note the e-file has a slightly modifed header to allow matalab to read the varaible names
T2=readtable(fn,'FileType','text');
T2.date=datetime(T2.GPST,'Inputformat','yyyy/MM/dd');
T2.datetime=T2.date+T2.time;
datetime_ppk=T2.datetime;
lat_ppk=T2.latitude;
lon_ppk=T2.longitude;
figure(10);
hold on
plot(lon_ppk,lat_ppk,'.-g')

figure(11);clf
height_ell_ppk=T2.height;
plot(T2.height)
hold on
plot(10*T2.Q)

plot(10000*(T2.latitude-T2.latitude(1)))
save(['PPK' fs],'lon_ppk','lat_ppk','height_ell_ppk','datetime_ppk','lat','lon','datetime1')
