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


set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%
e:
cd e:\log
md %ymd%-%hour%%ms%-%mydevice2%
cd %ymd%-%hour%%ms%-%mydevice2%

adb -s %mydevice2% pull data/data/com.sprd.vowifi.security/files/charon.log charon.log
md tombstones
adb pull data/tombstones/ tombstones/


adb -s %mydevice2% pull storage/sdcard0/slog/ slog/
adb -s %mydevice2% pull storage/sdcard0/ylog/ ylog/
adb -s %mydevice2% pull /data/slog/ slog_in/
adb -s %mydevice2% pull /data/ylog/ ylog_in/
adb -s %mydevice2% pull /data/data/com.spreadtrum.vowifi/files/SprdService/log mtc_log/
adb -s %mydevice2% pull /data/data/com.sprd.vowifi.security/files/Security/log security_log/
adb -s %mydevice2% pull sdcard/SprdService/log .

#for /f "delims=" %%s in ('dir /b /s /a-d *main*') do copy "%%s" .
#for /f "delims=" %%s in ('dir /b /s /a-d *crash*') do copy "%%s" .
#for /f "delims=" %%s in ('dir /b /s /a-d *radio*') do copy "%%s" .
#for /f "delims=" %%s in ('dir /b /s /a-d *kernel*') do copy "%%s" .



if exist ylog/ylog (
cd ylog/ylog/kernel/
python ./analyzer.py
cd ../android/
python ./analyzer.py


SETLOCAL ENABLEDELAYEDEXPANSION
if exist main.ylog (
FOR /f "delims=" %%i in ("main.log") do set file1=%%~zi
echo "main.log"
echo !file1!
FOR /f "delims=" %%i in ("main.ylog") do set file2=%%~zi
echo "main.ylog"
echo !file2!

IF !file2! gtr !file1! (
echo "move main.log missinglog.log"
move main.log missinglog.log
move main.ylog main.log
) else ( 
echo "move main.ylog missinglog.log"
move main.ylog missinglog.log
))



if exist radio.ylog (
move radio.ylog radio22.log
)

if exist system.ylog (
move system.ylog system22.log
)

copy ..\..\..\mtc_log\*.log .
copy ..\..\..\security_log\*.log .

python D:/scripts/scripts/parse_imsbr_file.py
python D:/scripts/scripts/reg_ui_sys.py
python D:/scripts/scripts/key_build.py
python D:/scripts/scripts/handover_log.py
python D:/scripts/scripts/system_warning.py
python D:/scripts/scripts/ipsecsa.py
python D:/scripts/scripts/ip_address.py
python D:/scripts/scripts/ip_call.py
python D:/scripts/scripts/VolteRegisterState.py
cd ../tcpdump/
python ./analyzer.py
copy ytag\*.cap ..\android\
explorer "..\android\"
)


cd e:\log
cd %ymd%-%hour%%ms%-%mydevice2%

if exist ylog_in/ylog (
cd ylog_in/ylog/kernel/
python ./analyzer.py
cd ../android/
python ./analyzer.py


SETLOCAL ENABLEDELAYEDEXPANSION
if exist main.ylog (
FOR /f "delims=" %%i in ("main.log") do set file1=%%~zi
echo "main.log"
echo !file1!
FOR /f "delims=" %%i in ("main.ylog") do set file2=%%~zi
echo "main.ylog"
echo !file2!

IF !file2! gtr !file1! (
echo "move main.log missinglog.log"
move main.log missinglog.log
move main.ylog main.log
) else ( 
echo "move main.ylog missinglog.log"
move main.ylog missinglog.log
))



if exist radio.ylog (
move radio.ylog radio22.log
)

if exist system.ylog (
move system.ylog system22.log
)

copy ..\..\..\mtc_log\*.log .
copy ..\..\..\security_log\*.log .

python D:/scripts/scripts/parse_imsbr_file.py
python D:/scripts/scripts/reg_ui_sys.py
python D:/scripts/scripts/key_build.py
python D:/scripts/scripts/handover_log.py
python D:/scripts/scripts/system_warning.py
python D:/scripts/scripts/ipsecsa.py
python D:/scripts/scripts/ip_address.py
python D:/scripts/scripts/ip_call.py
python D:/scripts/scripts/VolteRegisterState.py
cd ../tcpdump/
python ./analyzer.py
copy ytag\*.cap ..\android\
explorer "..\android\"
)


#copy ..\scripts\reg_ui_sys.py .

#for /f "delims=" %%s in ('dir /b /s /a-d *.pcap') do copy "%%s" .


cd ../

:my_remove
goto endofloop

adb -s %mydevice2% shell ls -l sdcard/JusTex/log
adb -s %mydevice2% shell rm -rf sdcard/JusTex/log/*

adb -s %mydevice2% shell rm -rf storage/sdcard0/slog/*.*
adb -s %mydevice2% shell rm -rf storage/sdcard0/slog/*

adb -s %mydevice2% shell rm -rf sdcard/SprdService/log/*.*
adb -s %mydevice2% shell rm -rf sdcard/SprdService/log/*

adb -s %mydevice2% shell ls -l storage/sdcard0/slog/
adb -s %mydevice2% shell ls -l sdcard/SprdService/log/
adb -s %mydevice2% shell ls -l sdcard/JusTex/log


adb -s %mydevice2% shell rm -rf /data/data/com.sprd.vowifi.security/files/Security/log
adb -s %mydevice2% shell rm -rf /data/data/com.spreadtrum.vowifi/files/SprdService/log
adb -s %mydevice2% shell rm -rf data/tombstones/*

adb -s %mydevice2% push E:/LOG/scripts/nf_xfrm_dec_tcpdump /proc/net/netfilter/nf_xfrm_dec_tcpdump


adb -s %mydevice2% shell cat /proc/net/netfilter/nf_xfrm_dec_tcpdump
adb -s %mydevice2% shell pkill -9 com.juphoon.justex.sprd
adb -s %mydevice2% shell pkill -9 com.juphoon.sprd.service

:endofloop


)


