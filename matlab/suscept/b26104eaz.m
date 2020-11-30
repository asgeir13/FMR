% loads the raw data
% run stochi
% runchifit
field = [];,thick = [];, spar = [];,freq = []; infdata = [];

t=1e-10*[
19  
36  
61  
76  
139 
196 
273 
418 
521 
683 
946 
1095
];	    

% t_nominal
% 30	
% 41	
% 55	
% 74	
% 100	
% 135	
% 182	
% 245	
% 331	
% 447	
% 603	
% 814	

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C02L3T1D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C03L3T2D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C04L3T3D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C05L3T4D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C08L2T5D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C08L2T6D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C10L1T7D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C11L2T8D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C12L2T9D2\eaz  
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C13L3T10D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(10),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C15L2T11D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(11),tmps,tmpf,tmpinf);

cd C:\usr\exp\suscept\PyBrown\B261-4terrace\C16L3T12D2\eaz 
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(12),tmps,tmpf,tmpinf);

 
cd c:\usr\exp\suscept\PyBrown\B261-4terrace
