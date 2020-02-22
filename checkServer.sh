IP=$2
CONTAINER_NAME=$1
#echo ip: $IP
result=`ssh -o StrictHostKeyChecking=no $IP docker ps -q -f status=running -f name=$CONTAINER_NAME`
#echo $result
if [[ $result != '' ]];then
   echo success
   #echo ${nodeNameList[$j]}节点上存在该服务，Ip: $z
fi

