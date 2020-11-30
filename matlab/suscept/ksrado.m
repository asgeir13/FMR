g = 2.1;
e = 4.8e-10;
m = 9.1e-28;
c = 3e10;
ga = g*e/(2*m*c);
Ks = .2;         %erg/cm^2 tentatively (not for Py)
A = 5.5e-7;      %erg/cm tentatively (not for Py)
Ms = 811;

%Ks*(k3*sinh(k3*t/2)*cosh(k1*t/2) - v31*k1*sinh(k1*t/2)*cosh(k3*t/2)) - ...
%A*k1*k3*(1 - v31)*sinh(k1*t/2)*sinh(k3*t/2);


tpm = 2*pi*Ms;
H = 90;
%thick = 1e-10*[1000;800;500;300;200;150;110;100;50];
for n = 1:length(trado)
  par = (tpm^2 + (wrado(n)/ga)^2)^(1/2);
  k1 = sqrt((Ms/(2*A))*(H + tpm - par));
  k3 = sqrt((Ms/(2*A))*(H + tpm + par));
  v31 = - (par + tpm)/(par - tpm);
  Ks(n,:) =  -A*k1*k3*(1 - v31)*sinh(k1*trado(n)/2)*sinh(k3*trado(n)/2)/(k3*sinh(k3*trado(n)/2)*cosh(k1*trado(n)/2) - v31*k1*sinh(k1*trado(n)/2)*cosh(k3*trado(n)/2));
  n
end









