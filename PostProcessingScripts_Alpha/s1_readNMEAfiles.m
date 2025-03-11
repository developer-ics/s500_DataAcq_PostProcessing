
v = ver
navtoolbox =any(strcmp(cellstr(char(v.Name)), 'Navigation Toolbox'))

dd=dir([dirstr1 '\*.dat'])
for ii=1:length(dd)
    disp([num2str(ii) ' ' (dd(ii).name)])
end
ji=0;
ji2=1
pnmea = nmeaParser("MessageIDs", 'GGA')
pnmeaRMC = nmeaParser("MessageIDs", 'RMC')

for fi=2:length(dd) %
    disp([dirstr1 '\' dd(fi).name])
   

    %fid=fopen([dirstr dd(fi).name]);
    lns=readlines([dirstr1 '\' dd(fi).name]);
    for ii=1:length(lns);

        ln=lns{ii};
        if ~isempty(ln)
            datestring=ln(4:29);
            try
                dt(ii)=datetime(char(datestring),'InputFormat','yyyy-MM-dd HH:mm:ss.SSSSSS');
            catch
                continue
            end

            nmcode=ln(31:35);
            nmdata=ln(30:end);

            if ~navtoolbox
                if strmatch(nmcode,'GNGGA')

                    ji2=ji2+1;
                    Str=ln(30:end);
                    str1 = regexprep(Str,'[,;=]', ' ');
                    str2 = regexprep(regexprep(str1,'[^- 0-9.eE(,)/]',''), ' \D* ',' ');
                    str3 = regexprep(str2, {'\.\s','\E\s','\e\s','\s\E','\s\e'},' ');
                    str4=regexprep(str3,'E','');
                    numArray = str2num(str4);
                    if length(numArray)>=3
                        gps_utc_time1a(ji2)=numArray(1);
                        gps_utc_time(ji2)=datetime(0,0,0,0,0,0,'TimeZone','UTC');
                        gps_utc_time(ji2).Hour=  floor(gps_utc_time1a(ji2)./1e4);
                        gps_utc_time(ji2).Minute= floor(rem(gps_utc_time1a(ji2),10000)./1e2);
                        gps_utc_time(ji2).Second= rem(gps_utc_time1a(ji2),100);
                        if ~isempty(strfind(str1,"W"))
                            lons=-1;
                        elseif  ~isempty(strfind(str1,"E"))
                            lons=1;
                        end
                        if ~isempty(strfind(str1,"N"))
                            lats=1;
                        elseif  ~isempty(strfind(str1,"S"))
                            lats=-1;
                        end
                        lat(ji2)=lats.*(floor(numArray(2)/100)+(numArray(2)-floor(numArray(2)/100)*100)./60);
                        lon(ji2)=lons.*(floor(numArray(3)/100)+(numArray(3)-floor(numArray(3)/100)*100)./60);
                        altMSL(ji2)=numArray(7);
                        GeoidSeparation(ji2)=numArray(8);
                        altWGS84(ji2)=   altMSL(ji2)+  GeoidSeparation(ji2);

                        pc_time_gga(ji2)=dt(ii);
                        gps_utc_time(ji2).Year=year(dt(ii));
                        gps_utc_time(ji2).Month=month(dt(ii));
                        gps_utc_time(ji2).Day=day(dt(ii));


                    end
                end

            elseif navtoolbox
                ggaData=pnmea(nmdata);
                rmcData=pnmeaRMC(nmdata);
                if rmcData.Status==0
                    rmcday=day(rmcData.UTCDateTime);
                    rmcmonth=month(rmcData.UTCDateTime);
                    rmcyear=year(rmcData.UTCDateTime);
               % elseif rmcData.Status==2
                  %   rmcday=17;
                  %  rmcmonth=10;
                  %  rmcyear=2024;
                end
               if ggaData.Status==0&exist('rmcday')
                    ji=ji+1;
                    gps_utc_time(ji)=datetime(ggaData.UTCTime,'TimeZone','UTC');% this is UTC

                    lat(ji)=ggaData.Latitude;
                    lon(ji)=ggaData.Longitude;
                    altWGS84(ji)=ggaData.Altitude-ggaData.GeoidSeparation;
                    altMSL(ji)=ggaData.Altitude;
                    GeoidSeparation(ji)=ggaData.GeoidSeparation;
                    pc_time_gga(ji)=dt(ii);% this is pc(rasbpi) time when gga sentences are recived
                    gps_utc_time(ji).Day=rmcday;
                    gps_utc_time(ji).Month=rmcmonth;
                    gps_utc_time(ji).Year=rmcyear;



                end
            end
        end
    end
end



%%
if 0
    lat(lat==0)="NaN";
    lon(lon==0)="NaN";

    figure(1);clf
    plot(lon,lat,'o-')
    figure(2);clf
    plot(pc_time_gga,altWGS84,'.-')
    hold on
    plot(pc_time_gga,altMSL,'.-')
    figure(3)
    subplot(211)
    plot(pc_time_gga,gps_time,'.')

    subplot(212)
    plot(seconds(datetime(pc_time_gga,'TimeZone','America/New_York')-gps_time),'.')
end
fs2=char(datetime(survey_day,'Format','yyyyMMdd'))

outname=[odir 's1_NMEA_GNSS_DATA_' fs2]
save(outname,'pc_time_gga','gps_utc_time','lat','lon','altMSL','altWGS84','GeoidSeparation')

%%


