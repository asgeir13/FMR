function [harr,tarr,sarr,farr,infarr] = appendb455eaz(harr,tarr,sarr,farr,infarr,t,tmps,tmpf,tmpinf);
  
  harr = [harr; (150:-10:20)'];
  tarr = [tarr; ones(14,1)*t];
  sarr = [sarr; tmps.'];         %non-complex conjugate transpose (transpose, not adjoint)
  farr = [farr; ones(14,1)*tmpf'];
  infarr = [infarr; tmpinf];
  
  
  
  
