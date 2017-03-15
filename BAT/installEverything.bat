
for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof)



e:
cd E:\0222\20160224\


copy /Y x:\output\dev3\* .



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
if "%mydevice2:~-1%"=="	" set "mydevice2=%mydevice2:~0,-1%"&goto intercept2
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

e:
cd E:\0222\20160224\



adb -s %mydevice2% push ImsCM.apk /system/priv-app/ImsCM/
adb -s %mydevice2% push ims.apk /system/app/ims/
adb -s %mydevice2% push libreference-ril_sp.so /system/lib/
adb -s %mydevice2% push Settings.apk system/priv-app/Settings/

adb -s %mydevice2% shell rm /system/priv-app/service/service.apk
adb -s %mydevice2% shell rm /system/framework/vowifi_adapter.jar

echo "copy so files"
for %%f in (*.so) do (
	echo start to push %%f
	adb -s %mydevice2% push %%f /system/lib/
)



adb -s %mydevice2% push Security.apk /system/priv-app/Security/
adb -s %mydevice2% push ju_ipsec_server /system/bin/

#adb -s %mydevice2% push radiooptions_sp /system/bin/
#adb -s %mydevice2% push wpa_supplicant /system/bin/

adb -s %mydevice2% push SprdVoWifiService.apk /system/priv-app/SprdVoWifiService/
#adb -s %mydevice2% push telephony-common.jar /system/framework/


:my_remove

adb -s %mydevice2% shell ls -l sdcard/JusTex/log
adb -s %mydevice2% shell rm -rf sdcard/JusTex/log/*

adb -s %mydevice2% shell rm -rf storage/sdcard0/slog/*.*
adb -s %mydevice2% shell rm -rf storage/sdcard0/slog/*

adb -s %mydevice2% shell rm -rf storage/sdcard0/modem_log/*.*
adb -s %mydevice2% shell rm -rf storage/sdcard0/modem_log/*

adb -s %mydevice2% shell rm -rf sdcard/SprdService/log/*.*
adb -s %mydevice2% shell rm -rf sdcard/SprdService/log/*

adb -s %mydevice2% shell ls -l storage/sdcard0/slog/
adb -s %mydevice2% shell ls -l sdcard/SprdService/log/
adb -s %mydevice2% shell ls -l sdcard/JusTex/log

adb -s %mydevice2% shell rm data/data/com.sprd.vowifi.security/files/charon.log

adb -s %mydevice2% push E:/LOG/scripts/nf_xfrm_dec_tcpdump /proc/net/netfilter/nf_xfrm_dec_tcpdump

adb -s %mydevice2% shell rm data/tombstones/*
adb -s %mydevice2% shell cat /proc/net/netfilter/nf_xfrm_dec_tcpdump
adb -s %mydevice2% shell pkill -9 com.juphoon.justex.sprd
adb -s %mydevice2% shell pkill -9 com.juphoon.sprd.service



adb -s %mydevice2% reboot


:endofloop


)


