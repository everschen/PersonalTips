
echo "mv pcap files"

set mydevice2=SP9830A71005B301449
set i=0

:intercept2

if %mydevice2%=="" goto :eof

echo 000 %i% %mydevice2% 111

echo 111 %mydevice2:~-1% end
echo 222 %mydevice2:~0,-2% end

:intercept 
if "%mydevice2:~-1%"==" " set "mydevice2=%mydevice2:~0,-1%" & goto intercept2 

echo %mydevice2% ok 








