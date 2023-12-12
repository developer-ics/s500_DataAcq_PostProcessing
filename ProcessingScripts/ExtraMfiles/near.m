function [index,distances]=near(x,x0);
%function [index,distance]=near(x,x0);
%     x is an array, x0 is a point.  Distance is the abs(x-x0)
index=findmin(abs(x-x0));
distance=abs(x(index)-x0);
distances=(x(index)-x0);
index=index(1);
end
function n=findmin(x);
n=find(x==ming(x));
end

function a=ming(b);
g=find(isfinite(b(:)));
a=min(b(g));

if length(g)==0;
   a=nan;
end;
end
