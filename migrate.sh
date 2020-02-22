SRCIP=$1
TARIP=$2
CONTAIN_NAME=$3

#开启目标主机socket服务
ssh -o StrictHostKeyChecking=no $TARIP 'cd /root/docker_based_cloudlet-master/ && nohup python cloudlet.py service -l >/dev/null 2>log &'
#源主机开启迁移服务
ssh -o StrictHostKeyChecking=no $SRCIP 'cd /root/docker_based_cloudlet-master/ && python cloudlet.py migrate ' $CONTAIN_NAME ' -t ' $TARIP
