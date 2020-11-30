function [Infstruct,fvec,Scarr] = s11sload(varargin);
%function [Infarr,fvec,Scarr] = sload({nfiles,strdate});
%returns fvec, frequency vector, and Scarr, complex S11S array read by reads11sdmpm.m
%and Infstruct a STRUCTURE of CELLS with basic information from dmpm dat files.
%input is optional, if none then user is prompted at command line.
%sthi 0699.
if isempty(varargin)
   nfiles = input('How many files total?  ');
   strdate = input('Input namebase:  ');
else
   nfiles = varargin{1};
   strdate = varargin{2};
end
Infarr = {''};
fvec = [];
Scarr = [];
for n=1:nfiles
   [Info,fvec,S] = reads11sdmpm(strdate,n);
   Scarr = [Scarr S];
   Infstruct(n).filename = Info{1};
   Infstruct(n).savedate = Info{2};
   Infstruct(n).savetime = Info{3};
end
