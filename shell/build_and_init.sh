#!/bin/bash

#source ../build/envsetup.sh

first_sim="10.207.49.5"
second_sim="10.229.116.43"

if [ ! -n "$1" ] ;then
    echo "Please input sim env 1 or 2!"
    exit 0
fi

if [ $1 -eq 1 ]; then
    ipaddress=$first_sim
elif [ $1 -eq 2 ]; then
    ipaddress=$second_sim
else
    echo "Please input sim env 1 or 2!"
    exit 0
fi

if [[ -n "$2" ]] && [[ "$2" == "test" ]] ;then
    echo "[DEBUG]For test purpose, ignore build_all"
else
    time=$(date "+%Y-%m-%d %H:%M:%S")
    echo "Start build at: $time"
    build_starttime=$(date +%s)
    echo "build_all"
    build_all
    #sleep 2s
    build_pass=$?
    build_endtime=$(date +%s)
    TIME_DIFF=$(( $build_endtime - $build_starttime ))
    hours=$(( $TIME_DIFF / 3600 ))
    build_cost_str="build time: $(( $TIME_DIFF / 3600 )) hours $(( ($TIME_DIFF - $hours*3600) / 60 )) minutes $(( $TIME_DIFF % 60 )) seconds"
    time=$(date "+%Y-%m-%d %H:%M:%S")
    echo "Build finished at: $time, build cost time: $build_cost_str"
fi

if [ $build_pass -eq 0 ]; then
    image=`ls output/image/GNOSIS_DEBUG/OS-c4dev* 2>NULL`
    echo "$image"
    if [ -z "$image" ]; then  
        echo "no image to reinit"
    else  

        echo "Let's start to reinit: auto_install_upgrade.sh -a $ipaddress -i '$image' -p"
        if [[ -n "$2" ]] && [[ "$2" == "test" ]] ;then
            echo "[DEBUG]For test purpose, ignore auto_install_upgrade.sh"
        else
            reinit_starttime=$(date +%s)
            echo "auto_install_upgrade.sh -a $ipaddress -i '$image' -p"
            auto_install_upgrade.sh -a $ipaddress -i "$image" -p
            #sleep 1s
            reinit_endtime=$(date +%s)
            TIME_DIFF=$(( $reinit_endtime - $reinit_starttime ))
            hours=$(( $TIME_DIFF / 3600 ))
            reinit_cost_str="build time: $(( $TIME_DIFF / 3600 )) hours $(( ($TIME_DIFF - $hours*3600) / 60 )) minutes $(( $TIME_DIFF % 60 )) seconds"
        fi
        echo "Reinit finished: (auto_install_upgrade.sh -a $ipaddress -i '$image' -p), reinit cost time: $reinit_cost_str"
    fi 
else
    echo "failed"
fi

time=$(date "+%Y-%m-%d %H:%M:%S")
echo "Finished at: $time, build cost time: $build_cost_str, reinit cost time: $reinit_cost_str"



