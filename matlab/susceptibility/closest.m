function index=closest(f,xval)
%function index=closest(f,xval)
%finds the index of the value in vector f closest to the value xval,
%returns index into f.
%
%sthi 6/10 '99
%
t=abs(f-xval);
index=find(t==min(t));
if length(index)>1
   disp('There are multiple minima of f-xval');
end
