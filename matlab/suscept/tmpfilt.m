% Intended to test smoothing of s-parameter using "filter" function
% filter
% stoz
% plot raw and smoothed
 figure(1),clf,box on
 subplot(2,1,1) 
 plot(f,real(s),'g.')
 subplot(2,1,2)
 plot(f,imag(s),'g.') 
 n = 3;
 b = ones(1,2*n);
 sm = filter(b,sum(b),s);
 in1 = 1:(801-n);
 in2 = (n+1):801;
 subplot(2,1,1) 
 hold on
 plot(f(in1),real(sm(in2)),'r')
 set(gca,'ylim',[-1.001 -.998])
 subplot(2,1,2)
 hold on
 plot(f(in1),imag(sm(in2)),'r')
 shg

