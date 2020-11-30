clf,axes,hold on
for n=1:length(name)
   s1 = strcat('f',name(n));
   s2 = strcat('c',name(n));
   eval(['plot(' s1 ',real(' s2 '(:,1)));']);
   shg
   pause
end
