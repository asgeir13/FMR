function y = relmafitf(x,p);
%
global e m c g Ms Dxbar Dybar H w wrud wr
%
num = g^2*Ms*(H + Dybar*Ms + i.*p(1).*2.*pi.*x./g);
den = wrud.^2 - (2*pi.*x).^2.*(1 + p(1).^2) + i*g*p(1)*(2*H + (Dybar + Dxbar)*Ms)*2*pi.*x;
y=real(num./den);

