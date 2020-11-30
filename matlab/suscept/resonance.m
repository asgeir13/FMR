ind = find(field == 90);
for n = 1:length(ind)
  plot(freq(ind(n),:),imag(chi(ind(n),:)),freq(ind(n),:),real(chi(ind(n),:)))
  lims=axis;
  fr = wres(ind(n))/(2*pi);
  line([fr; fr],[lims(3); lims(4)])
  shg
  pause
end
