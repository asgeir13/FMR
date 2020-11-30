function [harr,tarr,sarr,farr,infarr] = append(harr,tarr,sarr,farr,infarr,t,tmps,tmpf,tmpinf);
  
  harr = [harr; (90:-10:0)'];
  tarr = [tarr; ones(10,1)*t];
  sarr = [sarr; tmps.'];         %non-complex conjugate transpose (transpose, not adjoint)
  farr = [farr; ones(10,1)*tmpf'];
  infarr = [infarr; tmpinf];
  
  
  
  
