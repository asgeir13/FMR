% fit real part of the susceptibility with alpha as fit parameter
% and using Levenberg-Marquardt nonlinear regression.
% Names:
% relmafit.m (this file): real L-M alpha fit
% relmafitf.m           : fitfunction to fit real part
%
% Use numerical partial derivatives, i.e. dfdp.m.
%
global verbose e m c g Ms Dxbar Dybar H w wrud wr
verbose=1;
%
t = fa;
data= chia(:,2);
wt1=(1+0*t)./sqrt(data);  % = 1 /sqrt of variances of data
%
options=[[1e-20] [.01]];
[f1,p1,kvg1,iter1,corp1,covp1,covr1,stdresid1,Z1,r21]=...
  leasqr(t,data,[0.1],...
'relmafitf',1e-20,500,wt1,[1],'dfdp',options);
