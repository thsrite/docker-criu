# docker-criu
docker swarm集群间docker checkpoint热迁移方案

代码参考：https://github.com/hixichen/docker_based_cloudlet

Docker checkpoint参考：https://www.jianshu.com/p/2b288415896c

Docker swarm参考：https://www.cnblogs.com/zhujingzhi/p/9792432.html

Criu参考：https://www.cnblogs.com/PPWEI/p/9591660.html

Docker checkpoint参考：https://criu.org/Docker

Python 定时任务参考：https://blog.csdn.net/u012409883/article/details/50425939?depth_1-utm_source=distribute.pc_relevant.none-task&utm_source=distribute.pc_relevant.none-task


环境准备：

Ubuntu18.04    root/123456

Docker client 17.06.0

Criu 3.11

Python 2.7.17

Pip 9.0.1

代码在：/root/docker_based_cloudlet-master

Docker swarm集群：

manager节点ubuntu百度云：链接：https://pan.baidu.com/s/1qiTzX9OyQSrzLuwd0RYVlA 提取码：mn6m  使用使用 cat x* | tar xzvf - 解压

10.211.55.13 manager

10.211.55.15 node1

10.211.55.14 node2

配置manager节点与其他节点的免密登陆。参考：https://blog.51cto.com/6666613/2456451


1.manager创建集群

docker swarm init --advertise-addr 10.211.55.13 

2.node1和node2分别加入集群

docker swarm join --token SWMTKN-1-2ba1ole4efbwxrekxrq7cs81yxf2998ja7mayet9m0osa3as97-abusoel8n1ltgjglid8qqmd2i 10.211.55.13:2377 

3.manager创建网络

docker network create -d overlay looper-net

4.node1节点运行容器looper

docker run -d --name looper --security-opt seccomp:unconfined busybox  \
         /bin/sh -c 'i=0; while true; do echo $i; i=$(expr $i + 1); sleep 1; done'
         
5.node1节点的looper服务迁移到node2节点

(1) node2节点开启socket服务:

cd /root/docker_based_cloudlet-master/ && python cloudlet.py service -l

(2)node1节点执行：

cd /root/docker_based_cloudlet-master/ && python cloudlet.py migrate looper -t 10.211.55.15

6.设置频率自动迁移

cd /root/docker_based_cloudlet-master/ && python cloudlet.py cron looper 0

looper为容器名称

0为定时时间（min）

如果为0，则表示立即迁移，跟方面方法5一样，只不过是自动判断源服务器和目标服务器，无需手动输入

如果大于0，则表示每过多少分钟进行一边迁移。


#[How to use]:

!need root privilege now

    python cloudlet.py [argv]
    example:
    
    VM1:
    
    $python cloudlet.py check
    $python cloudlet.py overlay new_ubuntu  ubuntu
    $docker run -d --name test0 ubuntu
    $python cloudlet.py migrate test0 -t 192.168.x.x(ip of vm2)
    
    VM2:
    $python cloudlet.py service -l
#[support command]:

    cloudlet check

    cloudlet -v

    cloudlet -h

    cloudlet help
#[receive and restore]:

    cloudlet service -l
#[overlay]:

    cloudlet fetch [service name]

    cloudlet search [service name]

    cloudlet overlay  new_image  base image '-o [image_name]'
#[migrate]:

    cloudlet migrate [container id] -t [destionation address]
#[cron]:

    cloudlet cron [container name] [cron time]
