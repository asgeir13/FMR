function [f,z,x] = chifitf_returnf(n,t,EAHA,fixHk,Ks)
  global Data f H w Ms

% 4/19/00 sthi
%

  global Plothandle Plothandle1 kshape

  f = Data(:,1);
  x = Data(:,2);
  A = zeros(length(f),1);

  if fixHk == 0 
    g = n(1);
    Hk = n(2);
    a = n(3);
    kshape = n(4);
  else
    g = n(1);
    Hk = fixHk;
    a = n(2);
    kshape = n(3);
  end

  %  %%%TAKE INTO ACCOUNT INTERFACE ANISOTROPY ACCORDING TO QUICK ESTIMATE from (wres/gamma)^2, then improve until gamma becomes ~constant.
  %  %%%sthi 3/5 2000
  % Ks = -4.95e-1;
% Ks = -0.28;

  if EAHA == 0
    Dxbar= Hk/Ms;
    % Dybar= 4*pi + Hk/Ms;
    Dybar= 4*pi + Hk/Ms + 2*2*Ks/(1e2*t*Ms^2);     %1e2 in Ks term to convert t to cm; Ms^2 because Dybar multiplies with Ms everywhere. 2*(2Ks/(Md)) because of two surfaces.
    % It seems that breaking up the evaluation of the fitfunction affects the fitting!
    % A(:,1) = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./(wrud.^2 - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));
    A(:,1) = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./(g^2.*(H + Dybar.*Ms).*(H + Dxbar.*Ms) - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));
  %  display('EA')
  elseif EAHA == 1
    Dxbar= -Hk/Ms;
    % Dybar= 4*pi;
    Dybar= 4*pi + 2*2*Ks/(1e2*t*Ms^2);     %1e2 in Ks term to convert t to cm; Ms^2 because Dybar multiplies with Ms everywhere.  2*(2Ks/(Md)) because of two surfaces.
    %  %%%%%MUST FIX THIS FOR HA FIT, THIS IS THE EA EQUATION
    A(:,1) = kshape.*g^2.*Ms.*((H + Dybar.*Ms) + i.*w.*a./g)./(g^2.*(H + Dybar.*Ms).*(H + Dxbar.*Ms) - w.^2.*(1 + a.^2) + i.*w.*g.*a.*(2.*H + (Dxbar + Dybar).*Ms));
    display('HA---MUST FIX THE EQUATION FOR THIS FIT, THIS IS THE EA-EQUATION')
  else
    display('There is a problem with your EA/HA selection (in function runchifit.m); should be 0<->EA/1<->HA')
  end
  
% kshape = A\x;
% z = A*kshape;
z=A;
% set(Plothandle,'ydata',abs(z))                               % to plot magnitude (abs) or phase (angle) of chi.
  set(Plothandle,'ydata',real(z))
  set(Plothandle1,'ydata',imag(z))
  drawnow
  err = norm(z-x);
   



