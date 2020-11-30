function hp = cplot(strstruct,xvar,yvar,varargin) 
%  function hp = cplot(strstruct,xvar,yvar,newfigure(optional))
%    Written to plot susceptibility data that is originally from different 
%    workspaces that have been prepended with some string, e.g. b261thick 
%    or b261alpha.  Prepending is done by prependws.m.
% 
%    Severe restriction:  Only restricted math operations can be applied to xvar and yvar,
%                         i.e. it must go after the variable in the plotstring, e.g. .^2 or + 2
%                         but 1./ will not work.  Ranges also work, so xvar(1:50) works.
%    
%    Input:  strstruct  STRUCTURE of any number of prepended strings
%            xvar  variable name for x-axis in string format, e.g. 'thick'.
%            yvar  variable name for y-axis in string format, e.g. 'alpha'.
%            newfigure (optional)   'n' for a new figure, anything else (or 
%                                   nothing at all) for current figure.
%            
%    Returns:  hp handles to plot
%    
%    Last changed:  10/01/00 sthi

if isempty(strstruct)
  display('you must supply at least one prepended string') 
  return
end

if nargin > 3
  if varargin{1} == 'n', figure,clf,box on,hold on, end
end
  
plstr = [];
for n = 1:length(strstruct)
  if n ~= 1
    plstr = [plstr ',' char(strstruct(n)) char(xvar) ',' char(strstruct(n)) char(yvar) ',''.-'''];
  else
    plstr = [plstr char(strstruct(n)) char(xvar) ',' char(strstruct(n)) char(yvar)  ',''.-'''];
  end
end
% For some unexplained reason all the following attempts to plot are sensitive to putting an ';' in the plotstring, i.e. the version:
% plstr=['plot(' plstr ');']; will not work, but the following will!
% plstr=['plot(' plstr ')'];
% handle = evalin('base',plstr)
handle = evalin('base',['plot(' plstr ')']);
if nargout > 0
  hp = handle;
end

