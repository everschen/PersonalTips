
echo "get log files"

adb root
timeout 5


adb shell ls -l sdcard/JusTex/log
adb shell rm -rf sdcard/JusTex/log/mtc*.log
adb shell ls -l sdcard/JusTex/log
adb shell rm data/data/com.sprd.vowifi.security/files/charon.log

adb push E:/LOG/nf_xfrm_dec_tcpdump /proc/net/netfilter/nf_xfrm_dec_tcpdump


adb shell cat /proc/net/netfilter/nf_xfrm_dec_tcpdump


