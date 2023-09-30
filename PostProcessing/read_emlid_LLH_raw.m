fs='20221221165017';
fs='20230105141705';
if ispc
    slash = '\';
else
    slash = '/';
end

dirnm=['SampleData' slash 'YF2Reachm2_solution_' fs '_LLH']
dd=dir(dirnm);
fn=[dirnm slash dd(3).name];% this is before ppk processing so should agree with nmea strings
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
dirnm=['SampleData' slash 'YF2Reachm2_raw_' fs '_RINEX_3_03']


dd=dir(dirnm)
fn=[dirnm slash 'YF2Reachm2_raw_' fs '.pos']% note the e-file has a slightly modifed header to allow matalab to read the varaible names
opts = detectImportOptions(fn,'FileType','text');
opts.DataLines=[11 Inf];
opts.VariableNamesLine=10;

T2=readtable(fn,opts);
T2 = renamevars(T2,'x_','Date')
T2.date=datetime(T2.Date,'Inputformat','yyyy/MM/dd');
T2.datetime=T2.date+T2.GPST;
datetime_ppk=T2.datetime;
lat_ppk=T2.latitude_deg_;
lon_ppk=T2.longitude_deg_;
figure(10);
hold on
plot(lon_ppk,lat_ppk,'.-g')

figure(11);clf
height_ell_ppk=T2.height_m_;
plot(T2.height_m_)
hold on
plot(10*T2.Q)

plot(10000*(T2.latitude_deg_-T2.latitude_deg_(1)))
save(['PPK' fs],'lon_ppk','lat_ppk','height_ell_ppk','datetime_ppk','lat','lon','datetime1')
