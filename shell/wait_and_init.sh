#!/bin/bash


first_sim="10.207.49.5"
second_sim="10.229.116.43"

if [ ! -n "$1" ] ;then
    echo "Please input ese or gos!"
    exit 0
fi

if [ ! -n "$2" ] ;then
    echo "Please input build num like 517!"
    exit 0
fi

if [ ! -n "$3" ] ;then
    echo "Please input array 1/2!"
    exit 0
fi

if [ $3 -eq 1 ]; then
    ipaddress=$first_sim
elif [ $3 -eq 2 ]; then
    ipaddress=$second_sim
else
    echo "Please input sim env 1 or 2!"
    exit 0
fi

if [[ "$1" == "ese" ]]; then
    image="/net/ci-server-21/build_artifacts/s12y-nightly-build-ese/latest/image/GNOSIS_DEBUG/OS-c4dev_HEADR-5.1.0.9.0."$2"-GNOSIS_DEBUG.tgz.bin"
elif [[ "$1" == "gos" ]]; then
    image="/net/ci-server-21/build_artifacts/s12y-nightly-build-goshawk-15/latest/image/GNOSIS_DEBUG/OS-c4dev_HEADR-5.1.0.9.0."$2"-GNOSIS_DEBUG.tgz.bin"
else
    echo "Please input ese or gos for the first parameter!"
    exit 0
fi

echo "waiting for the image $image to be ready!"

#!/bin/bash
wait_starttime=$(date +%s)
image_ready=0
while [ $image_ready -eq 0 ]
do
    #check image is ready?
    sleep 2m
    FILE=/etc/resolv.conf
    if test -f "$image"; then
        echo "$image exists."
        image_ready=1
    else
        echo "$image is not ready."
    fi
done

wait_endtime=$(date +%s)
TIME_DIFF=$(( $wait_endtime - $wait_starttime ))
hours=$(( $TIME_DIFF / 3600 ))
wait_cost_str=" $(( $TIME_DIFF / 3600 )) hours $(( ($TIME_DIFF - $hours*3600) / 60 )) minutes $(( $TIME_DIFF % 60 )) seconds"
echo "wait cost time: $wait_cost_str"


if [ $image_ready -eq 1 ]; then
    #echo "$image"
    echo "Let's start to reinit: auto_install_upgrade.sh -a $ipaddress -i '$image' -p"

    reinit_starttime=$(date +%s)
    echo "auto_install_upgrade.sh -a $ipaddress -i '$image' -p"
    auto_install_upgrade.sh -a $ipaddress -i "$image" -p
    #sleep 1s
    reinit_endtime=$(date +%s)
    TIME_DIFF=$(( $reinit_endtime - $reinit_starttime ))
    hours=$(( $TIME_DIFF / 3600 ))
    reinit_cost_str="build time: $(( $TIME_DIFF / 3600 )) hours $(( ($TIME_DIFF - $hours*3600) / 60 )) minutes $(( $TIME_DIFF % 60 )) seconds"

    echo "Reinit finished: (auto_install_upgrade.sh -a $ipaddress -i '$image' -p), reinit cost time: $reinit_cost_str"

else
    echo "failed"
fi

time=$(date "+%Y-%m-%d %H:%M:%S")
echo "Finished at: $time, wait cost time: $wait_cost_str, reinit cost time: $reinit_cost_str"

