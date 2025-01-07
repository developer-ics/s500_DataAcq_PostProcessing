function ny=clean0(y,ms,ex)
% function ny=clean(y,ms,ex)
% CLEAN Performs robust cleaning of y
% ex is scaling of std for cleaning
% ms is odd number of points in median fliter
%
if (nargin==1), ms=3;ex=1; end;
if (nargin==2), ex=1; end;


if (rem(ms,2)~=1), error('median filter length must be an ODD number');end;

[Ny,My]=size(y);
y=y(:)';
N=max(Ny,My);

ny=y;

yy=zeros(ms,N-ms+1);
ym=zeros(1,N);

for i=1:ms,              % Do the middle bits
  yy(i,:)=y(i:N-ms+i);
end;
ym(fix(ms/2)+1:N-fix(ms/2))=median(yy,'omitmissing'); 

for i=1:fix(ms/2),       % Fix the ends
   ym(i)=median(y(1:ms),'omitmissing');
   ym(N-i+1)=median(y(N-ms:N),'omitmissing');
end;

%smad=median(abs(y-ym)');    % MAD
smad=median(abs(y-ym)','omitmissing');    % MAD


ii=find(abs(y-ym)> ex*smad);  % Guess the outliers

ny(ii)=ym(ii);               % replace outliers with interpolated values.
%figure
%plot(1:N,y,'r',1:N,ny,'b',ii,ny(ii),'.b');

ny=reshape(ny,Ny,My);


