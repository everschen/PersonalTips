
if exist ../kernel (
cd ../kernel/
python ./analyzer.py
cd ../android/
)

python ./analyzer.py


if exist main.ylog (
FOR /f "delims=" %%i in ("./main.log") do (set file1=%%~zi)
FOR /f "delims=" %%i in ("./main.ylog") do (set file2=%%~zi)
echo %file1%
echo %file2%
IF %file2% gtr %file1% (move main.log missinglog.log & move main.ylog main.log) else (move main.ylog missinglog.log)
)


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
cd ../android/
)




