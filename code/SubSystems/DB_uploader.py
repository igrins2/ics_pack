"""
... from uploader.py from IGRINS

Modified on Apr 17, 2023

@author: hilee, JJLee
"""

import os, sys
#import time as ti
import datetime
import pytz

import pyrebase
import threading

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

HK_VACUUM = 0
HK_BENCH = 1
HK_BENCH_HEATING = 2
HK_GRATING = 3
HK_GRATING_HEATING = 4
HK_DETS = 5
HK_DETS_HEATING = 6
HK_DETK = 7
HK_DETK_HEATING = 8
HK_CAMH = 9
HK_DETH = 10
HK_DETH_HEATING = 11
HK_BENCHCEN = 12
HK_COLDHEAD1 = 13
HK_COLDHEAD2 = 14
HK_COLDSTOP = 15
HK_CHARCOALBOX = 16
HK_CAMK = 17
HK_SHIELDTOP = 18
HK_AIR = 19

HK_BENCH_SP = 20
HK_GRATING_SP = 21
HK_DETS_SP = 22
HK_DETK_SP = 23
HK_DETH_SP = 24

class uploader(threading.Thread):
    
    def __init__(self):
        
        self.iam = "uploader"
        
        self.log = LOG(WORKING_DIR + "IGRINS", "HW")    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/"
        cfg = sc.LoadConfig(ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_routing_key")
                
        #datetime, vacuum, temperature 14, heating power 5
        self.hk_list = ["" for _ in range(25)]
        
        upload_interval = int(cfg.get(HK, "upload-intv"))
        
        firebase = self.get_firebase()
        self.db = firebase.database()
    
        #-------
        #for test
        #self.start_upload_to_firebase(self.db)
        #self.log.send(self.iam, INFO, "Uploaded " + ti.strftime("%Y-%m-%d %H:%M:%S"))
        #-------
                
        self.simul = bool(cfg.get(MAIN, "simulation"))
        #self.connect_to_server_hk_q()
        
        self.producer = None
        self.consumer = [None for _ in range(COM_CNT)]
        self.consumer_hk = None       
        
        # for getting setpoint from TC1~3
        threading.Timer(3600, self.get_setp).start()
        
        # publish queue "dewar list"
        threading.Timer(upload_interval, self.publish_dewar_list).start()
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.producer.channel.close()
        for i in range(COM_CNT):
            self.consumer[i].channel.close()
        self.consumer_hk.channel.close()

        self.log.send(self.iam, DEBUG, "Closed!")
                                    

    def get_firebase(self):
        
        config = {
            "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
            "authDomain": "igrins2-hk.firebaseapp.com",
            "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
            "storageBucket": "igrins2-hk.appspot.com",
            "serviceAccount": WORKING_DIR + "ics_pack/code/igrins2-hk-firebase-adminsdk-qtt3q-073f6caf5b.json"
            }
        
        '''
        # for test
        config={
            "apiKey": "AIzaSyDSt_O0KmvB5MjrDXuGJCABAOVNp8Q3ZB8",
            "authDomain": "hkp-db-37e0f.firebaseapp.com",
            "databaseURL": "https://hkp-db-37e0f-default-rtdb.firebaseio.com",
            "projectId": "hkp-db-37e0f",
            "storageBucket": "hkp-db-37e0f.appspot.com",
            "messagingSenderId": "1059665885507",
            "appId": "1:1059665885507:web:c4d5dbd322c1c0ff4e17f6",
            "measurementId": "G-450KS9WJF1"
        }
        '''
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
        if len(HK_list) != len(FieldNames):
            return None

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
        if self.producer == None:
            return
        
        self.producer.send_message(self.iam+'.q', msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        
    
    #-------------------------------    
    # sub queue
    def connect_to_server_q(self):
        # RabbitMQ connect       
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm"]
        sub_hk_ex = [com_list[i]+'.ex' for i in range(COM_CNT)]
        for idx in range(COM_CNT):
            self.consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_hk_ex[idx])      
            self.consumer[idx].connect_to_server()
            
        self.consumer[TMC1].define_consumer(com_list[TMC1]+'.q', self.callback_tmc1)       
        self.consumer[TMC2].define_consumer(com_list[TMC2]+'.q', self.callback_tmc2)
        self.consumer[TMC3].define_consumer(com_list[TMC3]+'.q', self.callback_tmc3)
        self.consumer[TM].define_consumer(com_list[TM]+'.q', self.callback_tm)
        self.consumer[VM].define_consumer(com_list[VM]+'.q', self.callback_vm)    
        
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
        
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_BENCH] = self.judge_value(param[1])
            self.hk_list[HK_GRATING] = self.judge_value(param[2])
            self.hk_list[HK_BENCH_HEATING] = self.judge_value(param[3])
            self.hk_list[HK_GRATING_HEATING] = self.judge_value(param[4])
        
        elif param[0] == HK_REQ_GETSETPOINT:
            self.hk_list[HK_BENCH_SP] = self.judge_value(param[1])
            self.hk_list[HK_GRATING_SP] = self.judge_value(param[2])
            
        else:
            return
        
        msg = "<- [TC1] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                        
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
     
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_DETS] = self.judge_value(param[1])
            self.hk_list[HK_DETK] = self.judge_value(param[2])
            self.hk_list[HK_DETS_HEATING] = self.judge_value(param[3])
            self.hk_list[HK_DETK_HEATING] = self.judge_value(param[4])
            
        elif param[0] == HK_REQ_GETSETPOINT:
            self.hk_list[HK_DETS_SP] = self.judge_value(param[1])
            self.hk_list[HK_DETK_SP] = self.judge_value(param[2])
            
        else:
            return
        
        msg = "<- [TC2] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                    
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_CAMH] = self.judge_value(param[1])
            self.hk_list[HK_DETH] = self.judge_value(param[2])
            self.hk_list[HK_DETH_HEATING] = self.judge_value(param[3])
            
        elif param[0] == HK_REQ_GETSETPOINT:
            self.hk_list[HK_DETH_SP] = self.judge_value(param[1])
            
        else:
            return
        
        msg = "<- [TC3] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                    
    
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_BENCHCEN] = self.judge_value(param[1])
            self.hk_list[HK_COLDHEAD1] = self.judge_value(param[2])
            self.hk_list[HK_COLDHEAD2] = self.judge_value(param[3])
            self.hk_list[HK_COLDSTOP] = self.judge_value(param[4])
            self.hk_list[HK_CHARCOALBOX] = self.judge_value(param[5])
            self.hk_list[HK_CAMK] = self.judge_value(param[6])
            self.hk_list[HK_SHIELDTOP] = self.judge_value(param[7])
            self.hk_list[HK_AIR] = self.judge_value(param[8])
            
        else:
            return
        
        msg = "<- [TM] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                            
       
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            dpvalue = ""
            if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                dpvalue = DEFAULT_VALUE
            else:
                dpvalue = param[1]
            
            self.hk_list[HK_VACUUM] = dpvalue
            
        else:
            return
        
        msg = "<- [VM] %s" % cmd
        self.log.send(self.iam, INFO, msg)
            
            
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if param[0] == HK_REQ_UPLOAD_DB:
            db = param[1:]
            if self.simul:
                print("uploaded virtual firebase database...")
            else:
                #from HKP
                self.start_upload_to_firebase(db)
                
        else:
            return
        
        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                
                
    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input
        return value
    
    
    def get_setp(self):
        self.publish_to_queue(HK_REQ_GETSETPOINT)
        
        
    def publish_dewar_list(self):
        
        hk_entries = [self.hk_list[HK_VACUUM],
                      self.hk_list[HK_BENCH],     self.hk_list[HK_BENCH_SP],
                      self.hk_list[HK_GRATING],   self.hk_list[HK_GRATING_SP],
                      self.hk_list[HK_DETS],      self.hk_list[HK_DETS_SP],
                      self.hk_list[HK_DETK],      self.hk_list[HK_DETK_SP],
                      self.hk_list[HK_CAMH],    
                      self.hk_list[HK_DETH],      self.hk_list[HK_DETH_SP],
                      self.hk_list[HK_BENCHCEN],
                      self.hk_list[HK_COLDHEAD1],    
                      self.hk_list[HK_COLDHEAD2],    
                      self.hk_list[HK_COLDSTOP],
                      self.hk_list[HK_CHARCOALBOX],    
                      self.hk_list[HK_CAMK],  
                      self.hk_list[HK_SHIELDTOP],
                      self.hk_list[HK_AIR]]  
        
        str_log = list(map(str, hk_entries))  
        msg = "%s %s" % (UPLOAD_Q, str_log)
        self.publish_to_queue(msg)
        
        
    def uploade_to_GEA(self):
        #need to add time ...
        pass
            

if __name__ == "__main__":
    
    fb = uploader()
    
    fb.connect_to_server_ex()
    fb.connect_to_server_q()
    
    
    
    
