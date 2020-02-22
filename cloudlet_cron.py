#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import struct
from docker import Client
from cloudlet_utl import *
import logging
import time
import subprocess


def get_con_info(name):
    cli = Client(version='1.21')
    out = cli.inspect_container(name)
    if 'Error' in out:
        logging.error('get container id failed')
        return None, None

    image = out['Config']['Image']
    image_id = out['Image']
    label = name + '-' + image + '-' + image_id
    logging.info(label)
    
    # get pid.
    pid = out['State']['Pid']
    logging.info(pid)

    return out['Id'], label, pid, out['Config']['Cmd']


def check_container_status(id):
    cli = Client(version='1.21')
    out = cli.containers(id)
    lines = str(out)
    if 'Id' in lines:
        logging.info('id get by docker-py:%s' % out[0]['Id'])
        return True

    return False

def getSwarmNameList():
    cmd = 'docker node ls | grep node |awk \'{print $2}\''
    back = subprocess.Popen(cmd, shell=True,
	stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()

    return back[0].decode()

def getSwarmIpList(self):
    swarmName = getSwarmNameList()
    self.swarmName = swarmName.split( )
    j=0
    self.swarmIP={}
    for i in self.swarmName:
	cmd = 'cat /etc/hosts | grep '+ i +' | awk \'{print $1}\''
	back = subprocess.Popen(cmd, shell=True,
	stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
	self.swarmIP[j] = str(back[0].decode())
	j += 1

def checkServer(self):
    getSwarmIpList(self)
    for i in self.swarmIP.values():
	cmd = 'bash /root/docker_based_cloudlet-master/checkServer.sh '  + self.con + ' ' + i 
	back = subprocess.Popen(cmd, shell=True,
	stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
	if back[0].decode() != '':
           srcIp = i
	else:
	   tarIp = i
    return srcIp, tarIp

def print_ts(message):
    print "[%s] %s"%(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), message)

def migrate(self):
    print("start migrate--")
    self.srcIp,self.tarIp = checkServer(self)
    print("srcIp: " + self.srcIp)
    print("tarIp: " + self.tarIp)
    if self.srcIp != '' and self.tarIp != '':
       param = str(self.srcIp) + ' ' + str(self.tarIp) + ' ' + self.con
       param = param.split( )
       param = param[0] + ' ' + param[1] + ' ' + param[2]
       cmd = 'bash /root/docker_based_cloudlet-master/migrate.sh '  + param
       print(cmd) 
       back = subprocess.Popen(cmd, shell=True,
       stdout=subprocess.PIPE,stderr=subprocess.PIPE).communicate()
       print(back[0].decode())
       print('server %s from %s to %s migrate success'%(self.con.split( )[0],self.srcIp.split( )[0],self.tarIp.split( )[0]))
       return True
    else:
       print('migrate faild')
       return False

class cron:
    def __init__(self, con, cron_time):
        self.cron_time = cron_time
        self.task_id = random_str()
        self.con = con
        self.con_id, self.label, self.pid ,self.cmd = get_con_info(con)

    def run(self):
	if float(self.cron_time) == 0:
	    return migrate(self)
	else:    
	    interval = int(self.cron_time)*60
	    print_ts("-"*100)
            print_ts("migrate cron start")
            print_ts("Starting every %s seconds."%interval)
            print_ts("-"*100)
            while True:
                try:
                    # sleep for the remaining seconds of interval
                    time_remaining = interval-time.time()%interval
                    print_ts("Sleeping until %s (%s seconds)..."%((time.ctime(time.time()+time_remaining)), time_remaining))
                    time.sleep(time_remaining)
                    print_ts("Starting command.")
                    # execute the command
                    #status = os.system(command)
		    status = migrate(self)
                    print_ts("-"*100)
                    print_ts("Command status = %s."%status)
                except Exception, e:
                    print e

	#return migrate(self)
