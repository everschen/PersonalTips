#!/bin/bash

labl=`date +%Y%m%d_%H%M%S`
labl="vowifi_"$labl
echo "use label: $labl"

./update.sh
mkdir ~/BUILD/$labl
mkdir ~/BUILD/$labl/symbols


for dir in $(find . -mindepth 1 -maxdepth 1 -type d)
do
	echo start to make label $labl for $dir code
	cd $dir
	git tag -a $labl -m "$labl"
	echo " " >> ../$labl.txt
	echo " " >> ../$labl.txt
	echo "--------- $dir -------------" >> ../$labl.txt
	git log -3 >> ../$labl.txt
	echo start to push label $labl for $dir code
	git push origin --tags
	cd ..
done

mv ./$labl.txt ~/BUILD/$labl/

./build-B.sh


cp -p ~/output/dev3/* ~/BUILD/$labl/
cp -p ~/output/dev3/symbols/* ~/BUILD/$labl/symbols/

