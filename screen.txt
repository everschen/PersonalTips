
screen -X title test //命令的方式修改title，也是执行screen命令，其他命令也可以这样执行
* Ctrl-a then :number <newnumber> to change the number (which will also change relative order of your session instances).
# CTRL+a A               // update name
# screen -t <name> [num]  // Create a new windows with name // screen -t onefs-115025 3

# screen -ls                // list screen sessions
# screen -S <session>       // create a screen session with given name
# screen -r <session>       // reattach to a detached screen session
# screen -d [-r] <session>  // detach the elsewhere running screen [and reattach here]
# screen -D [-r] <session>  // detach running screen and logout remote [and reattach here]
# screen -wipe <session>    // clean up a dead screen session


echen1@remotedev-echen1 ~ % cat ~/.screenrc
# Set default encoding using utf8
defutf8 on


## 解决中文乱码,这个要按需配置
defencoding utf8
encoding utf8 utf8


#兼容shell 使得.bashrc .profile /etc/profile等里面的别名等设置生效
shell -$SHELL

#set the startup message
startup_message off
term linux

## 解决无法滚动
termcapinfo xterm|xterms|xs ti@:te=\E[2J

# 屏幕缓冲区行数
defscrollback 10000

# 下标签设置
hardstatus on
caption always "%{= kw}%-w%{= kG}%{+b}[%n %t]%{-b}%{= kw}%+w %=%d %M %0c %{g}%H%{-}"

#关闭闪屏
vbell off

# initial windows with title
screen -t home 0
screen -t home 1
screen -t cluster 2
