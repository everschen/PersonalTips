
echo "get log files"



set "Ymd=%date:~,4%%date:~5,2%%date:~8,2%"
set "ms=%time:~3,2%%time:~6,2%"
if "%time:~0,1%"==" " (set hour=%time:~1,1%) else set hour=%time:~,2%

echo %hour%







