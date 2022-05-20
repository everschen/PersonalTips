#!/bin/bash

git diff auto_hunter_v5.py
git status | grep auto_hunter_v5.py
ret=$?

if [ $ret == 0 ]; then
    git add auto_hunter_v5.py
    git commit -m "update"
else
    echo "no update yet"
fi



