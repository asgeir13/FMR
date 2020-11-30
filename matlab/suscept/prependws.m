function prependws(pref,varargin)
% function prependws(pref,excl{optional})
%  
% Written to compare two different workspaces (e.g. EA and HA data for same sample or
% to compare different samples) with same variable names in both spaces.
%
% Takes following var's:
%        pref:  string variable to prepend to all variables in workspace
%        excl:  any number of comma seperated string variables, exclude 
%               variables starting with this string
%
% Intended for use with e.g. "cplot.m"
% 
% last change: 4/18 2000 sthi
%

clear wh
wh = evalin('base','who');

if ~isempty(varargin)
  for n = 1:length(varargin)
    ind = strmatch(varargin{n},wh);
    wh(ind) = [];
  end
end

for n = 1:length(wh)
  str = strcat(pref,char(wh(n)));
  evalin('base',[str, '=',char(wh(n)), ';']);
  evalin('base',['clear ', char(wh(n)),';']);
end
  

  
  
