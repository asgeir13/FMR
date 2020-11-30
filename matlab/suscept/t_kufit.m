% This function will fit an T-dependent in-plane angular variation FMR-measurement, i.e. fit 
% the resonance frequency as function of field angle.
% It is assumed that data has already been loaded appropriately.

H = Hmag;

wr = 2*pi*fitres;

psi= d2r(90-hang);

phi_func=inline('H*(cos(phi)*cos(psi) - sin(phi)*sin(psi)) - Hk*sin(phi)*cos(phi)','phi','psi','H','Hk');

phi = [];
opt = optimset('display','off');
for n = 1:length(psi)
  [phi(n,:),fval,exflag(n,:)] = fzero(phi_func,pi/2 - psi(n),opt,psi(n),H,Hk);  
  %   pause
end
if prod(exflag) ~= 1
  display('Didn''t converge in all cases')
end
    
% remove points where unable to determine f_res
rmv = [];%find(fitres<3.3e9);% | fitres>4.7e9);
psifit=psi;,psifit(rmv)=[];
phifit=phi;,phifit(rmv)=[];
wrfit=wr;,wrfit(rmv)=[];


%%%%%%%%%% DO THE FITTING %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

global Data
Data=[];
% Data(:,1) = phifit - d2r(0);  %shift the data to make it symmetric; appears to be hardware problem  
Data(:,1) = phifit;
Data(:,2) = wrfit;

global Plothandle
cla reset;
plot(r2d(Data(:,1)),Data(:,2),'r.','EraseMode','none');
shg;
hold on
Plothandle = plot(r2d(Data(:,1)),Data(:,2),'EraseMode','normal');
set(gca,'xlim',200*[-1 1])

%%%%%%%%%%%%%%%GIVE SOME VALUES TO PARAMETERS
% define the gamma value as variable g
e=-4.8032e-10;%  cgs
m=9.109e-28;%   [g] cgs
c=3e10;%       [cm/s]
g=geff*e/(2*m*c);%  gamma

%%%%%%%%%%%%%%%OTHERS ARE PRESUMABLY TAKEN CARE OF EARLIER

lambda = [];
lambda0 = [Hk 0];
% lambda0 = [Hk Ms 0];
opt = optimset('display','final','maxfunevals',10000,'tolfun',1e-20);
[lambda,x,exitflag,output] = fminsearch('t_kufitf',lambda0,opt,H,Ms,Hs,psifit,g);
% [lambda,x,exitflag,output] = fminsearch('t_kufitf',lambda0,opt,H,Ms,psifit,g);
% [lambda,x,exitflag,output] = fminsearch('t_kufitf',lambda0,opt,H,psifit,g);
% [lambda,x,exitflag,output] = fminsearch('t_kufitf',lambda0,opt,H,psifit);

lambda
if length(lambda) >= 4
  geff = 2*m*c*lambda(4)/e
else 
  geff = 2*m*c*g/e
end

Hk = lambda(1);
% Ms = lambda(2);
shang = lambda(2);
sprintf('%s%g\t%s%g\t%s%g\t%s%g','Results:  H_k = ',Hk,';H_s = ',Hs,';M_s = ',Ms,'shift_angle = ',shang)

Data = [phi wr];
wrescalc = t_kufitfplot(lambda,H,Ms,Hs,psi,g);
% clear global Data
% figure
% plot(r2d(phifit) - shang,wrfit/(2*pi*1e9),'r.',r2d(phi) - shang,wrescalc/(2*pi*1e9),'b-')
% xylab('\phi ( ^\circ )','f_{res} (GHz)','')
% set(gca,'xtick',[-180:90:180],'ytick',[2.6:.1:3])
% drawnow
shg
