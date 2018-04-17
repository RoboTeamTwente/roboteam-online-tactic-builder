#!/usr/bin/env bash

DATETIME=`date '+%Y%m%d_%H_%M_%S'`

mkdir -p logs/$DATETIME

nohup roslaunch roboteam_tactics TwoTeams.launch &> logs/$DATETIME/roslaunch.out&
nohup redis-server &> logs/$DATETIME/redis.out&
nohup python ./websimulator/manage.py runserver 0.0.0.0:8000 &> logs/$DATETIME/server.out&
nohup python ./websimulator/manage.py runworker simulator &> logs/$DATETIME/simulator.out&
nohup python ./websimulator/manage.py runworker listener &> logs/$DATETIME/listener.out&



sleep 2
echo ""
echo "Server started successfully and can be reached at 0.0.0.0:8000"
read -p "Press any key to shut down..."


echo ""
echo "=== THESE LINES CAN BE IGNORED ============="

FOUND=0
for pid in `ps | awk '{print $1}'`
do
    if [ "$FOUND" -eq 1 ]
    then
        kill $pid
    else
        if [ "$$" -eq "$pid" ]
        then
            FOUND=1
        fi
    fi
done

echo "============================================"



echo ""
echo "Server shutdown successfully."