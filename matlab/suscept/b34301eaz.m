% Thicknesses are NOMINAL AS OF 08/24/00 at least
% B343-1t1a    thickest; 500 Angstrom
% B343-1t1b
% B343-1t2a
% B343-1t2b
% B343-1t3 
% B343-1t4 
% B343-1t5a    thinnest;  35 Angstrom
% B343-1t5b

 field = [];,thick = [];, spar = [];,freq = []; infdata = [];
 t=1e-10*[
477
475
133
133   %not actually measured, taken same as T2a
74
48
36
39
% nominal,  NOT SURE WHAT ACTUAL THICKNESS IS, MISSING ONE TERRACE!
% 500
% 500
% 137
% 137
% 79
% 56
% 43
% 43
% % 35
];	    


 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t1a\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';                %%%%%%%%NB. HAVE TO FIX THE FREQUENCY AS WHEN THE DATA WAS TAKEN IT WAS RECORDED AS LOGFREQ
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t1b\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t2a\eaz
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t2b\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t3\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t4\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t5a\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);
 
 cd C:\usr\exp\suscept\PyBrown\b343-1terrace\b343-1t5b\eaz  
 [tmpinf,tmpf,tmps] = sload(12,'c');
 tmpf=(linspace(tmpf(1),tmpf(801),801))';
 [field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);
 
  
 cd c:\usr\exp\suscept\PyBrown\b343-1terrace
