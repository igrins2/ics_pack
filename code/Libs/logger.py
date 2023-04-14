# -*- coding: utf-8 -*-

"""
Created on Oct 26, 2022

Modified on Dec 14, 2022

@author: hilee
"""

import os
import time as ti
class LOG():

    def __init__(self, work_dir, iam):
                
        self.path = "%s/Log/%s/" % (work_dir, iam)
        self.createFolder(self.path)
        
        
    def createFolder(self, dir):
        try:
            if not os.path.exists(dir):
                os.makedirs(dir)
        except OSError:
            print("Error: Creating directory. " + dir)
        

    def send(self, iam, level, message):
       
        fname = ti.strftime("%Y%m%d", ti.localtime())+".log"
        f_p_name = self.path + fname
        #print(f_p_name)
        if os.path.isfile(f_p_name):
            file=open(f_p_name,'a+')
        else:
            file=open(f_p_name,'w')
                
        msg = "[%s:%s] %s" % (iam, level, message)    
        data = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()) + ": " + msg + "\n"
        #if level != "DEBUG":    
        file.write(data)
        file.close()

        if level != "INFO":
            print(data)