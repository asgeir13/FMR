 global Data Ms H
 Data = [];
 nlc = [];
 lc = [];
 out = [];
 exit = [];
 
 %electron constants in cgs units
 echarge = 4.803e-10;
 emass = 9.109e-28;
 cspeed = 2.9979e10;
 egamma = -echarge/(emass*cspeed);

 
% EAHA = input('EA/HA = 0/1:  ');
% Ms = input('Magnetization, Ms (emu/cm^3) = ');
% dofilt = input('Fourier cutoff filtering? (0/1):  ');
% fixHk = input('Fix value of Hk? (0 not fixed/nonzero value of Hk):  ');
% Ks = input('Surface anisotropy constant, Ks (erg/cm^2):  ');
%% Lazy parameter settings
EAHA = 0
% Ms = 834   %Py (specific measured value for b300a-4)    %MUST READ Ms AS FUNCTION OF T FROM VECTOR NOW.
% Ms = 798   %Py (specific measured value for b455)
% Ms = 1400  %estimated for Co
% Ms = 477     %estimated for Ni
% fixHk = 9.9  %Py (specific mesured value for b300a-4)    %MUST READ H_k AS FUNCTION OF T FROM VECTOR NOW.
% fixHk = 5  %Py mean measured value for b455
% fixHk = 25  %guesstimated for Co
% fixHk = 25  %guesstimated for Ni
% set Ks manually, no Ks fit at present
% Ks = -0.27;    %Py b300a-4
% Ks = -0.28;    %Py b455
Ks = -0.21;    %Py b470 --assumed the mean of b279 and b455 (-.15 -.28)/2; as 1 Py/Pt and 1 Si/Py (about same as SiO2/Py or Py/PR!) interface
% Ks = -0.17;    %Cu/Py/Cu b261-4

% if fixHk ~= 0, Hk = fixHk;,end 

 
 if (exist('fitfighandle') ~= 1)  fitfighandle = chifitgui;, else figure(fitfighandle), end;
 for n = 1:length(ia)
   [ffit,xfit]=vecselpair(f,chi,ia,n);
   range = find(ffit > 0.7e9);    %get rid of lowest frequency noise:
   ffit=ffit(range);, xfit=xfit(range);
   H = des_h(n);
   short_vector_ind = find(set_temp == des_t(n))
   fixHk = H_k(short_vector_ind);
   Ms = M(short_vector_ind);
   sprintf('%s%s\t%s%s\t%s%s','line: ',num2str(n),'field: ',num2str(H),'temperature: ',num2str(des_t(n)))
   cla,reset(gca)
%    if dofilt == 1      
%      tmphandle = plot(freqorg(n,:),real(chiorg(n,:)),freqorg(n,:),imag(chiorg(n,:)),freq(n,:),real(chi(n,:)),'k',freq(n,:),imag(chi(n,:)),'k');
%    elseif dofilt == 0
   tmphandle = plot(ffit,real(xfit),ffit,imag(xfit));
%    else
%      display('Problem with dofilt (should be 0/1)');
%    end

% coordlim = ginput(2);
   coordlim = [fr(n)-0.7e9   1.1*min([min(real(xfit))   min(imag(xfit))])        %1.1 since the min is usually negative.
               fr(n)+0.7e9   1.1*max([max(real(xfit))   max(imag(xfit))]) ];
   range = find((ffit > coordlim(1,1)) & (ffit < coordlim(2,1)));
   delete(tmphandle)
     
   Data = [];  %most reliable way to initialize this global variable.
   Data = [2*pi*ffit(range') xfit(range')];
   t_chifit;
   nlc = [nlc lambda'];
   lc = [lc; kshape];
   out = [out; output];
   exit = [exit; exitflag];
 %  pause
 end
 
 cl = input('OK to clear fit/scroll-figures? (0=no clear) ');
 if isempty(cl)
   delete(fitfighandle)
   if exist('scrollbarfighandle') == 1
     delete(scrollbarfighandle)
     clear scrollbarfighandle
   end
   clear fitfighandle
 end
 
%  if dofilt == 1
%    chi = chiorg;
%    freq = freqorg; 
%    clear chiorg freqorg;
%  end
 

 if EAHA == 0
   Dxbar= Hk/Ms;
   Dybar= 4*pi + Hk/Ms + 2*2*Ks/(1e2*t*Ms^2);     %1e2 in Ks term to convert t to cm; Ms^2 because Dybar multiplies with Ms everywhere. 2*(2Ks/(Md)) because of two surfaces.
 elseif EAHA == 1
   Dxbar= -Hk/Ms;
   Dybar= 4*pi + 2*2*Ks/(1e2*t*Ms^2);     %1e2 in Ks term to convert t to cm; Ms^2 because Dybar multiplies with Ms everywhere.  2*(2Ks/(Md)) because of two surfaces.
 else
   display('There is a problem with your EA/HA selection (in function runchifit.m); should be 0<->EA/1<->HA')
 end
 
 wres = [];,wthe = [];
 for n = 1:sz(1)
   wtmp = omegar(nlc(1,n),nlc(3,n),field(n),Dxbar,Dybar(n));
   wres(n,:) = abs(real(wtmp(1)));
   wtmp = omegar(2.1*egamma/2,0,field(n),Dxbar,Dybar(n));           %calculated with a g-factor of 2.1 (as observed for the thicker samples).
   wrud(n,:) = abs(real(wtmp(1)));   %theoretical undamped wFMR
 end

 alpha = nlc(3,:)';


