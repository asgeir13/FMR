
Dxbar= Hk/Ms;%   Dxbar = (Dx + Dkx - Dz - Dkz)
Dybar= 4*pi + Hk/Ms;%   anisotropy, shape and crystalline

wr=omegar(0);
wrud=wr(1);
frud=wrud/(2*pi);
wr=omegar(a);
fr=wr/(2*pi);
cxx=zeros(length(w),1);
cxx = chixx(a);

set(findobj('tag','EditText6'),'string',num2str(real(fr(2))));
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%A few parameters to calculate Chi measured(susceptibility of film)
gamma=4*A*t*mju0*kpsi/(wid^2);   %the 4 is from r_eff = w/2 =>r_eff^3 = w^3/8
%%%Calculate and plot susceptibility according to my measurement
%write chi=chi'+i*chi'' in matlab=> chi=chip+chipp
chip = (imag(cz))./(gamma.*2.*pi.*fm);
chipp = (real(cz))./(gamma.*2.*pi.*fm);
chim=chip+i*chipp;

%************************ plotting **************************
if get(findobj('tag','Radiobutton1'),'value')==0
   set(hp1,'ydata',angle(cxx));
   set(hpm,'ydata',unwrap(angle(chim))-4*pi);
%   set(hp1,'ydata',real(cxx));
%   set(hpm,'ydata',real(chim));
else
   set(hp1,'ydata',imag(cxx));
   set(hpm,'ydata',imag(chim));
end



