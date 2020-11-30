% loads the raw data
% Next run: stochib470eaz
%           runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
100
100
100
100
];	    


cd /home/sthi/usr/exp/suscept/pybrown/b470/b470_1/eaz_12nsgate
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb470eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b470/b470_2/eaz_12nsgate
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb470eaz(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b470/b470_3/eaz_12nsgate
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb470eaz(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b470/b470_4/eaz_12nsgate
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb470eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b470
