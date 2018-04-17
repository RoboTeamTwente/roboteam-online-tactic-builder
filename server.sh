#!/usr/bin/env bash

nohup roslaunch roboteam_tactics TwoTeams.launch &> logs/roslaunch.out&
nohup redis-server &> logs/redis.out&
nohup python ./websimulator/manage.py runserver 0.0.0.0:8000 &> logs/server.out&
nohup python ./websimulator/manage.py runworker simulator &> logs/simulator.out&
nohup python ./websimulator/manage.py runworker listener &> logs/listener.out&



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