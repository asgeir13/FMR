% loads the raw data
% Next run: stochib45002eaz
%           runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
% 800
% 333
% 211
% 154
121
121
% 100
];	    

% t_nominal

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c9t4d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);


cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace
