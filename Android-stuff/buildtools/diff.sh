#!/bin/bash

for dir in $(find . -mindepth 1 -maxdepth 1 -type d)
do
	echo start to diff $dir code
	cd $dir && git diff 
	cd ..
done



