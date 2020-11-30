%load with sload
%infarray
%h vector
%t vector read from t 
%s array
%
%f-dependent phase shift?
%
%do the s -> z conversion
%calculate chi
%
%do initial fminsearch
%
%do leasqr fit
%
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[18  
35  
58  
71  
132 
188 
259 
404 
496 
651 
897 
1047];	    

cd C:\usr\exp\suscept\PyBrown\B261-4\C02L3T1D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C03L3T2D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C04L3T3D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C05L3T4D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C08L2T5D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C08L2T6D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C10L1T7D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C11L2T8D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C12L2T9D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C13L3T10D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(10),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C15L2T11D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(11),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4\C16L3T12D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(12),tmps,tmpf,tmpinf);

 
cd c:\usr\exp\suscept\PyBrown\B261-4
