# conda pip and apt 

## conda install 和 pip install 区别
通常我们可以使用conda和pip两种方式来下载和卸载安装包，这里说一下这两种方式使用的区别。conda是一种通用包管理系统，可以构建和管理任何语言的任何类型的软件，因此，它也使用于Python包。pip是Python官当认可的包管理器，最常用于安装在Python包索引（PyPI）上发布的包，网址https://pypi.org/。
即：pip是Python包的通用管理器，conda是一个与语言无关的跨平台环境管理器，对于我们用户来说，最显著的区别是pip在任何环境中安装Python包，conda安装任何环境的任何包。
注意：Anaconda中base环境中已经集成安装好了conda和pip，所以可以使用两种方式来安装我们想要的python软件包，安装好了软件包在Scripts目录下可以找到。

## PiP常用命令
pip --version：查看已经安装了的pip版本
pip install -U pip：升级pip
pip list 或 pip freeze：查看当前已经安装好了包及版本
pip install package_name(包名)：下载安装包
pip uninstall package_name(包名)： 卸载安装包
pip show package_name(包名)：显示安装包信息（安装路径、依赖关系等）



## conda常用命令
conda list/pip list：查看环境中已经安装了的软件包 (需要先激活已经创建的虚拟环境)
conda env list 或者 conda info -e : 查看当前存在那些虚拟环境
conda update conda: 检查更新当前的conda版本
conda install package_name(包名)：下载安装包
conda uninstall package_name(包名)： 卸载安装包

## 创建虚拟环境
conda create -n your _env_name package_name python=X.X (2.7、3.6等)
虚拟环境名字为： your _env_name
注意：your_env_name文件可以在Anaconda安装目录envs文件下找到
举例：conda create -n myenv numpy matplotlib python=3.7

## 删除虚拟环境
conda remove -n your_env_name --all ,即可删除
删除虚拟环境中的某个包
conda remove -- name your_env_name package_name (包名)
或者进入激活虚拟环境后，使用命令 conda uninstall package_name(包名)


## 激活已经创建的虚拟环境
conda activate aligner

## 退出已经创建的虚拟环境
conda deactivate


## pip国内常用镜像源
阿里云 http://mirrors.aliyun.com/pypi/simple/
中国科技大学 https://pypi.mirrors.ustc.edu.cn/simple/
豆瓣(douban) http://pypi.douban.com/simple/
清华大学 https://pypi.tuna.tsinghua.edu.cn/simple/
中国科学技术大学 http://pypi.mirrors.ustc.edu.cn/simple/
这里推荐使用豆瓣和清华源，因为它们比较稳定

## pip安装临时使用国内镜像源
可以在使用pip安装时在后面加上 -i 参数，来指定pip源，举例：
pip install numpy -i https://pypi.douban.com/simple/
注意：http后面要加s

## 永久指定pip默认安装源
Windows:
直接在user目录中创建一个pip目录，如：C:\Users\用户名\pip,创建完后再pip 目 录下新建文件pip.ini，添加以下内容：
[gobal]
timeout = 6000
index-url = http://pypi.douban.com/simple/
trusted-host = http://pypi.douban.com
编辑完后进行保存，这样当我们再使用pip来安装时，会默认调用我们设置好了的镜像 源，就不用每次再临时添加。

Linux：
修改 ~/.pip/pip.conf (没有就创建一个)，和Windows上一样，在pip.conf文件中添加内容后保存
[gobal]
timeout = 6000
index-url = http://pypi.douban.com/simple/
trusted-host = http://pypi.douban.com


## conda切换源
在conda安装好之后，默认的镜像是官方的，由于官网的镜像在境外,访问太慢或者不能访问，为了能够加快访问的速度，首先在命令行中打开虚拟环境，输入以下命令(设置清华的镜像)
终端中运行命令：
(1)清华源(TUNA)
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.tuna.tsinghua.edu.cn/anaconda/pkgs/main/
conda config --setshow_channel_urls yes
(2)中科大源(USTC)
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/free/
conda config --add channels https://mirrors.ustc.edu.cn/anaconda/pkgs/main/
conda config --setshow_channel_urls yes
然后更改镜像源配置文件，在用户home目录下，找到 .condarc 配置文件，如C:\Users\用户名.condarc,右键选择记事本打开编辑，删掉channels下面的 -defaults一行,或者在其前面加#号注释掉。

## 换回默认源：
conda config --remove-key channels


## Conda 提供了多种保存和移动环境的方法。

Clone
在本地，conda 可以方便地创建环境的快照或者备份：
conda create --name snapshot --clone myenv

Spec List
如果需要在具有 相同操作系统 的计算机之间复制环境，则可以生成 spec list。这是离线打包。
生成 spec list 文件：
conda list --explicit > spec-list.txt
重现环境：
conda create  --name python-course --file spec-list.txt

