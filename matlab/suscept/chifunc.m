function out = chifunc(n) 
  global Data f H w Ms
  g = n(1);
  Hk = n(2);
  a = n(3);
  
  Dxbar= Hk/Ms
  Dybar= 4*pi + Hk/Ms

  wr = roots([1 
   -i*g*a*(2*H + (Dybar + Dxbar)*Ms)/(1 + a^2) 
   -g^2*(H + Dybar*Ms)*(H + Dxbar*Ms)/(1 + a^2)]);
   
  wrud = real(wr(2))


  chi = g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./(wrud.^2 - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));
  out = chi';

%  out = g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./...
%  (wrud.^2 - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));
  
  
