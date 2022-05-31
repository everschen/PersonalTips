
# docker commands summary

### 1) docker container run
启动新容器的命令。该命令的最简形式接收镜像和命令作为参数。镜像用于创建容器，而命令则是希望容器运行的应用。
docker container run -it ubuntu /bin/bash 命令会在前台启动一个 Ubuntu 容器，并运行 Bash Shell。

### 2) docker container ls = sudo docker ps
用于列出所有在运行（UP）状态的容器。如果使用 -a 标记，还可以看到处于停止（Exited）状态的容器。

### 3) docker container exec
用于在运行状态的容器中，启动一个新进程。该命令在将 Docker 主机 Shell 连接到一个运行中容器终端时非常有用。
docker container exec -it <container-name or container-id> bash 命令会在容器内部启动一个 Bash Shell 进程，并连接到该 Shell。

### 4) docker container stop
此命令会停止运行中的容器，并将状态置为 Exited(0)。

### 5) docker container start
重启处于停止（Exited）状态的容器。可以在 docker container start 命令中指定容器的名称或者 ID。

### 6) docker container rm
删除停止运行的容器。可以通过容器名称或者 ID 来指定要删除的容器。推荐首先使用 docker container stop 命令停止容器，然后使用 docker container rm 来完成删除。


### 7) docker container inspect
显示容器的配置细节和运行时信息。该命令接收容器名称和容器 ID 作为主要参数。

### 8) sudo docker images

### 9) 删除image
	sudo docker image rm
	sudo docker image rm -f

### 10) docker search centos

### 11) sudo nvidia-docker pull registry.baidubce.com/paddlepaddle/paddle:2.2.0-gpu-cuda10.2-cudnn7
	sudo nvidia-docker pull registry.baidubce.com/paddlepaddle/paddle

### 12) run the docker
	sudo nvidia-docker run --net=host --ipc=host --rm -it -v $(pwd)/PaddleSpeech:/PaddleSpeech registry.baidubce.com/paddlepaddle/paddle:2.2.0-gpu-cuda10.2-cudnn7 /bin/bash
	sudo nvidia-docker run --net=host --ipc=host --rm -it -v $(pwd)/PaddleSpeech:/PaddleSpeech registry.baidubce.com/paddlepaddle/paddle /bin/bash

	docker run --net=host --ipc=host --rm -it -v $(pwd)/PaddleSpeech:/PaddleSpeech registry.baidubce.com/paddlepaddle/paddle:2.2.0-gpu-cuda10.2-cudnn7 /bin/bash
	docker run --net=host --ipc=host --rm -it -v $(pwd)/PaddleSpeech:/PaddleSpeech registry.baidubce.com/paddlepaddle/paddle /bin/bash

### 13) 提交你刚才修改的镜像，新的镜像名称为demo，版本为v1.3 (docker ps 输出的CONTAINER ID)
    docker commit 4gd0ee60346g3 demo:v1.3

### 14) attach 
docker attach --sig-proxy=false container_id

### 15) 怎么在 docker 中开启多个终端
可以先通过docker ps获取container id，然后通过docker exec -it ${container_id} /bin/bash
