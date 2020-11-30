variables = [];
for nn=1:4
  varstr = strcat('var',int2str(nn));
  valstr = strcat('val',int2str(nn));
  minstr = strcat('min',int2str(nn));
  maxstr = strcat('max',int2str(nn));
  resstr = strcat('res',int2str(nn));
  variables(nn) = findobj('tag',varstr);
  values(nn) = findobj('tag',valstr);
  minvals(nn) = findobj('tag',minstr);
  maxvals(nn) = findobj('tag',maxstr);
  resolutions(nn) = findobj('tag',resstr);
end

vr = {'g';'Hk';'a';'kshape'};
% vl = [1 
for nn=1:4
  set(variables(nn),'string',char(vr(nn)));
end


