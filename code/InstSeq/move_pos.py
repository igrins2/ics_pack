# -*- coding: utf-8 -*-
"""
Created on Sep 28, 2023

Modified on Sep , 2023

@author: hilee, for sending "Move A" or "Move B" on-sky test without SeqExec
"""

# 1. move => GMP
# 2. position info => ObsApp

import os, sys

import time as ti
import datetime
from distutils.util import strtobool

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from InstSeq_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import cppyy
giapi_root=os.environ.get("GIAPI_ROOT")
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/GeminiUtil.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")

from cppyy.gbl import giapi


class MovePosition(threading.Thread):
    
    def __init__(self):
    
        self.iam = "MovePosition"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")

        self.log.send(self.iam, INFO, giapi_root)
                            
        # ---------------------------------------------------------------   
        # load ini file
        self.ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(self.ini_file)
                
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
                 
        self.producer = None
                                
        self.tcs_waitTime = int(cfg.get(INST_SEQ, "tcs-wait-time"))
                                          
        
    def __del__(self):
        
        for th in threading.enumerate():
            print(th.name + " exit.")              
        
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None
        

        
    def connect_to_server_ex(self):
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam + '.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
            
            
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.iam + '.q', msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        
        
    def send_to_TCS(self, p, q):        
        res = giapi.GeminiUtil.tcsApplyOffset(p, q, giapi.OffsetType.ACQ, self.tcs_waitTime)    # after wait time, no response, res = 0 : wait time -> config.ini
            
        msg = "tcsApplyOffset %.3f %.3f->" % (p, q)
        self.log.send(self.iam, INFO, msg)
                
        msg = "TCS Finished! result is: %d" % res
        self.log.send(self.iam, INFO, msg)
        
        if res == 1:
            msg = "%s %.3f %.3f" % (CUR_P_Q_POS, p, q)
            self.publish_to_queue(msg)
        
        
    def start(self):
        print( '================================================\n'+
            '                Ctrl + C to exit or type: exit  \n'+
            '================================================\n')
                    
        while True:
            print("input p q:", end=" ")
            args = input()
            if args == "exit":
                break
            
            param = list(args.split())    
            if len(param) == 2:
                self.send_to_TCS(float(param[0]), float(param[1]))
    
    
if __name__ == "__main__":
        
    proc = MovePosition()
        
    proc.connect_to_server_ex()
    proc.start()
    
    proc.__del__()
        
