#!/bin/bash

if [ $# != 1 ]; then
	echo "please input lable, vowifi_20160405_02 for example!"
	exit 1
fi



for dir in $(find . -mindepth 1 -maxdepth 1 -type d)
do
	echo start to remove label $1 for $dir code
	cd $dir
	git push origin :refs/tags/$1
	git tag -d $1
	cd ..
done

rm -rf ~/BUILD/$1

