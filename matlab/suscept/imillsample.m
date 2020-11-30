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

t=1e-10*[990	    
907	    
785	    
670	    
573	    
488	    
463	    
366	    
323	    
246	    
246	    
246	    
246	    
171	    
127	    
82]	    

cd c:\usr\exp\suscept\pyionmill\perm\990520\990520b
[tmpinf,tmpf,tmps] = sload(12,'990520b');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(1),tmps,tmpf,tmpinf);

cd ..\..\990602
[tmpinf,tmpf,tmps] = sload(12,'990602a');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(2),tmps,tmpf,tmpinf);

cd ..\990615\eaz
[tmpinf,tmpf,tmps] = sload(12,'f');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(3),tmps,tmpf,tmpinf);

cd ..\..\990616
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(4),tmps,tmpf,tmpinf);

cd ..\990618\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(5),tmps,tmpf,tmpinf);

cd ..\..\990621\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(6),tmps,tmpf,tmpinf);

cd ..\..\990622
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(7),tmps,tmpf,tmpinf);

cd ..\990624\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(8),tmps,tmpf,tmpinf);

cd ..\..\990625\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(9),tmps,tmpf,tmpinf);

cd ..\..\990628\a3_3
[tmpinf,tmpf,tmps] = sload(12,'a');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(10),tmps,tmpf,tmpinf);

cd ..\..\990630garb
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(11),tmps,tmpf,tmpinf);

cd ..\990701
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(12),tmps,tmpf,tmpinf);

cd ..\990702\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(13),tmps,tmpf,tmpinf);

cd ..\..\990706\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(14),tmps,tmpf,tmpinf);

cd ..\..\990708\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(15),tmps,tmpf,tmpinf);

cd ..\..\990712\eaz
[tmpinf,tmpf,tmps] = sload(12,'c');
[field,thick,spar,freq,infdata] = append(field,thick,spar,freq,infdata,t(16),tmps,tmpf,tmpinf);

 
cd c:\usr\exp\suscept\pyionmill\perm
