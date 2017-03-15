
if exist main.ylog (
FOR /f "delims=" %%i in ("main.log") do set file1=%%~zi
pause
FOR /f "delims=" %%i in ("main.ylog") do set file2=%%~zi
pause
echo %file1%
echo %file2%
IF %file2% gtr %file1% (move main.log missinglog.log & move main.ylog main.log) else (move main.ylog missinglog.log)
)
