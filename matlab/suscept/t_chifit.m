
w = Data(:,1);
x = Data(:,2);

global Plothandle Plothandle1 kshape
cla reset;
% plot(ffit,abs(xfit),'y',ffit,abs(xfit),'y',w/(2*pi),abs(x),'r-',w/(2*pi),abs(x),'g-','EraseMode','none');    % to plot magnitude (abs) or phase (angle) of chi.
plot(ffit,real(xfit),'y',ffit,imag(xfit),'y',w/(2*pi),real(x),'r-',w/(2*pi),imag(x),'g-','EraseMode','none');
shg;
hold on
% Plothandle = plot(w/(2*pi),abs(x),'EraseMode','xo');                               % to plot magnitude (abs) or phase (angle) of chi.
Plothandle = plot(w/(2*pi),real(x),'EraseMode','xo');
Plothandle1 = plot(w/(2*pi),imag(x),'EraseMode','xo');
% set(gca,'xlim',[1e8 4e9],'xscale','lin','yscale','lin');
set(gca,'xlim',[coordlim(1,1) coordlim(2,1)],'ylim',[coordlim(1,2)  coordlim(2,2)])

lambda = [];
options = optimset('display','final');
manualfit = 0;  
if fixHk == 0
  % lambda0 = [-1.73e7 9 1e-2 .45];
  lambda0 = [-1.80e7 9.9 1e-2 .1];
  [lambda,x,exitflag,output] = fminsearch('chifitf',lambda0,options,thick,EAHA,fixHk,Ks);
else
  % lambda0 = [-1.73e7 1e-2 .45];
  lambda0 = [-1.80e7 1e-2 .1];
  [lambdaHk,x,exitflag,output] = fminsearch('chifitf',lambda0,options,thick,EAHA,fixHk,Ks);
  lambda = [lambdaHk(1) fixHk lambdaHk(2) lambdaHk(3)];
end
% update once after the fit to show the results for the parameters
update_scrollpan_alpha(lambda,kshape);

% temporarily set manualfit to 1, so always goes to manual
% manualfit = 1;
while manualfit
  if (exist('scrollbarfighandle') ~= 1)  scrollbarfighandle = scrollbargui;, else figure(scrollbarfighandle), end;
  update_scrollpan_alpha(lambda,kshape);
  uiwait
end
figure(fitfighandle);

