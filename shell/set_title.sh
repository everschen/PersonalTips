#!/bin/bash

CRTDIR=$(pwd)

#echo $CRTDIR
if [[ "$CRTDIR" == "/ifs/home/echen1" ]]; then
	screen -X title "home"
else
	cur_branch=`git rev-parse --abbrev-ref HEAD`
	workspace=$(basename $CRTDIR )
	path=(`echo $CRTDIR| tr '/' ' '`)
	#echo ${path[3]}
	jira=(`echo $cur_branch| tr '_' ' '`)
	#echo ${jira[2]}
	echo "set title to "${path[3]}-${jira[2]}
	screen -X title ${path[3]}-${jira[2]}

	#git branch -vv

fi
