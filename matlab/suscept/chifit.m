global Data f H w PlotData


f = Data(:,1);
x = Data(:,2);
w = 2*pi*f;
global Plothandle Plothandle1 kshape
cla reset;
% plot(PlotData(:,1),abs(PlotData(:,2)),'y',PlotData(:,1),abs(PlotData(:,2)),'y',f,abs(x),'r-',f,abs(x),'g-','EraseMode','none');    % to plot magnitude (abs) or phase (angle) of chi.
plot(PlotData(:,1),real(PlotData(:,2)),'y',PlotData(:,1),imag(PlotData(:,2)),'y',f,real(x),'r-',f,imag(x),'g-','EraseMode','none');
shg;
hold on
% Plothandle = plot(f,abs(x),'EraseMode','xo');                               % to plot magnitude (abs) or phase (angle) of chi.
Plothandle = plot(f,real(x),'EraseMode','xo');
Plothandle1 = plot(f,imag(x),'EraseMode','xo');
% set(gca,'xlim',[1e8 4e9],'xscale','lin','yscale','lin');
set(gca,'xlim',[.7*coordlim(1,1) 1.3*coordlim(2,1)])

lambda = [];
options = optimset('display','final');
manualfit = 0;  
if fixHk == 0
  % lambda0 = [-1.73e7 9 1e-2 .45];
  lambda0 = [-1.80e7 9.9 1e-2 .1];
  [lambda,x,exitflag,output] = fminsearch('chifitf',lambda0,options,thick(n),EAHA,fixHk,Ks);
else
  % lambda0 = [-1.73e7 1e-2 .45];
  lambda0 = [-1.80e7 1e-2 .1];
  [lambdaHk,x,exitflag,output] = fminsearch('chifitf',lambda0,options,thick(n),EAHA,fixHk,Ks);
  lambda = [lambdaHk(1) fixHk lambdaHk(2) lambdaHk(3)];
end
% update once after the fit to show the results for the parameters
update_scrollpan_alpha(lambda,kshape);

% temporarily set manualfit to 1, so always goes to manual
manualfit = 1;
while manualfit
  if (exist('scrollbarfighandle') ~= 1)  scrollbarfighandle = scrollbargui;, else figure(scrollbarfighandle), end;
  update_scrollpan_alpha(lambda,kshape);
  uiwait
end
figure(fitfighandle);

