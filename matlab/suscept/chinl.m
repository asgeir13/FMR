global Data f H w Ms
H = 90;
Ms = 805;


f = Data(:,1);
x = Data(:,2);
w = 2*pi*f;
global Plothandle Plothandle1 c
cla reset;
plot(f,real(x),'r-',f,imag(x),'g-','EraseMode','none');
shg;
hold on
Plothandle = plot(f,real(x),'EraseMode','xo');
Plothandle1 = plot(f,imag(x),'EraseMode','xo');
set(gca,'xscale','log','yscale','lin');
n0 = [-1.73e7 8 1e-2 .5];
[n,x,exitflag,output] = fminsearch('chinlf',n0);

%set(Plothandle,'ydata',real(x))
%set(Plothandle1,'ydata',imag(x))
