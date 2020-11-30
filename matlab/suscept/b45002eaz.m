% loads the raw data
% Next run: stochib45002eaz
%           runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
2000
% 800
333
211
154
121
100
100  %b433-1-4
67   %b433-3-4
50   %b433-4-4
];	    

% t_nominal

cd /home/sthi/usr/exp/suscept/nibrown/b450_4/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c1t1d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c3t2d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c6t3d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c9t4d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c9t4d2/eazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c9t4d2/oldholdereazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c12t5d2/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace/c12t5d2/eazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b433_1_4/xymagneteazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b433_3_4/xymagneteazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);

cd /home/sthi/usr/exp/suscept/nibrown/b433_4_4/xymagneteazgate
[tmpinf,tmpf,tmps] = sload(23,'c');
[field,thick,spar,freq,infdata] = appendb45002eaz(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);



cd /home/sthi/usr/exp/suscept/nibrown/b450_2terrace
