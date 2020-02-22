#!/usr/bin/env /usr/local/bin/python
# encoding: utf-8

import os
import tarfile
from cloudlet_check import cloudlet_check
from cloudlet_utl import *
import time


def lz4_compress(level, workdir,parentdir, out_name='memory.lz4'):
    in_name = 'pages-1' + '.img'
    cmd = 'lz4 -'+level + ' ' + workdir + parentdir + '/' + in_name + ' ' + workdir + out_name
    logging.info(cmd)
    sp.call(cmd, shell=True)
    os.remove(in_name)


class cloudlet_memory:

    def __init__(self,task_id):
        self.task_id = task_id
        self.predump_cnt = 0
        os.mkdir(self.workdir())

    def workdir(self):
        return base_dir + 'tmp/' + self.task_id + '/'

    def premm_img_path(self):
        return self.workdir() + self.task_id + '-' + self.premm_name()+'.tar'

    def mm_img_path(self):
        return self.workdir() + self.task_id + '-mm.tar'

    def premm_name(self):
        return 'pre' + str(self.predump_cnt)

    def rename(self):
        os.rename(self.premm_name(), 'pre')

    def images_path(self):
	return self.workdir() + self.task_id + '-image.tar'
     
    def images_name(self):
	return self.task_id + '-image.tar'

    def predump(self, pid):

        # predump , we could done the predump as much as we want.
        # every time, we need the image_dir and parent_dir;
        os.chdir(self.workdir())
        self.predump_cnt += 1
        dir_name = self.premm_name()
        os.mkdir(dir_name)

        if(self.predump_cnt > 1):
            parent_dir = 'pre' + str(self.predump_cnt - 1)

            if not check_dir(self.workdir() + parent_dir):
                logging.error('parent dir not exist')

            parent_path = '../' + parent_dir
            append_cmd = ' --prev-images-dir ' + parent_path
        else:
            append_cmd = ''

        predump_sh = 'criu pre-dump -v2 -t ' + \
            str(pid) + ' --images-dir ' + dir_name + append_cmd

        logging.info(predump_sh)

        out_msg = sp.call(predump_sh, shell=True)
	if out_msg:
            logging.error('criu dump failed')
            return False
        # package it.
        name = self.mm_img_path()
        #self.pack_img(self.workdir(),dir_name, name, dir_name)
	tar_file = tarfile.open(name, 'w')
        tar_file.add(dir_name)
        tar_file.close()
        return True

    def pack_img(self, img_dir,parentdir, name, path):
        os.chdir(img_dir)
        os.chdir(path)
        #lz4_compress('1', self.workdir(),parentdir)
        os.chdir(img_dir)

        tar_file = tarfile.open(name, 'w')
        tar_file.add(path)
        tar_file.close()

        if not check_file(name):
            logging.error("package failed")
            return False
        return True

    def dump(self, con):
        dump_time_b = time.time()
        logging.debug(con)

        prepath = self.workdir() + './pre'
        if not check_dir(prepath):
            logging.debug('pre image is not exist\n')

        mm_dir = 'mm'
        os.mkdir(mm_dir)
        img_path = self.workdir() + mm_dir
        checkpoint_sh = 'docker checkpoint create --checkpoint-dir=' + img_path + ' ' +  con + ' ' + con + 'checkpoint' +  self.task_id
	print(checkpoint_sh)

        logging.debug(checkpoint_sh)

        out_msg = sp.call(checkpoint_sh, shell=True)
        if out_msg:
            logging.error('criu dump failed')
            return False

        dump_time_b2 = time.time()
        name = self.task_id + '-mm.tar'  # eg: /tmp/mytest.tar
	mm_dir = mm_dir + '/' + con + 'checkpoint' +  self.task_id

	tar_file = tarfile.open(name ,'w')
	path = img_path + '/' + con + 'checkpoint' +  self.task_id + '/'
        tar_file.add("mm")
        tar_file.close()

        #self.pack_img(self.workdir(),mm_dir, name, mm_dir)
        dump_time_e = time.time()
        logging.debug('dump handle time:%f' % (dump_time_b2 - dump_time_b))
        logging.debug('dump image pack time:%f' % (dump_time_e - dump_time_b2))

        return True
