function [harr,tarr,sarr,farr,infarr] = append(harr,tarr,sarr,farr,infarr,t,tmps,tmpf,tmpinf);
  
  n = length(tmpinf);  %number of data files
  harr = [harr; (1:n)'];   %manually set fields later
  tarr = [tarr; ones(n,1)*t];
  sarr = [sarr; tmps.'];         %non-complex conjugate transpose (transpose, not adjoint)
  farr = [farr; ones(n,1)*tmpf'];
  infarr = [infarr  tmpinf];
  
  
  
  
