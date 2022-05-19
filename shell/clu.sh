#!/bin/bash

executecmd(){
ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 $2 2>/dev/null
}



FILE_NAME=/root/.ssh/authorized_keys
SSH_PASS='sshpass -p a'
if $SSH_PASS ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 stat $FILE_NAME > /dev/null 2>&1
            then
                    echo "Already initialed!"
            else
ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 'mkdir -p .ssh;echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQCyJcCS6QzL4rHTnwirzb5+1D5UkEvFiBxcUnHlCc+QGEaxztf1CAcgHICqkZcl7o9NDQX1en0oKk6haeg9b7oPzjdJdhmqDae/hrhMfJX5dGfkzyRxmJRbPQzjfzKRtifSIuOOd1P49U66Iy6jIh219tYXkpICGvNvcQ5fYg8a/1XgqoOox2uHXKLATWa72a7sQSb832US/avCWw9cbGvG049mTLZlLw0MuDOePbbBBf91BguxlKetjZwoH9eMDifF8fJ6evFYwe61QynkXlgDIdyh1+hHTDBmjC214w19UlKtZ7htkRjIomR4HWnHJknHL66eL3D/lC3r7y2tWL0iOfdL1lY69FfkVQOr/uby9bUlpdf9TAlQETX2LLiVYqYzTsr5icIcDRL6HzSbv1anVYDKqpLcHmmvTtzZjXyEpFW0BMr2pFQwm1XPA23S94bkCWEZbVaPGaO9WFGMJiKEATc0COCjucq8NeuWCjPm/b+XaoGB27KypKxCeyVeVTSFY7e6ihpQqdX7K5BVs+5LCYviz3P4vNtGVBcwHSzxXL8qRSS62lhxW8Why5qU5lr3ExI21DG3Uzme4e7EMn0KJ0vZ3FXrpU+iGDUhvv1pLPHgLFIdOXy55nghabcQ8Get+kR5Fw9GIsMItOdTdyfQGlsK7fgysPq3DUO57Tm2tw== evers_chen@dell.com" >> ~/.ssh/authorized_keys;echo "ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAACAQDW6O33wxxkbhR1jqZltelpXBP4dCNaVFdllCphh5wMeEcB1tm+Qy998mo3+f+rE250IkZSq0bTP1QVpIB/AUMrDsxaM7lOrk9l1abscL72z/Tli/ec2FGpV1D2sBQfa1rRXmn/O30T9DW4V3UzIq0+Dbnnf7CfQDjE0nUSh+G14xhdv3pqvlQFLD+t88z0kv82WE8ArPiiFLkQDK6b9U2JyKRxn92Lw9vV1lNUKZ5crqHE4WSkzbmOT5Qhkyj4uWCG13P/o1AVCHJIbD0YXwQS/zDbBl9j1y14y/OUtSTArBB8CmNnO+uCJmxBzZz56O8hl/v8yHhXqKGnlwip1xEkWas8bVf9z55obVGMT/POswNszrITtdvtSSRzo0K1vnQowS9WRPCi+K1ZCAovWsjDnxF8eFh0JlAJH4PzXv/aO4taWgcqf0ZU9WppJQYMgSu/m9gPcWPbrANpudUvcmQ5LJ7rehC1pYpHrZSdz+MamSKI3dWJAoo/QbYvAPTr07jepzystFr8S8kkcRPxRDK7k19227FVT4GO1xY2CQaGBgElBE39kDw0lZwBHLVdGqAY54aLGcoR3cBG8xEXZDG/+9nf5aDWLzbGlqzl9zrdAQqIv3QXQjAu4nQ9ZtubrlX1pEozIN3sN2odfeirVVOYLBMXdYczLra+46k1E9wyIw== evers_chen@dell.com" >> ~/.ssh/authorized_keys;' 2>/dev/null
ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 'alias ver="cat /etc/isilon_build_number";mkdir -p "/b/mnt/src";mkdir -p "/b/mnt/obj";mkdir -p "/b/mnt/obj/tmp";export MAKEOBJDIRPREFIX=/b/mnt/obj;export WRKDIRPREFIX=/b/mnt/obj/tmp;mkdir -p "/b/mnt/update"' 2>/dev/null
fi




FILE_NAME=/root/.ali-cluster.sh
if $SSH_PASS ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 stat $FILE_NAME > /dev/null 2>&1
            then
                    echo "Already uploaded .ali-cluster.sh"
            else
scp /ifs/home/echen1/.ali-cluster.sh root@$1:/root
executecmd $1 "echo 'source ~/.ali-cluster.sh' >> ~/.zshrc"
fi


FILE_NAME=/root/check_mem.sh
if [ -n "$2" ]; then
if $SSH_PASS ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 stat $FILE_NAME > /dev/null 2>&1
            then
                    echo "Already uploaded $FILE_NAME"
            else
scp /ifs/home/echen1/check_mem.sh root@$1:/root
fi
fi

name=`ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 'uname -n' 2>/dev/null`
myarray=(`echo $name| tr '-' ' '`)

workspace=`ssh -o ConnectTimeout=30 -o ServerAliveCountMax=3 -o ServerAliveInterval=5 -t root@$1 'cat /etc/isilon_build_number' 2>/dev/null`
myws=(`echo $workspace| tr '.' ' '`)

if [ ${myws[-2]} = "main" ]; then
    tmpws="m"${myws[-1]}
else
    tmpws=${myws[-2]}-${myws[-1]}
fi

echo "set title to "${myarray[1]}-$tmpws
screen -X title ${myarray[1]}-$tmpws

ssh root@"$1"
screen -X title 'home'

