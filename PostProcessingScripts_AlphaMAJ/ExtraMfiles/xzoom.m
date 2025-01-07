
function xzoom(V)
%xzoom see also xzoom colorbar
xl=xlim;
chil=get(gcf,'chil')
%pos=get(gca,'pos')



for ii=1:length(chil)
    if ~(strcmpi(get(chil(ii),'Tag'),'Colorbar')||strcmpi(get(chil(ii),'Tag'),'legend'))
        if strcmp(get(chil(ii),'Type'),'axes')
%get(chil(ii)) 
   set(chil(ii),'xlim',xl);
  % pause
        end
    end
end