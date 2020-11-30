%[y,inda]=max(imag(ca))
for n=2:11
   hd(n-1)=plot(fra(n-1),imag(ca(inda(n-1),n)),'r.','markersize',15)
   %plot(fa,imag(ca(:,n))),shg,pause
end
