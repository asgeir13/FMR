% loads the raw data
% Next run: stochi
%           runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
300
];	    


cd /home/sthi/usr/exp/suscept/surfparticle/b420_4/as_deposited/eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);


cd /home/sthi/usr/exp/suscept/surfparticle/b420_4/as_deposited/eaz

