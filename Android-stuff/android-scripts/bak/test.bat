
echo "get log files"



set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%



for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof)
echo %mydevice%


for /f "delims=" %%t in ('adb root') do set str="%%t"
if %str%=="restarting adbd as root" goto adbroot_restarted
if %str%=="adbd is already running as root" goto adbroot_notrestarted


:adbroot_restarted
for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof)
echo %mydevice%

:adbroot_notrestarted











