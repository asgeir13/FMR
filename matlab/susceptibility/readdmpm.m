function [info,Z,S]=readdmpm(namebase,numfile)
%function [info,Z]=readdmpm(namebase,numfile)
%
%Read impedance measurement from DMPM (Roger Koch's program)
%in form Z=R + iX (R,X format) and reads the averaged R part and X part
%called res and react recorded by one of the following macroes:
%incref.mac  (steps only easy field)
%incrhf.mac  (steps only hard field)
%incrang.mac (keeps field magnitude fixed but rotates angle)
%
%variables: namebase  string containing namebase
%           numfile   number to append to namebase to obtain filename.dat
%
%returns:   info  text variables read from file, date, time, vector 
%                 length etc. stored in a cell array containing strings
%           Z  a matrix containing [freq res react].
%
%Snorri Ingvarsson, 990225

[s,skilabod]=fopen(strcat(namebase,num2str(numfile),'.dat'),'r','l');

filename='';
while isempty(findstr(filename,'FILE_NAME'))
   filename=fgetl(s);
end
savedate=fgetl(s);                %next line is savedate
savetime=fgetl(s);                %next line is savetime
lina='';
while isempty(findstr(lina,'vector names and lengths follow'))
   lina=fgetl(s);
end
nvect=str2num(lina(1:(findstr(lina,'vector names and lengths follow')-1)));
for i=1:3,
   fgetl(s);                      %read out the 3 lines that come before 
   %                               the real information on vectors.
end
%find how many bytes into the data my vectors are.  I'm searching for freq,
%res and react (frequency, the averaged real and imaginary impedances res
%and react.
relloc=0;                         %"current" relative location of w.r.t. 
%                                  starting byte count.
for i=1:(nvect - 3),
   lina=fgetl(s);
   len=str2num(lina(find(isspace(lina)):length(lina)));
   if ~isempty(findstr(lina,'FREQ[')), lvec=len;, freqloc=relloc;, end
   if ~isempty(findstr(lina,'RES[')), resloc=relloc;,end
   if ~isempty(findstr(lina,'REACT[')), reactloc=relloc;,end
   if ~isempty(findstr(lina,'S11AR[')), srealloc=relloc;,end
   if ~isempty(findstr(lina,'S11AI[')), simagloc=relloc;,end
   relloc=relloc + len;
end

fgetl(s);
lina=fgetl(s);
Z=zeros(lvec,3);
%find the starting byte count.
stbtct=str2num(lina(1:(findstr(lina,'is the starting byte count')-1)));
status=fseek(s,stbtct + 4*freqloc,'bof');   %read frequency.
Z(:,1)=fread(s,lvec,'float32');

status=fseek(s,stbtct + 4*resloc,'bof');    %read resistive part of impedance, Re(Z).
Z(:,2)=fread(s,lvec,'float32');

status=fseek(s,stbtct + 4*reactloc,'bof');  %read reactive part of impedance, Im(Z).
Z(:,3)=fread(s,lvec,'float32');

S=zeros(lvec,2);
status=fseek(s,stbtct + 4*srealloc,'bof');  %read Re(S11).
res=fread(s,lvec,'float32');

status=fseek(s,stbtct + 4*simagloc,'bof');  %read Im(S11) and add to real part.
ims=fread(s,lvec,'float32');
i=sqrt(-1);
S=res + i*ims;

fclose(s);

info = {filename; savedate; savetime};
