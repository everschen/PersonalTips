
if exist ../kernel (
cd ../kernel/
python ./analyzer.py
cd ../android/
)

if exist ../../../../security_log (
copy ..\..\..\..\security_log\*.log .
)

if exist ../../../../SprdService_log (
copy ..\..\..\..\SprdService_log\*.log .
)

if exist ../../../Sprd (
copy ..\..\..\Sprd\*.log .
)

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


python D:/scripts/scripts/parse_imsbr_file.py
python D:/scripts/scripts/reg_ui_sys.py
python D:/scripts/scripts/key_build.py
python D:/scripts/scripts/handover_log.py
python D:/scripts/scripts/system_warning.py
python D:/scripts/scripts/ipsecsa.py
python D:/scripts/scripts/ip_address.py
python D:/scripts/scripts/ip_call.py
python D:/scripts/scripts/VolteRegisterState.py


if exist ../tcpdump (
cd ../tcpdump/
python ./analyzer.py
copy ytag\*.cap ..\android\
cd ../android/
)




