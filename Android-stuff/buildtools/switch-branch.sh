#!/bin/bash


for dir in $(find . -mindepth 1 -maxdepth 1 -type d)
do
#	echo start to make label $labl for $dir code
	cd $dir
#	git tag -a $labl -m "$labl"
#	echo " " >> ../$labl.txt
#	echo " " >> ../$labl.txt
	echo " $dir current branch:" 
	git branch
        if [ "$1" != "" ]; then
	    git checkout $1 
        fi

#	echo start to push label $labl for $dir code
#	git push origin --tags
	cd ..
done



if [ "$1" == "sprd-7.0" ]; then
    cd /home/apuser/20160628/sprdroid6.0_trunk_vowifi_dev3/vendor/sprd/proprietories-source/ims_bridged 
	echo " $dir current branch:" 
	git branch
    git checkout sprdroid7.0_trunk_k310_vowifi_dev
fi


if [ "$1" == "sprd" ]; then
    cd /home/apuser/20160628/sprdroid6.0_trunk_vowifi_dev3/vendor/sprd/proprietories-source/ims_bridged 
	echo " $dir current branch:" 
	git branch
    git checkout sprdroid6.0_trunk_16b_rls2_vowifi_cus
fi
