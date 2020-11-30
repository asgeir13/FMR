% This was written to compare the shift in wr according to theory, with the measured shift.
% This doesn't quite make sense, sinse we know that for thin samples the effect of damping 
% becomes important, and the most sensible thing to plot would be the fitted value, which 
% of course perfectly reproduces the measured value by nature of the plot!
% 
% this is currently used for b261, so length of t or range in rng e.g. must be altered for other samples
wrcalc = zeros(size(t));
rng = 2:12;
% gammamean = 2.029*egamma/2
gammamean = 2.039*egamma/2
wr2calc = inline('gammamean.^2.*(H + 4*pi*Ms + Hk + 4*Ks*x/(1e2*Ms)).*(H + Hk)','x','gammamean','H','Ms','Hk','Ks');
d = 1e-10*((1/30:1/50*(1/2000-1/30):1/2000).^(-1))'
wr2data = wr2calc(1./d,gammamean,H,Ms,Hk,Ks);

clf
plot(1e-10./t(rng),manwres(rng).^2,'.',1e-10./d,wr2data,'-')
shg



