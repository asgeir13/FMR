function gibbs(action)
  global Data
  
  switch(action)
    case 'plot'
      Data = [];
      xvec = get(findobj('tag','xaxis'),'string');
      yvec = get(findobj('tag','yaxis'),'string');
      reim = get(findobj('tag','reim'),'value');
      if reim == 0
        evalin('base',['Data(:,1) = ' xvec ';, Data(:,2) = real(' yvec ');']);
        eval('Data(:,3) = fft(Data(:,2));, Data(:,4) = Data(:,3);, Data(:,5) = Data(:,2);');
      elseif reim == 1
        evalin('base',['Data(:,1) = ' xvec ';, Data(:,2) = imag(' yvec ');']);
        eval('Data(:,3) = fft(Data(:,2));, Data(:,4) = Data(:,3);, Data(:,5) = Data(:,2);');
      else
        disp('There is a problem with real/imag in plot callback');
      end
      plot(Data(:,1),Data(:,2))
    case 'cutoff'
      Data(:,4) = Data(:,3);
      cutoffval = round(get(gcbo,'value'));
      wid = get(findobj('tag','width'),'value');
      set(findobj('tag','cutofftxt'),'string',num2str(cutoffval));
      set(findobj('tag','widthtxt'),'string',num2str(wid));
      filt(:,1) = 1./(1 + exp(((1:400)' - cutoffval)./wid));
      filt = [1; filt; flipud(filt)];
      Data(:,4) = filt.*Data(:,3);
      Data(:,5) = real(ifft(Data(:,4)));
      plot(Data(:,1),Data(:,2),Data(:,1),Data(:,5),'r')
      figure(2)
      plot((1:400)',filt(2:401),(1:801)',abs(Data(:,3)).^2/max(abs(Data(:,3)).^2))
      set(gca,'xlim',[0 50])
      shg
      figure(1)
    case 'width'
      Data(:,4) = Data(:,3);
      cutoffval = round(get(findobj('tag','cutoff'),'value'));
      wid = get(findobj('tag','width'),'value');
      set(findobj('tag','cutofftxt'),'string',num2str(cutoffval));
      set(findobj('tag','widthtxt'),'string',num2str(wid));
      filt(:,1) = 1./(1 + exp(((1:400)' - cutoffval)./wid));
      filt = [1; filt; flipud(filt)];
      Data(:,4) = filt.*Data(:,3);
      Data(:,5) = real(ifft(Data(:,4)));
      plot(Data(:,1),Data(:,2),Data(:,1),Data(:,5),'r')
      figure(2)
      plot((1:400)',filt(2:401),(1:801)',abs(Data(:,3)).^2/max(abs(Data(:,3)).^2))
      set(gca,'xlim',[0 50])
      shg
      figure(1)
    end
    
