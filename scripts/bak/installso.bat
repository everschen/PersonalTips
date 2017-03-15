
echo "copy apk files"



for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof)
echo %mydevice%


for /f "delims=" %%t in ('adb root') do set str="%%t"
if %str%=="restarting adbd as root" goto adbroot_restarted
if %str%=="adbd is already running as root" goto adbroot_notrestarted


:adbroot_restarted
timeout 8
for /f "delims=" %%t in ('adb devices') do set str=%%t
if "%str:~-6%"=="device" (set mydevice=%str:~,19%) else set mydevice=""
if %mydevice%=="" (echo "no devices" & Goto :eof & pause)
echo %mydevice%


:adbroot_notrestarted
e:

cd E:\0222\20160224\

adb remount

adb shell mkdir -p /data/bin

echo "try to make more free space"
adb shell mv /system/bin/factorytest /data/bin
adb shell mv /system/bin/blktrace /data/bin
adb shell mv /system/bin/gdbserver /data/bin
echo "delete unused ringtones."
adb shell rm /system/media/audio/ringtones/Sceptrum.ogg
adb shell rm /system/media/audio/ringtones/Perseus.ogg
adb shell rm /system/media/audio/ringtones/ArgoNavis.ogg

echo "delete browser email"
adb shell rm -rf /system/app/Browser
adb shell rm -rf /system/app/Email


echo "copy so and app from server..."
copy /Y x:\output\* .

echo "copy so files"
for %%f in (*.so) do (
	echo start to push %%f
	adb push %%f /system/lib/
)



adb shell mkdir /system/priv-app/justex/
adb shell mkdir /system/priv-app/jussec/
adb shell mkdir /system/priv-app/service/

echo "copy jussec, justex apks"
adb push justex.apk /system/priv-app/justex/
adb push service.apk /system/priv-app/service/
adb push Security.apk /system/priv-app/Security/



adb shell ls -l sdcard/JusTex/log
adb shell rm -rf sdcard/JusTex/log/*

adb shell rm -rf storage/sdcard0/slog/*.*
adb shell rm -rf storage/sdcard0/slog/*
adb shell rm -rf sdcard/SprdService/log/*.*
adb shell rm -rf sdcard/SprdService/log/*

adb shell ls -l storage/sdcard0/slog/

adb shell ls -l sdcard/JusTex/log
adb shell rm data/data/com.sprd.vowifi.security/files/charon.log

#adb push E:/LOG/scripts/nf_xfrm_dec_tcpdump /proc/net/netfilter/nf_xfrm_dec_tcpdump


#adb shell cat /proc/net/netfilter/nf_xfrm_dec_tcpdump
adb shell pkill -9 com.juphoon.justex.sprd

#adb shell rm -rf /system/priv-app/service


adb reboot


