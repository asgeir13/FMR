% Written so that one can just graphically click with mouse to find the resonance frequency
sz = size(chi);
for n = 1:sz(1)
  cla,reset(gca)
  plot(freq(n,:),real(chi(n,:)),freq(n,:),imag(chi(n,:)),freq(n,:),abs(chi(n,:)))
  % allow user to zoom in on graph  
  disp('pick lower-left/upper-right hand corners of zoom window...')
  zm = ginput(2);
  set(gca,'xlim',[zm(1,1) zm(2,1)],'ylim',[zm(1,2) zm(2,2)])
  coord = ginput(1);
  manwres(n,:) = 2*pi*coord(1);
  manchiampl(n,:) = coord(2);
  % get the linewidth
  % zm = ginput(2);
  % deltaf(n) = zm(2,1) - zm(1,1);
end
