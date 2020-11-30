% written to plot a Bode plot of the frequency response of chi_xx
% SAMPLE B261-4
% 
figure(1),clf
% semilogx(2*pi.*freq(3,:)',20*log10(abs(chi(3,:).'))-8)
figure(2),clf
% semilogx(2*pi.*freq(7,:)',r2d(angle(chi(7,:).')))
Ms = 800
Ks = -.27
% g = -1.83e7 
Hk = 9 
% a = .8e-2
% a = [.001:.005:.1]'
% a = .015
% kshape = .45
% t=1e-10*[10:30:310]'
% t=1000e-10

Dxbar= Hk/Ms;
Dybar= 4*pi + Hk/Ms + 2.*2.*Ks./(1e2.*t.*Ms.^2);     %1e2 in Ks term to convert t to cm; Ms^2 because Dybar multiplies with Ms everywhere. 2*(2Ks/(Md)) because of two surfaces.

cxx=[];,c0=[];,w=[];
% w = 2*pi*freq;
w = logspace(8,11,2000)';

wres=[];,w0=[];
% for n = 1:length(a)
%   cxx(:,n) = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a(n)./g)./(g^2.*(H + Dybar.*Ms).*(H + Dxbar.*Ms) - w.^2.*(1 + a(n).^2) + i.*w.*g.*a(n).*(2.*H + (Dxbar + Dybar).*Ms));
%   wtmp = zeros(size(w));
%   c0(:,n) = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*wtmp.*a(n)./g)./(g^2.*(H + Dybar.*Ms).*(H + Dxbar.*Ms) - wtmp.^2.*(1 + a(n).^2) + i.*wtmp.*g.*a(n).*(2.*H + (Dxbar + Dybar).*Ms));
%   wtmp = omegar(g,a(n),H,Dxbar,Dybar);
%   wres(n) = abs(real(wtmp(1)));
%   wtmp = omegar(g,0,H,Dxbar,Dybar)
%   w0(n) = abs(real(wtmp(1)))
% end
for n = 1:length(t)
  g=nlc(1,n);
  a=alpha(n);
  kshape=nlc(4,n);
% 
  cxx(:,n) = kshape.*g^2.*Ms.*((H + Dybar(n).*Ms) + i.*w.*a./g)./(g^2.*(H + Dybar(n).*Ms).*(H + Dxbar.*Ms) - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar(n)).*Ms));
  wtmp = zeros(size(w));
  c0(:,n) = kshape.*g^2.*Ms.*((H + Dybar(n).*Ms) + i.*wtmp.*a./g)./(g^2.*(H + Dybar(n).*Ms).*(H + Dxbar.*Ms) - wtmp.^2.*(1 + a.^2) + i.*wtmp.*g.*a.*(2.*H + (Dxbar + Dybar(n)).*Ms));
  wtmp = omegar(g,a,H,Dxbar,Dybar(n));
  wres(n) = abs(real(wtmp(1)));
  wtmp = omegar(g,0,H,Dxbar,Dybar(n))
  w0(n) = abs(real(wtmp(1)))
end

% num = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g);
% den = g^2.*(H + Dybar.*Ms).*(H + Dxbar.*Ms) - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms);


col = [1 .53 0]; % orange
% col = 'g'
figure(1),hold on
% semilogx(w/(2*pi),20*log10(abs(cxx)) - 20*log10(abs(c0)),'color',col)
semilogx(w/(2*pi),abs(cxx),'color',col)
% semilogx(w/(2*pi),imag(cxx),'color',col)
xylab('\omega (rad/s)','|\chi_{xx}| dB',['100Cu/946Py/100Cu (' angst ')'])
% set(gca,'xlim',[1e9 1e11])
% m=[];,m=max(20*log10(abs(cxx)) - 20*log10(abs(c0)));
m=[];,m=max(abs(cxx));
for n=1:length(wres)
  hp = line(w0(n)/(2*pi)*[1;1],m(n)*[1;1]);
  set(hp,'marker','.','markersize',10,'linestyle','none','color','b')
  hp = line(wres(n)/(2*pi)*[1;1],m(n)*[1;1]);
  set(hp,'marker','.','markersize',10,'linestyle','none','color','r')
end

shg
pause
figure(2),hold on
semilogx(w,r2d(angle(cxx)),'color',col)
xylab('\omega (rad/s)','\angle\chi_{xx} ( {}^\circ )',['100Cu/946Py/100Cu (' angst ')'])
set(gca,'xlim',[1e9 1e11],'ylim',[-20 200],'ytick',[0:45:180])
shg
% pause
% semilogx(w',r2d(angle(num)),w',r2d(angle(den)),w',r2d(angle(num)) - r2d(angle(den)))





