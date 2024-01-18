"""
Created on Feb 15, 2023

Modified on Dec 12, 2023

@author: Francisco, hilee
"""

import os, sys

import time as ti
import datetime
from distutils.util import strtobool

import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SubSystems_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import cppyy
giapi_root=os.environ.get("GIAPI_ROOT")
#giapi_root="/home/ics/giapi-glue-cc"
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/EpicsStatusHandler.h")
cppyy.include("giapi/GeminiUtil.h")
cppyy.include("giapi/GiapiUtil.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")
cppyy.include("InstCmdHandler.h")
cppyy.include("InstStatusHandler.h")

from cppyy.gbl import giapi
from cppyy.gbl import instDummy

channel = ["ag:port:igrins2", \
        "tcs:sad:instrPA", "tcs:sad:currentRma", \
        "tcs:sad:currentRA", "tcs:sad:currentDec", \
        "tcs:sad:airMass", "tcs:sad:airMassNow", \
        "tcs:sad:currentZd", "tcs:sad:LST", \
        "tcs:sad:currentHAString"]

class tcs_info(threading.Thread):
    
    def __init__(self):
        
        self.iam = "tcs_info"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/"
        cfg = sc.LoadConfig(ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")

        self.upload_interval = int(cfg.get(HK, "upload-intv"))
        
        self.producer = None
        
        # for getting tcs information
        handler = instDummy.InstStatusHandler.create(self.callbackStatus)
        
        giapi.GeminiUtil.subscribeEpicsStatus(channel[3], handler)
        giapi.GeminiUtil.subscribeEpicsStatus(channel[4], handler)
        giapi.GeminiUtil.subscribeEpicsStatus(channel[5], handler)
        
        threading.Timer(self.upload_interval, self.publish_tcs_info).start()


    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None

        self.log.send(self.iam, DEBUG, "Closed!")
        

    def callbackStatus(t, statusItem):
        #print (f'Recieved the message type is: {t}')
        #if  giapi.type.BOOLEAN == t:
        #    print (f'{statusItem.getDataAsInt(0)}')
        #elif giapi.type.INT == t:
        #    print (f'{statusItem.getDataAsInt(0)}')
        
        if giapi.type.DOUBLE == t:
            pass
            #print (f'{statusItem.getDataAsDouble(0)}')
        elif giapi.type.STRING == t:
            pass
            #print (f'{statusItem.getDataAsString(0)}')
        #elif giapi.type.BYTE == t:
        #    print (f'{statusItem.getDataAsByte(0)}')
        else:
            print (f'Not defined, it is an error')
        
        
    #-------------------------------
    # tcs_info publisher 
    def connect_to_server_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.iam+'.q', msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        

    def publish_tcs_info(self):
                
        pStatus =  giapi.GeminiUtil.getChannel(channel[3], 20)
        cur_ra = pStatus.getDataAsString(0)
        print (f'The tcs:sad:currentRA is: {cur_ra}')
        
        pStatus =  giapi.GeminiUtil.getChannel(channel[4], 20)
        cur_dec = pStatus.getDataAsString(0)
        print (f'The tcs:sad:currentDec is: {cur_dec}')
        
        pStatus =  giapi.GeminiUtil.getChannel(channel[5], 20)
        cur_am = pStatus.getDataAsDouble(0)
        print (f'The tcs:sad:currentDec is: {cur_am}')
        
        #msg = "%s %s %s %f" % (UPLOAD_TCS_INFO, cur_ra, cur_dec, cur_am)
        #self.publish_to_queue(msg)


if __name__ == "__main__":

    proc = tcs_info()


