% Only two terraces I successfully got signal from in the B424-1 terrace sample.
% Thickness is according to the calibration by LR, i.e. not measured magnetically.

field = [];,thick = [];, spar = [];,freq = []; infdata = [];
t=1e-10*[
500
% 137
];	    


cd /home/sthi/usr/exp/suscept/cobrown/b424_1terrace/1/eaz
[tmpinf,tmpf,tmps] = sload(23,'c');
tmpf=(linspace(tmpf(1),tmpf(1601),1601))';
[field,thick,spar,freq,infdata] = appendb42401eaz(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);


cd /home/sthi/usr/exp/suscept/cobrown/b424_1terrace/

stochib42401

