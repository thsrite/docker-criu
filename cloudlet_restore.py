#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8
import os
import logging
import commands
import shutil
import tarfile
from cloudlet_filesystem import cloudlet_filesystem
from cloudlet_memory import cloudlet_memory
from cloudlet_utl import *
import time


def lz4_uncompress(in_name='memory.lz4', out_name='pages-1.img'):
    cmd = 'lz4 -d ' + in_name + ' ' + out_name
    logging.info(cmd)
    sp.call(cmd, shell=True)
    os.remove(in_name)


class restore:

    """docstring for ClassName"""

    def __init__(self):
        os.chdir(base_dir + '/tmp/')

    def init_restore(self, task_id, label):
        # set work dir.
        os.mkdir(task_id)
        os.chdir(task_id)
        self.task_id = task_id

        label_ar = label.split('-')
        con_name = label_ar[0]
        base_img = label_ar[1]
        img_id = label_ar[2]
	self.con_name = con_name
	print("con_name: " + con_name)
	print("base_img: "+ base_img)
	print("img_id: "+ img_id)
        logging.debug('keep image id for verify %s ' % img_id)
        logging.debug(label_ar)

        cmd_option = 'docker run --name=foo -d ' + base_img + \
            ' tail -f /dev/null && docker rm -f foo'
        os.system(cmd_option)

        delete_op = 'docker rm -f ' + con_name + ' >/dev/null 2>&1'
        os.system(delete_op)

        #create_op = 'docker create --name=' + con_name + ' --security-opt seccomp:unconfined ' + base_img
	#print(create_op)
        #logging.debug(create_op)
        #ret, id = commands.getstatusoutput(create_op)
        #self.con_id = id
	#print("id: "+ id)
	
    def init_docker_images(self, task_id, label, cmd):
	#docker images load
	label_ar = label.split('-')
        con_name = label_ar[0]
        base_img = label_ar[1]
        img_id = label_ar[2]
	logging.debug('begin reload docker images')

        load_op = 'docker import ' + self.workdir() + '/' + self.task_id + '-image.tar ' + con_name
	print(load_op)
        os.system(load_op)

        create_op = 'docker create --name=' + con_name + ' --security-opt seccomp:unconfined ' + con_name + ' ' + cmd
	print(create_op)
        logging.debug(create_op)
        ret, id = commands.getstatusoutput(create_op)
        self.con_id = id
	print("id: "+ id)
	print('docker images load success')
        return True

    def workdir(self):
        return base_dir + '/tmp/' + self.task_id

    def restore_fs(self):

        restore_filesystem = cloudlet_filesystem(self.con_id, self.task_id)
        if restore_filesystem.restore() is False:
            logging.error('filesystem restore failed\n')
            return False

        return True

    def unpack_img(self, tar_ball, mm_dir):
        os.chdir(self.workdir())
        if not check_file(tar_ball):
            logging.error('file() not exist ,maybe receive error' % dump_mm)
            return False

        t = tarfile.open(tar_ball, "r")
        t.extractall()
        t.close()
        os.chdir(mm_dir)
        # lz4_uncompress()
        os.chdir('../')
        return True

    def premm_restore(self, premm_name, mm_dir):
        self.unpack_img(premm_name, mm_dir)
	print("predump revice success")
	#restory_cmd = 'criu restore --shell-job --images-dir ' + mm_dir
	#logging.debug(restory_cmd)

        #ret = sp.call(restory_cmd, shell=True)
        #logging.info(ret)

        #if ret != 0:
        #    logging.error('criu restore failed')
        #    return False

        # shutil.rmtree(self.workdir())
        return True

    def restore(self, mm_img_name):
        self.unpack_img(mm_img_name, 'mm')
        image_dir = self.workdir() + '/mm'
	mv_op = 'mv ' + image_dir + '/* ' + base_dir + 'containers/' + self.con_id + '/checkpoints/'
	print(mv_op)
	ret = sp.call(mv_op, shell=True)
	logging.info(ret)

        if ret != 0:
            logging.error('mv failed')
            return False

	restore_op = 'docker start --checkpoint=' + self.con_name + 'checkpoint' + self.task_id + ' ' + self.con_name
	print(restore_op)
        #restore_op = 'docker restore --force=true --allow-tcp=true --work-dir=' \
        #    + image_dir + ' --image-dir=' + image_dir + ' ' + self.con_id

        logging.debug(restore_op)

        ret = sp.call(restore_op, shell=True)
        logging.info(ret)

        if ret != 0:
            logging.error('criu restore failed')
            return False

        # shutil.rmtree(self.workdir())
        return True
