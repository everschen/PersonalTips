
for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof)

set tar=dev3
set tar=release

e:
cd E:\0222\20160224\
echo "copy so and app from ue..."




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

if %1=="d" goto my_remove


set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%
e:
cd E:\0222\20160224\From-UE
md %ymd%-%hour%%ms%-%mydevice2%
cd %ymd%-%hour%%ms%-%mydevice2%

adb -s %mydevice2% pull /system/priv-app/ImsCM/ImsCM.apk .
adb -s %mydevice2% pull /system/app/ims/ims.apk .
adb -s %mydevice2% pull /system/lib/libreference-ril_sp.so .


adb -s %mydevice2% pull /system/priv-app/Security/Security.apk .
adb -s %mydevice2% pull /system/bin/ju_ipsec_server .

adb -s %mydevice2% pull /system/lib/liblemon.so .
adb -s %mydevice2% pull /system/lib/libmme_jrtc.so .
adb -s %mydevice2% pull /system/lib/libCamdrv23.so .
adb -s %mydevice2% pull /system/lib/libzmf.so .
adb -s %mydevice2% pull /system/lib/libavatar.so .
adb -s %mydevice2% pull /system/lib/libandroidbridge.so .
adb -s %mydevice2% pull /system/lib/libcharon.so .
adb -s %mydevice2% pull /system/lib/libhydra.so .
adb -s %mydevice2% pull /system/lib/libimcv.so .
adb -s %mydevice2% pull /system/lib/libipsec.so .
adb -s %mydevice2% pull /system/lib/libstrongswan.so .
adb -s %mydevice2% pull /system/lib/libtnccs.so .
adb -s %mydevice2% pull /system/lib/libtncif.so .


adb -s %mydevice2% pull /system/priv-app/Settings/Settings.apk .
adb -s %mydevice2% pull /system/bin/radiooptions_sp .
adb -s %mydevice2% pull /system/priv-app/SprdVoWifiService/SprdVoWifiService.apk .
adb -s %mydevice2% pull /system/framework/telephony-common.jar .

:endofloop


)


