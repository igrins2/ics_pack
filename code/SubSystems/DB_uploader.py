"""
... from uploader.py from IGRINS

Modified on July 26, 2023

@author: hilee, JJLee
"""

import os, sys
#import time as ti
import datetime
import pytz

import pyrebase
import threading

from distutils.util import strtobool

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SubSystems_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

#HKLogPath = WORKING_DIR + "IGRINS/Log/Web/tempweb.dat"

FieldNames = [('date', str), ('time', str),
              ('pressure', float),
              ('bench', float), ('bench_tc', float),
              ('grating', float), ('grating_tc', float),
              ('detS', float), ('detS_tc', float),
              ('detK', float), ('detK_tc', float),
              ('camH', float),
              ('detH', float), ('detH_tc', float),
              ('benchcenter', float), ('coldhead01', float), 
              ('coldhead02', float), ('coldstop', float), 
              ('charcoalBox', float), ('camK', float), 
              ('shieldtop', float), ('air', float), 
              ('alert_status', str)]

# string
GEA_DATETIME        = 0

#values inside dewar
# float
GEA_VACUUM          = 1
GEA_BENCH           = 2
GEA_BENCH_HEATING   = 3
GEA_GRATING         = 4
GEA_GRATING_HEATING = 5
GEA_DETS            = 6
GEA_DETS_HEATING    = 7
GEA_DETK            = 8
GEA_DETK_HEATING    = 9
GEA_CAMH            = 10
GEA_DETH            = 11
GEA_DETH_HEATING    = 12
GEA_BENCHCEN        = 13
GEA_COLDHEAD1       = 14
GEA_COLDHEAD2       = 15
GEA_COLDSTOP        = 16
GEA_CHARCOALBOX     = 17
GEA_CAMK            = 18
GEA_SHIELDTOP       = 19
GEA_AIR             = 20

# set point, float
GEA_BENCH_SP        = 21
GEA_GRATING_SP      = 22
GEA_DETS_SP         = 23
GEA_DETK_SP         = 24
GEA_DETH_SP         = 25

# pdu status, bool
GEA_PDU1_PWR        = 26
GEA_PDU2_PWR        = 27
GEA_PDU3_PWR        = 28
GEA_PDU4_PWR        = 29
GEA_PDU5_PWR        = 30
GEA_PDU6_PWR        = 31
GEA_PDU7_PWR        = 32
GEA_PDU8_PWR        = 33

# com status, bool
GEA_COM_TC1         = 34
GEA_COM_TC2         = 35
GEA_COM_TC3         = 36
GEA_COM_TM          = 37
GEA_COM_VM          = 38
GEA_COM_PDU         = 39


class uploader(threading.Thread):
    
    def __init__(self):
        
        self.iam = "uploader"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/"
        cfg = sc.LoadConfig(ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_routing_key")
                
        #datetime, vacuum, temperature 14, heating power 5, set point 5, pdu status 8, com status 6
        self.hk_list = [None for _ in range(40)]
        
        self.upload_interval = int(cfg.get(HK, "upload-intv"))
        
        self.simul = strtobool(cfg.get(MAIN, "simulation"))

        firebase = self.get_firebase(self.simul)
        self.db = firebase.database()
        
        self.producer = None
        self.consumer = [None for _ in range(COM_CNT)]
        self.consumer_hk = None       
                        
        # publish queue "dewar list"
        threading.Timer(self.upload_interval, self.publish_dewar_list).start()
        
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None
        for i in range(COM_CNT):
            self.consumer[i] = None
        self.consumer_hk = None

        self.log.send(self.iam, DEBUG, "Closed!")
                                    

    def get_firebase(self, simul):
        
        if simul:
            # for test
            config = {
                "apiKey": "AIzaSyDSt_O0KmvB5MjrDXuGJCABAOVNp8Q3ZB8",
                "authDomain": "hkp-db-37e0f.firebaseapp.com",
                "databaseURL": "https://hkp-db-37e0f-default-rtdb.firebaseio.com",
                "storageBucket": "hkp-db-37e0f.appspot.com",
                "serviceAccount": WORKING_DIR + "ics_pack/code/hkp-db-37e0f-firebase-adminsdk-9r23k-a8a806fcb0.json"
            }
        else:
            config = {
                "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
                "authDomain": "igrins2-hk.firebaseapp.com",
                "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
                "storageBucket": "igrins2-hk.appspot.com",
                "serviceAccount": WORKING_DIR + "ics_pack/code/igrins2-hk-firebase-adminsdk-qtt3q-073f6caf5b.json"
            }
            
       
        firebase = pyrebase.initialize_app(config)

        return firebase
    

    def start_upload_to_firebase(self, HK_list):
        HK_dict = self.read_item_to_upload(HK_list)
        if HK_dict is None:
            self.log.send(self.iam, WARNING, "No data ")

        else:
            HK_dict["utc_upload"] = datetime.datetime.now(pytz.utc).isoformat()                
            if self.push_hk_entry(HK_dict):
                self.log.send(self.iam, INFO, HK_dict)


    def read_item_to_upload(self, HK_list):
        if len(HK_list) != len(FieldNames): return None

        HK_dict = dict((k, t(v)) for (k, t), v in zip(FieldNames, HK_list))

        HK_dict["datetime"] = HK_dict["date"] + "T" + HK_dict["time"] + "+00:00"

        return HK_dict
    
    
    def push_hk_entry(self, entry):
        try:
            self.db.child("BasicHK").push(entry)
        
            msg = "%s %s" % (HK_REQ_UPLOAD_STS, self.iam)   
            self.publish_to_queue(msg)

            return True
        
        except:
            self.log.send(self.iam, WARNING, "Upload fail")

            return False
        
        
    #-------------------------------
    # DB uploader publisher 
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
        
    
    #-------------------------------    
    # sub queue
    def connect_to_server_q(self):
        # RabbitMQ connect       
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu"]
        sub_hk_ex = [com_list[i]+'.ex' for i in range(COM_CNT)]
        for idx in range(COM_CNT):
            self.consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_hk_ex[idx])      
            self.consumer[idx].connect_to_server()
            
        self.consumer[TMC1].define_consumer(com_list[TMC1]+'.q', self.callback_tmc1)       
        self.consumer[TMC2].define_consumer(com_list[TMC2]+'.q', self.callback_tmc2)
        self.consumer[TMC3].define_consumer(com_list[TMC3]+'.q', self.callback_tmc3)
        self.consumer[TM].define_consumer(com_list[TM]+'.q', self.callback_tm)
        self.consumer[VM].define_consumer(com_list[VM]+'.q', self.callback_vm)    
        self.consumer[PDU].define_consumer(com_list[PDU]+'.q', self.callback_pdu) 
        
        for idx in range(COM_CNT):
            th = threading.Thread(target=self.consumer[idx].start_consumer)
            th.start()       
        
        # ---- from HKP
        self.consumer_hk = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        self.consumer_hk.connect_to_server()
        self.consumer_hk.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=self.consumer_hk.start_consumer)
        th.start()
                    
    
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE): return

        msg = "<- [TC1] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC1] = bool(int(param[1]))
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_BENCH] = float(param[1])
                self.hk_list[GEA_GRATING] = float(param[2])
                self.hk_list[GEA_BENCH_HEATING] = float(param[3])
                self.hk_list[GEA_GRATING_HEATING] = float(param[4])
                self.hk_list[GEA_BENCH_SP] = float(param[5])
                self.hk_list[GEA_GRATING_SP] = float(param[6])
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                                    
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE): return
     
        msg = "<- [TC2] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC2] = bool(int(param[1]))
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_DETS] = float(param[1])
                self.hk_list[GEA_DETK] = float(param[2])
                self.hk_list[GEA_DETS_HEATING] = float(param[3])
                self.hk_list[GEA_DETK_HEATING] = float(param[4])
                self.hk_list[GEA_DETS_SP] = float(param[5])
                self.hk_list[GEA_DETK_SP] = float(param[6])
        
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                                
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE): return

        msg = "<- [TC3] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC3] = bool(int(param[1]))
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_CAMH] = float(param[1])
                self.hk_list[GEA_DETH] = float(param[2])
                self.hk_list[GEA_DETH_HEATING] = float(param[3])
                self.hk_list[GEA_DETH_SP] = float(param[4])
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
                    
    
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE): return

        msg = "<- [TM] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TM] = bool(int(param[1]))
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_BENCHCEN] = float(param[1])
                self.hk_list[GEA_COLDHEAD1] = float(param[2])
                self.hk_list[GEA_COLDHEAD2] = float(param[3])
                self.hk_list[GEA_COLDSTOP] = float(param[4])
                self.hk_list[GEA_CHARCOALBOX] = float(param[5])
                self.hk_list[GEA_CAMK] = float(param[6])
                self.hk_list[GEA_SHIELDTOP] = float(param[7])
                self.hk_list[GEA_AIR] = float(param[8])
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
                            
       
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE): return
        
        msg = "<- [VM] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_VM] = bool(int(param[1]))
            
            elif param[0] == HK_REQ_GETVALUE:
                dpvalue = ""
                if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                    dpvalue = float(DEFAULT_VALUE)
                else:
                    dpvalue = float(param[1])
                
                self.hk_list[GEA_VACUUM] = dpvalue
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
            
        
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
                
        msg = "<- [VM] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_PDU] = bool(int(param[1]))
            
            elif param[1] == HK_REQ_PWR_STS:
                for i in range(PDU_IDX):
                    self.hk_list[GEA_PDU1_PWR+i] = bool(int(param[i+1]))
        
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                                
            
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_UPLOAD_DB):  return

        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_UPLOAD_DB:
                db = param[1:]
                if self.simul:
                    print("uploaded virtual firebase database...")
                
                self.start_upload_to_firebase(db)
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                    
    '''            
    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input
        return value
    '''
    
            
        
    def publish_dewar_list(self):
        
        hk_entries = [self.hk_list[GEA_VACUUM],
                      self.hk_list[GEA_BENCH],     self.hk_list[GEA_BENCH_SP],
                      self.hk_list[GEA_GRATING],   self.hk_list[GEA_GRATING_SP],
                      self.hk_list[GEA_DETS],      self.hk_list[GEA_DETS_SP],
                      self.hk_list[GEA_DETK],      self.hk_list[GEA_DETK_SP],
                      self.hk_list[GEA_CAMH],    
                      self.hk_list[GEA_DETH],      self.hk_list[GEA_DETH_SP],
                      self.hk_list[GEA_BENCHCEN],
                      self.hk_list[GEA_COLDHEAD1],    
                      self.hk_list[GEA_COLDHEAD2],    
                      self.hk_list[GEA_COLDSTOP],
                      self.hk_list[GEA_CHARCOALBOX],    
                      self.hk_list[GEA_CAMK],  
                      self.hk_list[GEA_SHIELDTOP],
                      self.hk_list[GEA_AIR]]  
        
        str_log = "    ".join(list(map(str, hk_entries)))     
        msg = "%s %s" % (UPLOAD_Q, str_log)
        self.publish_to_queue(msg)

        threading.Timer(self.upload_interval, self.publish_dewar_list).start()
        
        
    def uploade_to_GEA(self):
        #need to add time ...
        pass
            

if __name__ == "__main__":
    
    fb = uploader()
    
    fb.connect_to_server_ex()
    fb.connect_to_server_q()
    
    
    
    
