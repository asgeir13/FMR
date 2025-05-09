function err = chifitf(n)
  global Data H w Ms

%Stolid fra matlab demo
%

global Plothandle Plothandle1 c

f = Data(:,1);
x = Data(:,2);

  g = n(1);
  Hk = n(2);
  a = n(3);
  kshape = n(4);
  
  Dxbar= Hk/Ms;
  Dybar= 4*pi + Hk/Ms;

  wr = roots([1 
   -i*g*a*(2*H + (Dybar + Dxbar)*Ms)/(1 + a^2) 
   -g^2*(H + Dybar*Ms)*(H + Dxbar*Ms)/(1 + a^2)]);
   
  wrud = abs(real(wr(1)));
  
%****************
 
%  mu0 = 4*pi*1e-7;
%  wsample = .0031115; 
%  lsample = .003683; 
%  hsample = .001016;
  
%  prefac = (8 * mu0 * adot * tdot * lsample * hsample ) / wsample^4


chi = g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./(wrud.^2 - ...
      w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));

z = kshape*chi - x;


set(Plothandle,'ydata',real(chi))
set(Plothandle1,'ydata',imag(chi))
drawnow
err = norm(z);




