 global Data PlotData Ms
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
% Ms = 834   %Py (specific measured value for b300a-4)
Ms = 798   %Py (specific measured value for b455)
% Ms = 1400  %estimated for Co
% Ms = 477     %estimated for Ni
dofilt = 0
% fixHk = 9.9  %Py (specific mesured value for b300a-4)
fixHk = 5  %Py mean measured value for b455
% fixHk = 25  %guesstimated for Co
% fixHk = 25  %guesstimated for Ni
% set Ks manually, no Ks fit at present
% Ks = -0.27;    %Py b300a-4
% Ks = -0.28;    %Py b455
Ks = -0.21;    %Py b470 --assumed the mean of b279 and b455 (-.15 -.28)/2; as 1 Py/Pt and 1 Si/Py (about same as SiO2/Py or Py/PR!) interface
% Ks = -0.17;    %Cu/Py/Cu b261-4

if fixHk ~= 0, Hk = fixHk;,end 

 
 if dofilt == 1
% do a simple "filter" filtering
   n = 3;
   b = ones(1,2*n);
   freqorg = freq;, chiorg = chi;
   chi = filter(b,sum(b),chi);
   in1 = 1:(801-n);
   in2 = (n+1):801;
   freq = freq(:,in1);
   chi = chi(:,in2);
   clear b in1 in2
% do a Fourier transform filtering
%   chiunfiltered = chi;, frequnfiltered = freq;
%   fchi = fft(chi.');
%   cutoffval = 32;
%   wid = 5;
%   clear filt
%   filt(:,1) = 1./(1 + exp(((1:400)' - cutoffval)./wid));
%   filt = [1; filt; flipud(filt)];
%   sz = size(fchi);
%   filtfchi = zeros(sz);
%   for n = 1:sz(2)
%     filtfchi(:,n) = filt.*fchi(:,n);
%   end
%   chi = (ifft(filtfchi)).';
%   trunc = find(freq(1,:) > 3.6e9);
%   freq(:,trunc) = [];
%   chi(:,trunc) = [];
 end
 
 if (exist('fitfighandle') ~= 1)  fitfighandle = chifitgui;, else figure(fitfighandle), end;
 range = find(freq(1,:) > 1e9);
 sz = size(chi);
 for n = 1:sz(1)
   H = field(n);
   sprintf('%s%s\t%s%s\t%s%s','line: ',num2str(n),'field: ',num2str(H),'thickness: ',num2str(thick(n)))
%    if thick(n) > 300e-10
%      if H > 40
%        range = find(freq(n,:) > 1e9);
%      elseif H > 0
%        range = find(freq(n,:) > 7e8);
%      elseif H == 0
%        range = find(freq(n,:) > 4e8);
%      else
%        sprintf('%s','There is a problem with the range to fit');
%      end
%    else
%      switch H
%        case 90
%          range = find(freq(n,:) > 2.2e9);
         cla,reset(gca)
         if dofilt == 1      
           tmphandle = plot(freqorg(n,:),real(chiorg(n,:)),freqorg(n,:),imag(chiorg(n,:)),freq(n,:),real(chi(n,:)),'k',freq(n,:),imag(chi(n,:)),'k');
         elseif dofilt == 0
% tmphandle = plot(freq(n,:),abs(chi(n,:)));                                      % to plot magnitude (abs) or phase (angle) of chi.
           tmphandle = plot(freq(n,:),real(chi(n,:)),freq(n,:),imag(chi(n,:)));
         else
           display('Problem with dofilt (should be 0/1)');
         end
         coordlim = ginput(2);
         range = find((freq(n,:) > coordlim(1,1)) & (freq(n,:) < coordlim(2,1)));
         delete(tmphandle)
%        case 80
%          range = find(freq(n,:) > 2.0e9);
%        case 70
%          range = find(freq(n,:) > 1.7e9);
%        case 60
%          range = find(freq(n,:) > 1.6e9);
%        case 50
%          range = find(freq(n,:) > 1.5e9);
%        case 40
%          range = find(freq(n,:) > 1.3e9);
%        case 30
%          range = find(freq(n,:) > 1.1e9);
%        case 20
%          range = find(freq(n,:) > 0.9e9);
%        case 10
%          range = find(freq(n,:) > 0.7e9);
%        case 0
%          range = find(freq(n,:) > 0.4e9);
%          otherwise
%            range = find(freq(n,:) > 1e9);
%            disp('There is a problem with your field value!');
%      end
%    end
     
   Data = [];
   PlotData = [];
   Data = [(freq(n,range')).' (chi(n,range')).'];
   PlotData = [(freq(n,:)).' (chi(n,:)).'];
   chifit;
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
 
 if dofilt == 1
   chi = chiorg;
   freq = freqorg; 
   clear chiorg freqorg;
 end
 

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
 talpha = thick.*alpha;

