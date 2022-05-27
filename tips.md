1. keep alive for ssh
	echen1@remotedev-echen1 ~/.ssh
	% cat config
	Host *
			ServerAliveInterval 30
			ServerAliveCountMax 5

2. vi 字符替换
vi string replace: %s/yyyy-MM-dd HH:mm:ss//g

3. 填充文件大小
dd if=/dev/zero of=filename bs=$((1024*1024)) count=$((10*1024))  //10G

4. 超时执行命令
output=`timeout $CONNECT_TIMEOUT /usr/bin/telnet $address $port 2>&1`

5.删除文件行末尾的^M
sed -e "s/\r//g" file > newfile

6.文本文件做集合交、并、差运算时
      sort a b | uniq > c   # c 是 a 并 b
      sort a b | uniq -d > c   # c 是 a 交 b
      sort a b b | uniq -u > c   # c 是 a - b

7.head -100 *  （每个文件有一个标题）来阅读检查目录下所有文件的内容。这在检查一个充满配置文件的目录（如 /sys、/proc、/etc）时特别好用

8.计算文本文件第三列中所有数的和（可能比同等作用的 Python 代码快三倍且代码量少三倍）
awk '{ x += $3 } END { print x }' myfile

9.要持续监测文件改动，可以使用 watch，例如检查某个文件夹中文件的改变，可以用 watch -d -n 2 'ls -rtlh | tail'；或者在排查 WiFi 设置故障时要监测网络设置的更改，
可以用 watch -d -n 2 ifconfig