#!/bin/bash

for dir in $(find . -mindepth 1 -maxdepth 1 -type d)
do
	echo start to update $dir code
	cd $dir && git pull
	cd ..
done



