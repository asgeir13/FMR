ztmp = 50*gamma2z(spar);
% % rotate imill-sample to take into account phase change.
% tmp = zeros(192,160);
% tmp(:,1) = 1;
% ftmp = tmp*freq;
% fmax = freq(1,801);
% th = -.07.*2.*pi.*ftmp./fmax;
% ztmp = ztmp.*exp(-i.*th);
% clear tmp th fmax ftmp
% % end of rotation

z=[];
sz = size(ztmp);
for n = 1:sz(1)
  a = mod(n,16);
  if ((a > 2) | (a == 0))
% z(n-((floor((n-1)/16)+1)*2),:) = ztmp(n,:);
% s(n-((floor((n-1)/16)+1)*2),:) = spar(n,:);
z(n-((floor((n-1)/16)+1)*2),:) = ztmp(n,:);% - ztmp((floor((n-1)/16)*16+1),:);
  end
end



%%%A few parameters to calculate Chi (susceptibility of film)
%Sample holder dimensions in SI
% This holder (#5) was made on 10/31/01, sthi
wid = 1.9e-3;      %width of holder
len = 3.7e-3;       %length of holder (one way)
hei = .05842e-3;       %height of holder
Area = pi*(2e-3)^2/4;    %Area of film dot in m^2

mju0=4*pi*1e-7;   %"permeability of free space" in SI-system

prefac = 8*mju0*Area*len*hei/(wid^4);   %This version documented in labnotebook on 990604

sz = size(z);
for n = 1:sz(1)
  const = thick(n)*prefac;
  chip = (imag(z(n,:)))./(const.*2.*pi.*freq(n,:));
  chipp = (real(z(n,:)))./(const.*2.*pi.*freq(n,:));
  chi(n,:) = (chip + i*chipp)/(4*pi);     %The 4*pi is to convert into cgs units (gaussian)
end

clear chip chipp ztmp const sz


















