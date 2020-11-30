function out = omegar(g,a,H,Dxbar,Dybar)
% function out = omegar(g,a,H,Dxbar,Dybar)
% 
% Calculates FMR resonance angular frequency, returning two roots which
% are "anti"-complex conjugates.
%
global Ms
out = roots([1
   -i*g*a*(2*H + (Dybar + Dxbar)*Ms)/(1 + a^2)
   -g^2*(H + Dybar*Ms)*(H + Dxbar*Ms)/(1 + a^2)]);
