"""
... from uploader.py from IGRINS

Modified on Mar 6, 2023

@author: hilee, JJLee
"""

import os, sys
#import time as ti
import datetime
import pytz

import pyrebase
import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
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

HK_DATETIME = 0
HK_VACUUM = 1
HK_BENCH = 2
HK_BENCH_HEATING = 3
HK_GRATING = 4
HK_GRATING_HEATING = 5
HK_DETS = 6
HK_DETS_HEATING = 7
HK_DETK = 8
HK_DETK_HEATING = 9
HK_CAMH = 10
HK_DETH = 11
HK_DETH_HEATING = 12
HK_BENCHCEN = 13
HK_COLDHEAD1 = 14
HK_COLDHEAD2 = 15
HK_COLDSTOP = 16
HK_CHARCOALBOX = 17
HK_CAMK = 18
HK_SHIELDTOP = 19
HK_AIR = 20
class uploader(threading.Thread):
    
    def __init__(self, simul='0'):
        
        self.iam = "uploader"
        
        self.log = LOG(WORKING_DIR + "IGRINS", "HW")    
        self.log.send(self.iam, INFO, "start")
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/"
        cfg = sc.LoadConfig(ini_file + "IGRINS.ini")
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_sub_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_sub_routing_key")
                
        #datetime, vacuum, temperature 14, heating power 5
        self.hk_list = ["" for _ in range(21)]
        
        firebase = self.get_firebase()
        self.db = firebase.database()
    
        #-------
        #for test
        #self.start_upload_to_firebase(self.db)
        #self.log.send(self.iam, INFO, "Uploaded " + ti.strftime("%Y-%m-%d %H:%M:%S"))
        #-------
                
        self.simul = bool(int(simul))
        #self.connect_to_server_hk_q()
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")

        self.log.send(self.iam, DEBUG, "Closed!")
                                    

    def get_firebase(self):
        
        config = {
            "apiKey": "AIzaSyCDUZO9ejB8LzKPtGB0_5xciByJvYI4IzY",
            "authDomain": "igrins2-hk.firebaseapp.com",
            "databaseURL": "https://igrins2-hk-default-rtdb.firebaseio.com",
            "storageBucket": "igrins2-hk.appspot.com",
            "serviceAccount": "/home/ics/workspace/ics/igrins2-hk-firebase-adminsdk-qtt3q-073f6caf5b.json"
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
            self.producer.send_message(self.iam+'.q', msg)

            return True
        
        except:
            self.log.send(self.iam, WARNING, "Upload fail")

            return False
        
        
    #-------------------------------
    # sub -> hk    
    def connect_to_server_sub_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def connect_to_server_hk_q(self):
        # RabbitMQ connect       
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm"]
        sub_hk_ex = [com_list[i]+'.ex' for i in range(COM_CNT-1)]
        consumer = [None for _ in range(COM_CNT-1)]
        for idx in range(COM_CNT-1):
            consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_hk_ex[idx])      
            consumer[idx].connect_to_server()
            
        consumer[TMC1].define_consumer(com_list[TMC1]+'.q', self.callback_tmc1)       
        consumer[TMC2].define_consumer(com_list[TMC2]+'.q', self.callback_tmc2)
        consumer[TMC3].define_consumer(com_list[TMC3]+'.q', self.callback_tmc3)
        consumer[TM].define_consumer(com_list[TM]+'.q', self.callback_tm)
        consumer[VM].define_consumer(com_list[VM]+'.q', self.callback_vm)    
        
        for idx in range(COM_CNT-1):
            th = threading.Thread(target=consumer[idx].start_consumer)
            th.start()       
        
        # ---- from HKP
        consumer_up = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        consumer_up.connect_to_server()
        consumer_up.define_consumer(self.hk_sub_q, self.callback_uploader)
        
        th = threading.Thread(target=consumer_up.start_consumer)
        th.start()
                    
    
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_BENCH] = self.judge_value(param[1])
            self.hk_list[HK_GRATING] = self.judge_value(param[2])
            self.hk_list[HK_BENCH_HEATING] = self.judge_value(param[3])
            self.hk_list[HK_GRATING_HEATING] = self.judge_value(param[4])
            
            print(self.hk_list)
            
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
     
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_DETS] = self.judge_value(param[1])
            self.hk_list[HK_DETK] = self.judge_value(param[2])
            self.hk_list[HK_DETS_HEATING] = self.judge_value(param[3])
            self.hk_list[HK_DETK_HEATING] = self.judge_value(param[4])
            
            print(self.hk_list)
            
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            self.hk_list[HK_CAMH] = self.judge_value(param[1])
            self.hk_list[HK_DETH] = self.judge_value(param[2])
            self.hk_list[HK_DETH_HEATING] = self.judge_value(param[3])
            
            print(self.hk_list)
        
    
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
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
            
            print(self.hk_list)
                
       
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        if len(cmd) < 80:
            self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_REQ_GETVALUE:
            dpvalue = ""
            if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                dpvalue = DEFAULT_VALUE
            else:
                dpvalue = param[1]
            
            self.hk_list[HK_VACUUM] = float(dpvalue)
            
            print(self.hk_list)
            
            
    def callback_uploader(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        if param[0] == HK_REQ_UPLOAD_DB:
            db = param[1:]
            if self.simul:
                print("uploaded virtual firebase database...")
            else:
                #from HKP
                self.start_upload_to_firebase(db)
                
                
    def judge_value(self, input):
        if input != DEFAULT_VALUE:
            value = "%.2f" % float(input)
        else:
            value = input
        return value
    
    
    def uploade_to_GEA(self):
        #need to add time ...
        pass
            

if __name__ == "__main__":
    
    fb = uploader(sys.argv[1])
    
    fb.connect_to_server_sub_ex()
    fb.connect_to_server_hk_q()
    
    
    
    
