#!/bin/bash

while [ 1 ]
do
    if [ $(($(date '+%S') % 5)) -eq 0 ]
    then
        # echo $(date "+%S")
        git commit -m "$1"
        git log
        break
    fi
done