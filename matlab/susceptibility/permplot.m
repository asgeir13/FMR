function [f] = permplot(Infstruct,Z)
global C
%function permplot(Infstruct,Z)
%accepts Infstruct a structure containing info from dat files and
%Z an array of triplets of freq, res and react from these files.
figure(1),clf,axes,box on
s = size(Z);
nfiles = length(Infstruct);
subplot(2,1,1)
for n = 0:(nfiles-1)
   hp1(n+1) = line(Z(:,n*3 + 1),Z(:,n*3 + 2));
end
subplot(2,1,2)
for n = 0:(nfiles-1)
   hp2(n+1) = line(Z(:,n*3 + 1),Z(:,n*3 + 3));
end

C2=[C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C;C];
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%A few parameters to calculate Chi (susceptibility of film)
wid=5e-3      %width of fixture 5 mm in m
A=pi*(2e-3)^2/4  %Approximate area of film in m^2
t=871e-10   %800 A film of Permalloy 81/19 from Eugene
k=.9        %Geometrical factor, from patent of van Dover
psi=.85     %Geometrical factor, from patent of van Dover
mju0=4*pi*1e-7   %"permeability of free space" in SI-system

gamma=4*A*t*mju0*k*psi/(wid^2);   %the 4 is from r_eff = w/2 =>r_eff^3 = w^3/8
%%%Calculate and plot susceptibility according to my measurement
%write chi=chi'+i*chi'' in matlab=> chi=chip+chipp
figure(2),clf;
hold on;
subplot(2,1,1);
ylabel('\chi\prime','fontsize',18,'fontweight','bold');
title('Susceptibility of 871 A MRC dc-mag Py film','fontsize',18,'fontweight','bold');
for n = 1:(nfiles-1), 
   chip(:,n) = (Z(:,n*3 + 3) - Z(:,3))./(gamma.*2.*pi.*Z(:,n*3 + 1));
   chipp(:,n) = (Z(:,n*3 + 2) - Z(:,2))./(gamma.*2.*pi.*Z(:,n*3 + 1));
%   chip(:,n) = (Z(:,(n-1)*3 + 3))./(gamma.*2.*pi.*Z(:,(n-1)*3 + 1));
%   chipp(:,n) = (Z(:,(n-1)*3 + 2))./(gamma.*2.*pi.*Z(:,(n-1)*3 + 1));
   hpchi(n) = line(Z(:,n*3 + 1),chip(:,n));
   set(hpchi(n),'color',C2(n,:),'marker','*');
end
set(gca,'xscale','log','xlim',[1e8 1e10],'box','on');
subplot(2,1,2);
for n = 1:(nfiles - 1),
   hpchi(n) = line(Z(:,n*3 + 1),chipp(:,n));
   set(hpchi(n),'color',C2(n,:),'marker','*');
end
set(gca,'xscale','log','xlim',[1e8 1e10],'box','on');
xlabel('f (Hz)','fontsize',18,'fontweight','bold');
ylabel('\chi\prime\prime','fontsize',18,'fontweight','bold');
shg
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

f=[];
res=[];
react=[];
st=size(Z);
for n=1:(st(2)/3)
   f(:,n) = Z(:,3*(n-1) + 1);   
   res(:,n) = Z(:,3*(n-1) + 2);   
   react(:,n) = Z(:,3*(n-1) + 3);
end

