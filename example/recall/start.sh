#!bin/bash

while true;
do
    count=$(ps -ef | grep entrypoint.py | grep -v grep | awk '{print $2}')
    echo "entrypoint:"${count}
    if [ "$count" != "" ];then
        echo "entrypoint is running"
    else
        echo "first running entrypoint..."
        python entrypoint.py &
    fi
    sleep 2
done
