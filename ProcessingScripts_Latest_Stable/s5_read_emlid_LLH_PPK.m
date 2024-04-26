


load([odir 's3_START_END_TIMES_' fs2 '.mat'])

%% Read LLH File


file_name=[data_dir '\' ppk_gpsdata_LLH_path]
T=readtable(file_name,'FileType','text');
T.date=datetime(T.Var1,'Inputformat','yyyy/MM/dd');
T.datetime=T.date+T.Var2;
datetime_LLH=T.datetime;
lat=T.Var3;
lon=T.Var4;
figure(14);;clf
hk =plot(lon,lat,'.-k');
title('1st look at EMLID LLH data')
hold on
%% Read PPK *.pos file



file_name=[data_dir '\' ppk_gpsdata_pos_path]

opts = detectImportOptions(file_name,'FileType','text');
opts.DataLines=[11 Inf];
opts.VariableNamesLine=10;
T2p=readtable(file_name,opts);
T2p = renamevars(T2p,'x_','Date');
T2p.date=datetime(T2p.Date,'Inputformat','yyyy/MM/dd');
T2p.datetime=T2p.date+T2p.GPST;
datetime_ppk=T2p.datetime;
datetime_ppk=datetime(datetime_ppk,'TimeZone','UTC');
%% trim inds
ppk_ind_st=near(datetime_ppk,start_time);
ppk_ind_en=near(datetime_ppk,end_time);
ppk_ind=ppk_ind_st:ppk_ind_en;
datetime_ppk_g=datetime_ppk(ppk_ind);

lat_ppk=T2p.latitude_deg_(ppk_ind);
lon_ppk=T2p.longitude_deg_(ppk_ind);
figure(14);
hold on
hg=plot(lon_ppk,lat_ppk,'-g');
title('1st look at EMLID LLH & PPK data')

legend([hk hg],'LLH GNSS data before PPK processing','PPK data')
%%  saves ppk  and q1 only  nav88height data
figure(15);clf
%height_ell_ppk=func_despike_phasespace(T2p.height_m_);
height_datum_ppk=T2p.height_m_+ ell2ortho;
% filter length is 151 / 5=30 s. thresh level of 12 seems to work 

inds=logical(conv((T2p.Q~=1)',ones(13 ,1)','same'));% imdilate (with conv) as points on either side of q 1 transition are often bad

height_datum_ppk(inds)=NaN;


clean_height_datum_ppk=clean0(height_datum_ppk,251,6)  ;
%clean_height_datum_ppk=hampel(T2p.height_m_,251,6) + ell2ortho ;

q1_clean_height_datum_ppk=clean_height_datum_ppk;
%inds=logical(conv((T2p.Q~=1)',ones(13 ,1)','same'));% imdilate (with conv) as points on either side of q 1 transition are often bad

%q1_clean_height_datum_ppk(inds)=NaN;
subplot(311)
plot(datetime_ppk,T2p.height_m_+ ell2ortho,'.-b')
hold on
clean_height_datum_ppk=clean_height_datum_ppk(ppk_ind);
plot(datetime_ppk_g,clean_height_datum_ppk,'-c');
title(" Despiked datum Height");

subplot(312)
plot(datetime_ppk,T2p.height_m_+ ell2ortho,'.-b');
hold on
q1_clean_height_datum_ppk=q1_clean_height_datum_ppk(ppk_ind);
plot(datetime_ppk_g,q1_clean_height_datum_ppk,'-r');
title(" Despiked Q1 datum Height")

%xaxis([6000 8000]);yaxis([-27.5 -25.5])
subplot(313)
hold on
Qf=T2p.Q(ppk_ind);
plot(datetime_ppk_g,Qf,'.-r');
title("GNSS Quality Factor");
xzoom;



%%
fs2=char(datetime(survey_day,'Format','yyyyMMdd'));
mkdir(odir)
save([odir 's5_PPK_GNSS_DATA_' fs2],'lon_ppk','lat_ppk','clean_height_datum_ppk','q1_clean_height_datum_ppk','datetime_ppk_g','Qf','height_datum_ppk')
