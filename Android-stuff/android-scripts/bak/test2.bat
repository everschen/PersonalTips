
echo "mv pcap files"



for /d %%i in (*) do (
    set str="%%i"
	cd /d %%i	
	for /f "delims=" %%s in ('dir /b /s /a-d *.pcap') do copy "%%s" .
	cd .. )









