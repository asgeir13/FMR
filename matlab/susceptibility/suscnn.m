function [chi,cz] = suscnn(Infstruct,f,S)
%function [chi,cz] = suscnn(Infstruct,f,S)
%input values:
%   Ingstruct: structure containing filenames, savedate, etc.
%   f: frequency vector (assumed all scans loaded are same frequency)
%   S: S11 reflection parameter
%return values:
%   chi:  complex susceptibility matrix (NO NORMALIZATION IN THIS FUNCTION)
%   cz:   complex UNcorrected Z (impedance)
global C
nfiles = length(Infstruct);
z = 50*(1 + S)./(1 - S);
for n=2:nfiles
   cz(:,n-1) = z(:,n) - z(:,1);
end

C2=[C;C;C;C;C];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%A few parameters to calculate Chi (susceptibility of film)
wid=5e-3      %width of fixture 5 mm in m
A=pi*(2e-3)^2/4  %Approximate area of film in m^2
t=871e-10   %800 A film of Permalloy 81/19 from Eugene
%k=.9        %Geometrical factor, from patent of van Dover
%psi=.85     %Geometrical factor, from patent of van Dover
kpsi=.50     %Geometrical factor
mju0=4*pi*1e-7   %"permeability of free space" in SI-system

gamma=4*A*t*mju0*kpsi/(wid^2);   %the 4 is from r_eff = w/2 =>r_eff^3 = w^3/8
%%%Calculate and plot susceptibility according to my measurement
%write chi=chi'+i*chi'' in matlab=> chi=chip+chipp
figure(1),clf;
hold on;
xlabel('f (Hz)','fontsize',18,'fontweight','bold');
ylabel('\chi\prime','fontsize',18,'fontweight','bold');
title('Susceptibility of \alpha2-4; 871 A MRC dc-mag Py film','fontsize',18,'fontweight','bold');
for n=1:(nfiles-1)
   chip(:,n) = (imag(cz(:,n)))./(gamma.*2.*pi.*f);
   chipp(:,n) = (real(cz(:,n)))./(gamma.*2.*pi.*f);
end
chi=chip+i*chipp;
hpchi = plot(f,chip);
%set(gca,'xscale','log','xlim',[1e8 3e9],'ylim',[-7e2 1.7e3],'box','on');
set(gca,'xscale','log','box','on');
%datestamp('tl',2);
figure(2),clf;
hpchi = plot(f,chipp);
%set(gca,'xscale','log','xlim',[1e8 3e9],'ylim',[-1e3 2e3],'box','on');
set(gca,'xscale','log','box','on');
xlabel('f (Hz)','fontsize',18,'fontweight','bold');
ylabel('\chi\prime\prime','fontsize',18,'fontweight','bold');
title('Susceptibility of \alpha2-4; 871 A MRC dc-mag Py film','fontsize',18,'fontweight','bold');
%datestamp('tl',2);
shg

