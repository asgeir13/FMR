function [Infstruct,Zarr,Sarr] = permload;
%function [Infarr,Zarr] = permload;
%returns Zarr an array of triplets of vectors, freq, res and react read by readdmpm.m
%and Infstruct a STRUCTURE of CELLS with basic information from dmpm dat files.
nfiles = input('How many files total?  ');
strdate = input('Input namebase (date):  ');
Zarr = [];
Infarr = {''};
Sarr = [];
for n=1:nfiles
   [Info,Z,S] = readdmpm(strdate,n);
   Zarr = [Zarr Z];
   Sarr = [Sarr S];
   Infstruct(n).filename = Info{1};
   Infstruct(n).savedate = Info{2};
   Infstruct(n).savetime = Info{3};
end
