clear phi alpha x y xx yy zz

H=90;
Hk=12;
%%%%%%%%%%SURFACE/CONTOUR PLOT OF THE CONDITION ON PHI AND COMPARE WITH PHI+ALPHA=PI/2

x=(pi/2:-pi/30:-3*pi/2)';
% x=(0:pi/180:pi/2)';
% y=x;
y=(0:pi/30:2*pi)';
[xx,yy] = meshgrid(x,y);
zz = H*cos(yy+xx) - (Hk/2)*sin(2*yy);

% figure(1)
% clf
% axes
% % axis square
% h0=mesh(xx,yy,zz);
% hold on
% [c,h]=contour(x,y,zz,[0 0],'k');
% set(h,'linewidth',2)
% 
% h1=plot3((pi/2 - x),y,zeros(length(x),1),'r');
% set(h1,'linewidth',2)
% 
% % set(gca,'xlim',[0 pi/2],'ylim',[0 pi/2])
% 
% % view(0,90);
% view(120,20);
% 
% xlabel('\alpha (appl. field angle)')
% ylabel('\phi (equilibrium M-angle)')
% 
% % hidden off
% 
% shg


%%%%%%%%%%%%%%%%%%%%%%SOLVE FOR PHI

% f is the equilibrium condition for phi
% f=inline('(H*cos(phi + alpha) - (Hk/2)*sin(2*phi))','phi','alpha','H','Hk')
f=inline('H*(cos(phi)*cos(alpha) - sin(phi)*sin(alpha)) - Hk*sin(phi)*cos(phi)','phi','alpha','H','Hk')

opt = optimset('display','off')
for n = 1:length(x)
  alpha(n,:) = x(n);
  [phi(n,:),fval,exflag(n,:)] = fzero(f,pi/2 - alpha(n),opt,alpha(n),H,Hk);  
  %   pause
end
if prod(exflag) ~= 1
  display('Didn''t converge in all cases')
end


figure(2),clf
plot(alpha,pi/2 - alpha,'b',alpha,phi,'ro')
xylab('\alpha','\phi; (\pi /2 - \alpha);','')
legend('pi/2-a','phi')


figure(3),clf
oalpha = r2d(alpha);
ophi = r2d(phi);
plot(oalpha,90 - oalpha,'b',oalpha,ophi,'ro')
xylab('\alpha','\phi; (\pi /2 - \alpha)','')
legend('pi/2-a','phi')




shg




