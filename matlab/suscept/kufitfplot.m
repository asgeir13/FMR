% function funcval = Kufitf(la,H,Ms,Hs,psi,g)
function funcval = Kufitf(la,H,Hs,psi,g)
% function funcval = Kufitf(la,H,psi,g)
% function funcval = Kufitf(la,H,psi)
  global Data
%
% 4/19/00 sthi
%

  
  % shiftangle
  shang = la(3);

  phi = Data(:,1) - d2r(shang);
  wr = Data(:,2);
  z = zeros(length(phi),1);

  Hk = la(1);
% Hs = la(2);
Ms = la(2);
% g = la(4);

  
  c1 = H*sin(phi + psi) + 4*pi*Ms + Hs;
  c2 = H*sin(phi + psi);
   
  z(:,1) = sqrt(g.^2*(Hk*(cos(phi)).^2 + c1).*(Hk*cos(2*phi) + c2));

  funcval = z;


