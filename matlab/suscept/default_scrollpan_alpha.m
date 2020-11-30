function [lambda,kshape] = default_scrollpan_alpha(selector,lambda,kshape)
%  function default_scrollpan_alpha(selector,lambda,kshape)
%    This function resets all or a selected one of the alpha fit values to 
%    its default value, defined in
%    deflambda
%     defkshape
%     
%     selector: 0 all, 1, 2, 3, 4 for successive values
%
%    
%    Last modified:  4/21/00 sthi
%    
  
% deflambda = [-1.73e7  9  .01 .45];     % 4th element is kshape
  deflambda = [-1.80e7  9.9  .01 .41];     % 4th element is kshape
  defkshape = deflambda(4);
  switch selector
    case 0
      lambda = deflambda;
      kshape = defkshape;
      update_scrollpan_alpha(lambda,kshape);
    case 1
      lambda(1) = deflambda(1);
      update_scrollpan_alpha(lambda,kshape);
    case 2
      lambda(2) = deflambda(2);
      update_scrollpan_alpha(lambda,kshape);
    case 3
      lambda(3) = deflambda(3);
      update_scrollpan_alpha(lambda,kshape);
    case 4
      kshape = defkshape;
      lambda(4) = deflambda(4);                       %4th element is kshape
      update_scrollpan_alpha(lambda,kshape);
    otherwise
      display('Problem with call to default_scrollpan_alpha');
    end
      
 
