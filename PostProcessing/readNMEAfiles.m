clear
dirstr='01-05-2023n';
outname=[ 'nmea' dirstr(3:end-1)]';  % matfile output

if ispc
    slash = '\';
else
    slash = '/';
end

dd=dir(['SampleData' slash dirstr slash '*.dat']);
for ii=1:length(dd)
    disp([num2str(ii) ' ' (dd(ii).name)])
end
    ji=0;

for fi=2:length(dd) %5  20201218-101925265.bin ios new 500 khz
    [dirstr dd(fi).name];
    %fid=fopen([dirstr dd(fi).name]);
    lns=readlines(['SampleData' slash dirstr slash dd(fi).name]);
    for ii=1:length(lns);
        
        ln=lns{ii};
        if ~isempty(ln)
        datestring=ln(4:29);
        dt(ii)=datetime(char(datestring),'InputFormat','yyyy-MM-dd HH:mm:ss.SSSSSS');
        nmcode=ln(31:35);
%         if strmatch(nmcode,'GNRMC')
%             ji=ji+1;
%             Str=ln(30:end);
%             str1 = regexprep(Str,'[,;=]', ' ');
%         str2 = regexprep(regexprep(str1,'[^- 0-9.eE(,)/]',''), ' \D* ',' ');
%         str3 = regexprep(str2, {'\.\s','\E\s','\e\s','\s\E','\s\e'},' ');
%         str4=regexprep(str3,'E','');
%         numArray = str2num(str4);
%         if length(numArray)>=3
%         gps_time(ji)=numArray(1);
%         lat(ji)=floor(numArray(2)/100)+(numArray(2)-floor(numArray(2)/100)*100)./60;
%         lon(ji)=floor(numArray(3)/100)+(numArray(3)-floor(numArray(3)/100)*100)./60;
%         pc_time_gga(ji)=dt(ii);

        if strmatch(nmcode,'GNGGA')
            ji=ji+1;
            Str=ln(30:end);
            str1 = regexprep(Str,'[,;=]', ' ');
        str2 = regexprep(regexprep(str1,'[^- 0-9.eE(,)/]',''), ' \D* ',' ');
        str3 = regexprep(str2, {'\.\s','\E\s','\e\s','\s\E','\s\e'},' ');
        str4=regexprep(str3,'E','');
        numArray = str2num(str4);
        if length(numArray)>=3
        gps_time(ji)=numArray(1);
        lat(ji)=floor(numArray(2)/100)+(numArray(2)-floor(numArray(2)/100)*100)./60;
        lon(ji)=-(floor(numArray(3)/100)+(numArray(3)-floor(numArray(3)/100)*100)./60);
        altWGS84(ji)=numArray(8);
        altMSL(ji)=numArray(7);
        pc_time_gga(ji)=dt(ii);

        end
        end
        end
    end
end
%%
lat(lat==0)="NaN";
lon(lon==0)="NaN";

figure(10);clf
plot(lon,lat,'o-')
figure(11);clfs
plot(pc_time_gga,altWGS84,'.-')
hold on
plot(pc_time_gga,altMSL,'.-')

save(outname,'pc_time_gga','gps_time','lat','lon','altMSL','altWGS84')

    
