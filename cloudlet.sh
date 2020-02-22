#!/bin/bash
echo 第一个参数：$1
echo 第二个参数：$2

CONTAINER_NAME=$1
TIME=$2
nodelist=(`docker node ls | grep node |awk '{print $2}'`)
i=0
for str in ${nodelist[@]};do
    echo $str
    ips=(`cat /etc/hosts | grep $str | awk '{print $1}'`)
    echo ${ips[*]}
    nodeNameList[i]=$str
    nodeIPList[i]=${ips[*]}
    i=`expr $i + 1`
    done
echo 节点名称列表：${nodeNameList[*]}
echo 节点ip列表：${nodeIPList[*]}

j=0
for z in ${nodeIPList[*]};do
    echo 当前节点为：${nodeNameList[$j]} Ip: $z
    result=`ssh -o StrictHostKeyChecking=no $z docker ps -q -f status=running -f name=$CONTAINER_NAME`
    echo $result
    if [[ $result != '' ]];then
        serverIp=${nodeIPList[$j]}
	echo ${nodeNameList[$j]}节点上存在该服务，Ip: $z
    fi
    echo 节点：${nodeNameList[$j]}不存在该服务 Ip: $z
    j=`expr $j + 1`
    done
echo $serverIp
