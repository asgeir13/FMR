% loads the raw data
% Next run: stochib455eaz
%           runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
300
107
65
47
37
30
];	    

% t_nominal
% Terrace 1
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_2/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_3/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_3/true_eaz_30deg
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

% Terrace 2
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_6/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_6/true_eaz_45deg
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

% Terrace 3
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_9/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_9/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_9/true_eaz_50deg
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

% Terrace 4
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_11/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_11/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_12/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_12/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_12/haz
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

% Terrace 5
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_14/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_14/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_14/haz
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_15/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

% Terrace 6
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_16/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_16/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
% 
cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_16/true_eaz_45deg
[tmpinf,tmpf,tmps] = sload(16,'c');
[field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_17/eaz
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
% 
% cd /home/sthi/usr/exp/suscept/pybrown/b455/b455_17/eaz12nsgate
% [tmpinf,tmpf,tmps] = sload(16,'c');
% [field,thick,spar,freq,infdata] = appendb455eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);


cd /home/sthi/usr/exp/suscept/pybrown/b455
