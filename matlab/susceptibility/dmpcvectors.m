% Script that reads all vectors from a dmpc data file and stores them under their original names in the main workspace.
fnm=input('DMPC file name (.dat extension assumed):  ','s');
[s,skilabod]=fopen(strcat(fnm,'.dat'),'r','l');

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
   fgetl(s);                      % read out the 3 lines that come before
   % the real information on vectors.  These vectors are there for historic reasons
   % and are NOT written to the data file.                              
end
%find how many bytes into the data my vectors are.  I'm searching for freq,
%s11sr and s11si (frequency, the averaged real and imaginary S11S parameter.
%
relloc=0;                         %"current" relative location of w.r.t. 
%                                  starting byte count.  NOTE for below: THE THREE JUNK VECTORS ARE NOT WRITTEN TO THE FILE BY DMPC!!
vnames=[];
vlens=[];
for i=1:(nvect - 3),       %the 3 dummy vectors at beginning are subtracted (skipped over them above).
  lina=fgetl(s);
  nafn=lina(1:find(isspace(lina)));
  if isempty(findstr(nafn,'[['))   %check to see if the name contains [[ at end, as images do as well as special vars, oldcoms[[ and viewsave[[.
    nafn(end-1:end)=[];   %to get rid of the '[ ' in the vector name.  All ordinary vectors contain one [ at end.
    vnames=strvcat(vnames,nafn);
  elseif ~isempty(findstr(nafn,'[['))   %i.e. this vector contains an image, or is one of the special vector oldcoms[[ or viewsave[[.
    nafn(end-2:end)=[];   %to get rid of the '[[ ' in the vector name.  All ordinary vectors contain one [ at end.
    vnames=strvcat(vnames,'junk_name_for_dmpc_matlab_read');  %will actually read into this hopefully unique variable name(!), then erase it.
  else
    display('This line should never be reached!  Terminating script.')
    return
  end
  len=str2num(lina(find(isspace(lina)):length(lina)));   %find and add length of the vector to vlens.
  vlens=[vlens; len];
  relloc=relloc + len;
end
vnames=cellstr(vnames);   %convert to a cellstring for use with the eval function below.

lina='';
while isempty(findstr(lina,'is the starting byte count'))
   lina=fgetl(s);
end
%find the starting byte count.
stbtct=str2num(lina(1:(findstr(lina,'is the starting byte count')-1)));
status=fseek(s,stbtct,'bof');   %find the 1st data byte NOTE: THE THREE JUNK VECTORS ARE NOT WRITTEN TO THE FILE BY DMPC!!!!
for i=1:length(vlens),
  tmp=fread(s,vlens(i),'float32');
  eval([lower(char(vnames(i))) '=tmp;']);    %convert to lowercase, uppercase is a pain...
end

fclose(s);

file_info = {filename; savedate; savetime}
sprintf('Total vectors in the data file............................\t%d\nOrdinary vectors (i.e. not images or special variables)...\t%d',...
   nvect-3,nvect-3-length(find(strcmp(vnames,'junk_name_for_dmpc_matlab_read'))))   %Removing the 3 dummy vectors from vector number.

clear i status tmp nafn len filename savedate savetime skilabod vnames vlens ... 
   lina relloc nvect s lvec stbtct fnm junk_name_for_dmpc_matlab_read


% clear real and imag if they exist, as these names conflict with the functions in matlab (I used these in some macros):
if exist('real')==1
  sprintf('CLEARING THE VARIABLE NAMED ''real'' FROM THE WORKSPACE,\nAS IT COLLIDES WITH MATLAB FUNCTION real.')
  clear real
end
if exist('imag')==1
  sprintf('CLEARING THE VARIABLE NAMED ''imag'' FROM THE WORKSPACE,\nAS IT COLLIDES WITH MATLAB FUNCTION imag.')
  clear imag
end
