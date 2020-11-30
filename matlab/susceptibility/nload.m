% name=strvcat('a','b','c','d','e');
name='c';
for n=1:length(name)
   s1 = strcat('inf',name(n));
   s2 = strcat('f',name(n));
   s3 = strcat('s',name(n));
%   eval(['[' s1 ',' s2 ',' s3 ']=sload(12,''990602a'');']);
   eval(['[' s1 ',' s2 ',' s3 ']=sload(12,name(n));']);
   s4 = strcat('c',name(n));
   s5 = strcat('z',name(n));
   eval(['[' s4 ',' s5 ']=spermplot(' s1 ',' s2 ',' s3 ');']);
end
%title('990520/990520b1-12','fontname','times','fontsize',18,'fontweight','bold')
%title('990616/990616\\eaz\\c1-12','fontname','times','fontsize',18,'fontweight','bold')
