% load with sload
% infarray
% h vector
% t vector read from t 
% s array
% 
% f-dependent phase shift?
% 
% do the s -> z conversion
% calculate chi
% 
% do initial fminsearch
% 
% do leasqr fit

 field = [];,thick = [];, spar = [];,freq = []; infdata = [];
 t=1e-10*[
 % from AGM-results
 26
 40
 57
 59
 65
 95
 177
 184
 532
 771 
% 30
% 33
% 36
% 41
% 46
% 54
% 64
% 78
% 102
% 145
% 254
% 500
% 711
 ];	    

% The terraces for this sample (B279-2) were labelled from 0-12 (rather than 0-13)

 
%  cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C6L3T5d2\haz  
%  [tmpinf,tmpf,tmps] = sload(12,'c');
% % [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
%  [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C8L2T6d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C8L3T6d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C9L2T7d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C10L3T8d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C12L2T9d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(10),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C13L2T10d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(11),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C14L3T11d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(12),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\B279-2terrace\C15L3T12d2\haz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
% [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(13),tmps,tmpf,tmpinf);
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(10),tmps,tmpf,tmpinf);

  
 cd c:\usr\exp\suscept\PyBrown\B279-2terrace
