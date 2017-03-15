
echo "get log files"

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
if %mydevice%=="" (echo "no devices" & Goto :eof)
echo %mydevice%

:adbroot_notrestarted
adb remount

if "%1"=="d" goto my_remove


set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%
cd e:\log
md %ymd%-%hour%%ms%
cd %ymd%-%hour%%ms%

adb pull data/data/com.sprd.vowifi.security/files/charon.log charon.log
md JusTex
adb pull sdcard/JusTex/log JusTex/
adb pull storage/sdcard0/slog/ slog/
adb pull sdcard/SprdService/log .

for /f "delims=" %%s in ('dir /b /s /a-d *main*') do copy "%%s" .

python ../key_build.py

for /f "delims=" %%s in ('dir /b /s /a-d *.pcap') do copy "%%s" .


cd ../

:my_remove

adb shell ls -l sdcard/JusTex/log
adb shell rm -rf sdcard/JusTex/log/*

adb shell rm -rf storage/sdcard0/slog/*.*
adb shell rm -rf storage/sdcard0/slog/*

adb shell rm -rf sdcard/SprdService/log/*.*
adb shell rm -rf sdcard/SprdService/log/*

adb shell ls -l storage/sdcard0/slog/
adb shell ls -l sdcard/SprdService/log/
adb shell ls -l sdcard/JusTex/log

adb shell rm data/data/com.sprd.vowifi.security/files/charon.log

adb push E:/LOG/nf_xfrm_dec_tcpdump /proc/net/netfilter/nf_xfrm_dec_tcpdump


adb shell cat /proc/net/netfilter/nf_xfrm_dec_tcpdump
adb shell pkill -9 com.juphoon.justex.sprd
adb shell pkill -9 com.juphoon.sprd.service

echo off
#adb shell rm -rf /system/priv-app/service




