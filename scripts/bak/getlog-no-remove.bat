for /f "delims=" %%t in ('adb devices') do call :abc "%%t"
goto :eof
:abc

set str=
set str2=
set str3=
set mydevice2=
set mydevice=

echo %1
set str=%1
:intercept
echo 000 %str%
if "%str:~-2,1%"==" " set str=%str:~1,-2% & goto intercept
echo 789 %str%
echo 456 %str:~-7,6%
echo 123 %str:~1,20%
if "%str:~-7,6%"=="device" set mydevice2=%str:~1,20% 
if NOT "%str:~-7,6%"=="device" goto endofloop
echo 555 %mydevice2% 666


:intercept2
if "%mydevice2:~-1%"==" " set "mydevice2=%mydevice2:~0,-1%"&goto intercept2

echo 456

echo 789
:abc2
echo 888 %mydevice2% 777

:next_steps
for /f "delims=" %%t in ('adb -s %mydevice2% root') do set str2="%%t"
if %str2%=="restarting adbd as root" goto adbroot_restarted
if %str2%=="adbd is already running as root" goto adbroot_notrestarted
goto endofloop


:adbroot_restarted
timeout 3
goto next_steps



:adbroot_notrestarted
adb -s %mydevice2% remount




set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%
e:
cd e:\log
md %ymd%-%hour%%ms%-%mydevice2%
cd %ymd%-%hour%%ms%-%mydevice2%

adb -s %mydevice2% shell ls -l sdcard/JusTex/log

adb -s %mydevice2% shell ls -l storage/sdcard0/slog/
adb -s %mydevice2% shell ls -l sdcard/SprdService/log/
adb -s %mydevice2% shell ls -l sdcard/JusTex/log
adb -s %mydevice2% shell ls -l data/data/com.sprd.vowifi.security/files/charon.log

adb -s %mydevice2% pull data/data/com.sprd.vowifi.security/files/charon.log charon.log
md JusTex
adb -s %mydevice2% pull sdcard/JusTex/log JusTex/
adb -s %mydevice2% pull storage/sdcard0/slog/ slog/
adb -s %mydevice2% pull sdcard/SprdService/log .

for /f "delims=" %%s in ('dir /b /s /a-d *main*') do copy "%%s" .
for /f "delims=" %%s in ('dir /b /s /a-d *crash*') do copy "%%s" .

python ../scripts/key_build.py

for /f "delims=" %%s in ('dir /b /s /a-d *.pcap') do copy "%%s" .


cd ../



:endofloop


)


