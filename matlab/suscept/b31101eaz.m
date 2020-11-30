% Thicknesses are NOMINAL AS OF 08/22/00 at least
% B311-1T1a  thickest; 800 Angstrom
% B311-1t1b
% B311-1t2b
% B311-1t3 
% B311-1t4 
% B311-1t5 
% B311-1T6   thinnest;  83 Angstrom

 field = [];,thick = [];, spar = [];,freq = []; infdata = [];
 t=1e-10*[
% nominal
800
800
293
180
129
101
83
];	    


 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t1a\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';                %%%%%%%%NB. HAVE TO FIX THE FREQUENCY AS WHEN THE DATA WAS TAKEN IT WAS RECORDED AS LOGFREQ
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t1b\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t2b\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t3\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t4\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t5\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b311-1terrace\b311-1t6\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);
 
  
 cd c:\usr\exp\suscept\PyBrown\b311-1terrace
