"""
... from uploader.py from IGRINS

Modified on Apr 26, 2024

@author: hilee, Emma.K
"""

import os, sys
import time as ti
import datetime
import pytz
import random
import pyrebase
import threading

from distutils.util import strtobool

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SubSystems_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import cppyy
giapi_root=os.environ.get("GIAPI_ROOT")
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/EpicsStatusHandler.h")
cppyy.include("giapi/GeminiUtil.h")
cppyy.include("giapi/giapi.h")
cppyy.include("giapi/GiapiUtil.h")
cppyy.include("giapi/StatusUtil.h")
cppyy.include("giapi/giapiexcept.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")

cppyy.include("InstCmdHandler.h")
#cppyy.include("InstStatusHandler.h")

from cppyy.gbl import giapi
from cppyy.gbl import instDummy

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

GEA_Items = {GEA_VACUUM:"vacuum:pressure", 
            
            GEA_BENCH:"bench:temp",
            GEA_BENCH_HEATING:"bench:heatPower",
            GEA_GRATING:"grating:temp", 
            GEA_GRATING_HEATING:"grating:heatPower", 
            GEA_DETS:"dcss:temp", 
            GEA_DETS_HEATING:"dcss:heatPower",
            GEA_DETK:"dcsk:temp", 
            GEA_DETK_HEATING:"dcsk:heatPower",
            GEA_CAMH:"camh:temp", 
            GEA_DETH:"dcsh:temp", 
            GEA_DETH_HEATING:"dcsh:heatPower",
            GEA_BENCHCEN:"benchCenter:temp", 
            GEA_COLDHEAD1:"1stColdHead:temp", 
            GEA_COLDHEAD2:"2ndColdHead:temp", 
            GEA_COLDSTOP:"heaterCover:temp", 
            GEA_CHARCOALBOX:"charcoalBox:temp", 
            GEA_CAMK:"camk:temp", 
            GEA_SHIELDTOP:"radShield:temp", 
            GEA_AIR:"rackAmbient:temp", 
            
            GEA_PDU1_PWR:"macie:power",
            GEA_PDU2_PWR:"vm:power", 
            GEA_PDU3_PWR:"motor:power", 
            GEA_PDU4_PWR:"THLamp:power", 
            GEA_PDU5_PWR:"HCLamp:power",
            
            GEA_COM_PDU:"pdu:com",
            GEA_COM_VM:"vacuum:com",
            GEA_COM_TC1:"tc1:com",
            GEA_COM_TC2:"tc2:com",
            GEA_COM_TC3:"tc3:com",
            GEA_COM_TM:"tm:com"} 
        
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

        self.simul = strtobool(cfg.get(MAIN, "simulation"))
        
        #add 20240119 
        #self.slit_img_flip = cfg.get(SC, 'slit-image-flip')
        self.slit_cen = cfg.get(SC, 'slit-cen').split(",")
        self.pixelscale = cfg.get(SC, 'pixelscale')
                
        #datetime, vacuum, temperature 14, heating power 5, set point 5, pdu status 8, com status 6
        self.hk_list = [0 for _ in range(40)]
        
        self.temp_sts_bench, self.temp_sts_grating, self.temp_sts_air = None, None, None
        self.temp_sts_detH, self.temp_sts_detK, self.temp_sts_detS = None, None, None
        self.temp_cause_detH, self.temp_cause_detK, self.temp_cause_detS = None, None, None
        
        self.upload_interval = int(cfg.get(HK, "upload-intv"))
        self.upload_to_web = strtobool(cfg.get(HK, "upload-to-web"))
        self.publish_interval = int(cfg.get(HK, "hk-monitor-intv"))
        
        # --------------------------------------------
        self.temp_warn_lower, self.temp_normal_lower, self.temp_normal_upper, self.temp_warn_upper = dict() ,dict() ,dict() ,dict() 
        self.label_list = ["tmc1-a", "tmc1-b", "tmc2-a", "tmc2-b", "tmc3-b", "tm-8"]
        for k in self.label_list:
            hk_list = cfg.get(HK, k).split(",")
            if k == "tm-8":
                self.temp_normal_lower[k] = hk_list[0]
                self.temp_normal_upper[k] = hk_list[1]
                self.temp_warn_upper[k] = hk_list[2]
            else:
                self.temp_warn_lower[k] = hk_list[0]
                self.temp_normal_lower[k] = hk_list[1]
                self.temp_normal_upper[k] = hk_list[3]
                self.temp_warn_upper[k] = hk_list[4]
        # --------------------------------------------

        firebase = self.get_firebase()
        self.db = firebase.database()
        
        self.producer = None
        self.consumer = [None for _ in range(COM_CNT)]
        self.consumer_hk = None       
        self.consumer_dcs = [None for _ in range(DCS_CNT)]
        self.consumer_cmd = [None for _ in range(3)]    #add 20240419
        
        self.dcs_enable = [True for _ in range(DCS_CNT)]
        
        self.heartbeat_check_interval = 60
        self.heartbeat_time = [-200 for _ in range(COM_CNT+DCS_CNT)]    # modify 20240422
        
        self.alive = [True for _ in range(COM_CNT+DCS_CNT)]
        
        self.publshing = False
        self.publish_heartbeat()

        # add 20240419
        self.cur_ra = '--:--:--.--'
        self.cur_dec = '+--:--:--.--'
        self.cur_am = -1.0
        self.cur_pa = -1.0
        self.tel_ra=-1.0 # the unit is in degree
        self.tel_dec=-1.0 # the unit is in degree
        
        # add 20240426
        self.epoch = "2024"
        
        for idx in range(COM_CNT+DCS_CNT):
            self.monit_heartbeat(idx)
        
        if not self.simul:    
            # ---------------------------------------------------------------------          
            # create status items
            for idx, item in enumerate(GEA_Items):
                if idx > 20:
                    break
                cmd = "ig2:sts:" + GEA_Items[item]
                #if idx == 0:
                #   giapi.StatusUtil.createStatusItem(cmd, giapi.type.Type.DOUBLE) 
                #else:
                giapi.StatusUtil.createStatusItem(cmd, giapi.type.Type.FLOAT) 
                print(cmd)

            # create alarm items 
            for idx in range(GEA_COM_PDU, len(GEA_Items)):
                cmd = "ig2:alm:" + GEA_Items[idx]            
                giapi.StatusUtil.createAlarmStatusItem(cmd, giapi.type.Type.BOOLEAN)
                print(cmd)
        
            giapi.StatusUtil.createAlarmStatusItem("ig2:alm" + GEA_Items[GEA_BENCH], giapi.type.Type.BOOLEAN) 
            giapi.StatusUtil.createAlarmStatusItem("ig2:alm" + GEA_Items[GEA_GRATING], giapi.type.Type.BOOLEAN) 
            giapi.StatusUtil.createAlarmStatusItem("ig2:alm" + GEA_Items[GEA_DETS], giapi.type.Type.BOOLEAN) 
            giapi.StatusUtil.createAlarmStatusItem("ig2:alm" + GEA_Items[GEA_DETK], giapi.type.Type.BOOLEAN) 
            giapi.StatusUtil.createAlarmStatusItem("ig2:alm" + GEA_Items[GEA_DETH], giapi.type.Type.BOOLEAN) 
            
            # create health items
            # FR for testiong TODO.revert
            #giapi.StatusUtil.createHealthStatusItem("ig2:health") 
            giapi.StatusUtil.createHealthStatusItem("ig2:ics:health") 
            giapi.StatusUtil.createHealthStatusItem("ig2:dcsh:health") 
            giapi.StatusUtil.createHealthStatusItem("ig2:dcsk:health") 
            giapi.StatusUtil.createHealthStatusItem("ig2:dcss:health") 
            
            self._callbackStatus = self.callbackStatus
            # for getting tcs information
            #self._handler = instDummy.InstStatusHandler.create(self._callbackStatus)
            
            #pStatus =  giapi.GeminiUtil.getChannel("tcs:sad:currentRA", 20)       
            #print (f'The currentRA  is: {pStatus.getDataAsString(0)}') 

            #giapi.GeminiUtil.subscribeEpicsStatus("tcs:sad:currentRA", self._handler)
            #giapi.GeminiUtil.subscribeEpicsStatus("tcs:sad:currentDec", self._handler)
            #giapi.GeminiUtil.subscribeEpicsStatus("tcs:sad:airMass", self._handler)
            # ---------------------------------------------------------------------
        
        # publish queue "dewar list"
        threading.Timer(self.upload_interval, self.publish_dewar_list).start()
        ti.sleep(1)
        threading.Timer(self.publish_interval, self.uploade_to_GEA).start()      
        
        
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
        for i in range(DCS_CNT):
            self.consumer_dcs[i] = None
        #add 20240419
        for i in range(3):
            self.consumer_cmd[i] = None

        self.log.send(self.iam, DEBUG, "STOPPED!")
                                     

    def get_firebase(self):
        
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
            self.log.send(self.iam, WARNING, "No data")

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
        
        
    def publish_heartbeat(self):
        if self.producer == None or self.publshing:
            threading.Timer(2, self.publish_heartbeat).start()
            return
        
        self.publshing = True
        self.producer.send_message(self.iam+'.q', HEART_BEAT)
        self.publshing = False
        
        msg = "%s ->" % HEART_BEAT
        self.log.send(self.iam, DEBUG, msg)
        
        threading.Timer(HEART_BEAT_PUB, self.publish_heartbeat).start()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None or self.publshing:   return
        
        self.publshing = True
        self.producer.send_message(self.iam+'.q', msg)
        self.publshing = False
        
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
                    
                    
    def monit_heartbeat(self, idx):
        
        #msg = "time interval: %.3f" % (ti.time() - self.heartbeat_time[idx])
        #self.log.send(self.iam, DEBUG, msg)
        
        if ti.time() - self.heartbeat_time[idx] > self.heartbeat_check_interval: 
            
            # add 20240422 -> modify 20240425
            if self.alive[idx]:     # when alive -> die, send alarm just 1 time
                if GEA_COM_TC1-34 <= idx <= GEA_COM_PDU-34:
                    self.alarm_com_status(GEA_COM_TC1+idx, "dead")
                
            self.alive[idx] = False
            
        else:
            self.alive[idx] = True

        # modify 20240423
        #threading.Timer(self.heartbeat_check_interval, lambda: self.monit_heartbeat(idx)).start()
        threading.Timer(20, lambda: self.monit_heartbeat(idx)).start()
        
    
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE or param[0] == HEART_BEAT): return

        msg = "<- [TC1] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[TMC1] = ti.time()
            self.alive[TMC1] = True # add 20240422
                
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC1] = bool(int(param[1]))
                self.alarm_com_status(GEA_COM_TC1)            
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_COM_TC1] = True
                self.hk_list[GEA_BENCH] = float(param[1])
                self.hk_list[GEA_GRATING] = float(param[2])
                self.hk_list[GEA_BENCH_HEATING] = float(param[3])
                self.hk_list[GEA_GRATING_HEATING] = float(param[4])
                self.hk_list[GEA_BENCH_SP] = float(param[5])
                self.hk_list[GEA_GRATING_SP] = float(param[6])
                
                self.temp_sts_bench, cause = self.alarm_temperature(self.label_list[0], GEA_BENCH)
                self.temp_sts_grating, cause = self.alarm_temperature(self.label_list[1], GEA_GRATING)
                
        except:
            self.log.send(self.iam, WARNING, "parsing error tmc1")
                                    
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE or param[0] == HEART_BEAT): return
     
        msg = "<- [TC2] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[TMC2] = ti.time()
            self.alive[TMC2] = True # add 20240422
            
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC2] = bool(int(param[1]))
                self.alarm_com_status(GEA_COM_TC2)
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_COM_TC2] = True
                self.hk_list[GEA_DETS] = float(param[1])
                self.hk_list[GEA_DETK] = float(param[2])
                self.hk_list[GEA_DETS_HEATING] = float(param[3])
                self.hk_list[GEA_DETK_HEATING] = float(param[4])
                self.hk_list[GEA_DETS_SP] = float(param[5])
                self.hk_list[GEA_DETK_SP] = float(param[6])
                
                self.temp_sts_detS, self.temp_cause_detS = self.alarm_temperature(self.label_list[2], GEA_DETS)
                self.temp_sts_detK, self.temp_cause_detK = self.alarm_temperature(self.label_list[3], GEA_DETK)
        
        except:
            self.log.send(self.iam, WARNING, "parsing error tmc2")
                                
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
            
        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE or param[0] == HEART_BEAT): return

        msg = "<- [TC3] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[TMC3] = ti.time()
            self.alive[TMC3] = True # add 20240422

            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TC3] = bool(int(param[1]))
                self.alarm_com_status(GEA_COM_TC3)
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_COM_TC3] = True
                self.hk_list[GEA_CAMH] = float(param[1])
                self.hk_list[GEA_DETH] = float(param[2])
                self.hk_list[GEA_DETH_HEATING] = float(param[3])
                self.hk_list[GEA_DETH_SP] = float(param[4])
                
                self.temp_sts_detH, self.temp_cause_detH = self.alarm_temperature(self.label_list[4], GEA_DETH)
                #self.log.send(self.iam, DEBUG, self.temp_sts_detH)
                
        except:
            self.log.send(self.iam, WARNING, "parsing error tmc3")
            
                    
    
    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
            
        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE or param[0] == HEART_BEAT): return

        msg = "<- [TM] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[TM] = ti.time()
            self.alive[TM] = True   # add 20240422

            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_TM] = bool(int(param[1]))
                self.alarm_com_status(GEA_COM_TM)
            
            elif param[0] == HK_REQ_GETVALUE:
                self.hk_list[GEA_COM_TM] = True
                self.hk_list[GEA_BENCHCEN] = float(param[1])
                self.hk_list[GEA_COLDHEAD1] = float(param[2])
                self.hk_list[GEA_COLDHEAD2] = float(param[3])
                self.hk_list[GEA_COLDSTOP] = float(param[4])
                self.hk_list[GEA_CHARCOALBOX] = float(param[5])
                self.hk_list[GEA_CAMK] = float(param[6])
                self.hk_list[GEA_SHIELDTOP] = float(param[7])
                self.hk_list[GEA_AIR] = float(param[8])
                
                self.temp_sts_air, cause = self.alarm_temperature_m(self.label_list[5], GEA_AIR)
                
        except:
            self.log.send(self.iam, WARNING, "parsing error tm")
            
                            
       
    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
            
        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_GETVALUE or param[0] == HEART_BEAT): return
        
        msg = "<- [VM] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[VM] = ti.time()
            self.alive[VM] = True   # add 20240422
           
            dpvalue = ""
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_VM] = bool(int(param[1]))
                self.alarm_com_status(GEA_COM_VM)

            elif param[0] == HK_REQ_GETVALUE:
                #dpvalue = ""
                if len(param[1]) > 10 or param[1] == DEFAULT_VALUE:
                    dpvalue = float(DEFAULT_VALUE)
                    self.hk_list[GEA_COM_VM] = False
                    self.alarm_com_status(GEA_COM_VM)
                else:
                    dpvalue = float(param[1])      
                    self.hk_list[GEA_COM_VM] = True

                self.hk_list[GEA_VACUUM] = dpvalue

            # add 20240427
            if dpvalue == float(DEFAULT_VALUE):
                self.hk_list[GEA_COM_VM] = False
                
        except:
            self.log.send(self.iam, WARNING, "parsing error vm")

        giapi.StatusUtil.postStatus()
            
            
        
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
            
        msg = "<- [PDU] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            #if param[0] == HEART_BEAT:
            self.heartbeat_time[PDU] = ti.time()
            self.alive[PDU] = True  # add 20240422
            
            if param[0] == HK_REQ_COM_STS:
                self.hk_list[GEA_COM_PDU] = bool(int(param[1]))
            elif param[0] == HK_REQ_PWR_STS:
                self.hk_list[GEA_COM_PDU] = True
                for i in range(PDU_IDX):
                    if param[i+1] == "on":
                        self.hk_list[GEA_PDU1_PWR+i] = True
                        
                        # add 20240425 when MACIE power on, alarm!
                        if i == 0:  
                            cmd = "ig2:alm:" + GEA_Items[GEA_DETH]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_OK, giapi.alarm.Cause.ALARM_CAUSE_OK) 
                            md = "ig2:alm:" + GEA_Items[GEA_DETK]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_OK, giapi.alarm.Cause.ALARM_CAUSE_OK)
                            md = "ig2:alm:" + GEA_Items[GEA_DETS]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_OK, giapi.alarm.Cause.ALARM_CAUSE_OK)
                            
                    elif param[i+1] == "off":                  
                        self.hk_list[GEA_PDU1_PWR+i] = False
                        
                        # add 20240425 when MACIE power off, alarm!
                        if i == 0:  
                            cmd = "ig2:alm:" + GEA_Items[GEA_DETH]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_FAILURE, giapi.alarm.Cause.ALARM_CAUSE_OTHER, "power off")
                            cmd = "ig2:alm:" + GEA_Items[GEA_DETK]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_FAILURE, giapi.alarm.Cause.ALARM_CAUSE_OTHER, "power off")
                            cmd = "ig2:alm:" + GEA_Items[GEA_DETS]
                            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_FAILURE, giapi.alarm.Cause.ALARM_CAUSE_OTHER, "power off")
                                                    
                    self.log.send(self.iam, DEBUG, self.hk_list[GEA_PDU1_PWR+i])
        
        except:
            self.log.send(self.iam, WARNING, "parsing error pdu")
                                
            
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_UPLOAD_DB):  return

        msg = "<- [HKP] %s" % cmd 
        self.log.send(self.iam, INFO, msg)

        try: 
            if param[0] == HK_REQ_UPLOAD_DB: 
                db = param[1:] 
                if not self.upload_to_web:    return
                
                if self.simul: 
                    print("uploaded virtual firebase database...")
                
                self.start_upload_to_firebase(db)
                
        except: 
            self.log.send(self.iam, WARNING, "parsing error hk")
                    
    
    #-------------------------------
    # dcs queue
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        dcs_list = ["DCSS", "DCSH", "DCSK"] 
        dcs_dt_ex = [dcs_list[i]+'.ex' for i in range(DCS_CNT)] 
        for idx in range(DCS_CNT):
            self.consumer_dcs[idx] = MsgMiddleware(self.iam, self.ics_ip_addr,self.ics_id, self.ics_pwd, dcs_dt_ex[idx])
            self.consumer_dcs[idx].connect_to_server()
        
        self.consumer_dcs[SVC].define_consumer(dcs_list[SVC]+'.q',self.callback_svc)
        self.consumer_dcs[H].define_consumer(dcs_list[H]+'.q', self.callback_h)
        self.consumer_dcs[K].define_consumer(dcs_list[K]+'.q', self.callback_k)   
        
        for idx in range(DCS_CNT): 
            th = threading.Thread(target=self.consumer_dcs[idx].start_consumer)
            th.start()
            
    
    def callback_svc(self, ch, method, properties, body): 
        cmd = body.decode()
        param = cmd.split()            

        msg = "<- [DCSS] %s" % cmd 
        self.log.send(self.iam, INFO, msg)
 
        self.dcs_data_processing(param, SVC)
                                               
    
    def callback_h(self, ch, method, properties, body): 
        cmd = body.decode()
        param = cmd.split()

        msg = "<- [DCSH] %s" % cmd 
        self.log.send(self.iam, INFO, msg)
        
        self.dcs_data_processing(param, H)
        
                    
    def callback_k(self, ch, method, properties, body): 
        cmd = body.decode()
        param = cmd.split()
                    
        msg = "<- [DCSK] %s" % cmd 
        self.log.send(self.iam, INFO, msg)
        
        self.dcs_data_processing(param, K)

    #-------------------------------
    # add 20240419 command taking image from InstSeq, ObsApp, DTP -> for saving
    # DC core: Tel RA, Dec
    def connect_to_server_taking_image_q(self):
        # RabbitMQ connect
        cmd_list = ["InstSeq", "dt", "ObsApp"] 
        cmd_ex = [cmd_list[i]+'.ex' for i in range(3)] 
        for idx in range(3): 
            self.consumer_cmd[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, cmd_ex[idx]) 
            self.consumer_cmd[idx].connect_to_server()

        self.consumer_cmd[0].define_consumer(cmd_list[0]+'.q',
                self.callback_InstSeq)
        self.consumer_cmd[1].define_consumer(cmd_list[1]+'.q',
                self.callback_DT)
        self.consumer_cmd[2].define_consumer(cmd_list[2]+'.q',
                self.callback_ObsApp)

        for idx in range(3): 
            th = threading.Thread(target=self.consumer_cmd[idx].start_consumer)
            th.start()


    def callback_InstSeq(self, ch, method, properties, body): 
        cmd = body.decode() 
        param = cmd.split()

        if param[0] != CMD_ACQUIRERAMP_ICS: return

        msg = "<- [InstSeq] %s" % cmd 
        self.log.send(self.iam, INFO, msg)

        self.publish_tel_ra_dec()


    def callback_DT(self, ch, method, properties, body): 
        cmd = body.decode()
        param = cmd.split()

        if param[0] != CMD_ACQUIRERAMP_ICS: return

        msg = "<- [DT] %s" % cmd 
        self.log.send(self.iam, INFO, msg)

        self.publish_tel_ra_dec()



    def callback_ObsApp(self, ch, method, properties, body): 
        cmd = body.decode() 
        param = cmd.split()

        if param[0] != CMD_ACQUIRERAMP_ICS: return

        msg = "<- [ObsApp] %s" % cmd 
        self.log.send(self.iam, INFO, msg)

        self.publish_tel_ra_dec()

        
        
    # from tcs
    def callbackStatus(self, t, statusItem): 
        if self.simul: return
        
        print (f'Recieved the message type is: {t} {giapi.type.DOUBLE} {giapi.type.STRING}') #print (f'{statusItem.getDataAsDouble(0)}')
        
        if  giapi.type.BOOLEAN == t: 
            print (f'{statusItem.getDataAsInt(0)}')
        elif giapi.type.INT == t: 
            print (f'{statusItem.getDataAsInt(0)}') 
        if giapi.type.DOUBLE == t: 
            print (f'{statusItem.getDataAsDouble(0)}') 
        elif giapi.type.STRING == t: 
            print (f'{statusItem.getDataAsString(0)}') 
        elif giapi.type.BYTE == t: 
            print (f'{statusItem.getDataAsByte(0)}') 
        else:
            print (f'Not defined, it is an error')
        
        
    def dcs_data_processing(self, param, idx):
        
        #if param[0] == HEART_BEAT: 
        self.heartbeat_time[UPLOADER+idx] = ti.time() 
        self.alive[UPLOADER+idx] = True # add 20240422
            
        if param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
            self.dcs_enable[idx] = bool(int(param[1]))
    
        elif param[0] == CMD_SETFSPARAM_ICS:   
            self.dcs_enable[idx] = bool(int(param[1]))
                
        elif param[0] == CMD_ACQUIRERAMP_ICS: 
            self.dcs_enable[idx] = bool(int(param[3]))
            
    
    def alarm_com_status(self, idx, err = "communication error"): 
        if self.simul: return
        
        cmd = "ig2:alm:" + GEA_Items[idx] 
        if self.hk_list[idx]:
            giapi.StatusUtil.setAlarm(cmd, giapi.alarm.Severity.ALARM_OK,
                    giapi.alarm.Cause.ALARM_CAUSE_OK) 
            self.log.send(self.iam, INFO, cmd) # add 20240426

        else: giapi.StatusUtil.setAlarm(cmd,
                giapi.alarm.Severity.ALARM_FAILURE,
                giapi.alarm.Cause.ALARM_CAUSE_OTHER, err)
        self.log.send(self.iam, ERROR, cmd)  
            
            
    def alarm_temperature(self, label, idx): 
        cmd = "ig2:alm:" + GEA_Items[idx]
        severity, cause = None, None
        
        if float(self.temp_warn_lower[label]) > self.hk_list[idx]: 
            severity = giapi.alarm.Severity.ALARM_FAILURE 
            cause = giapi.alarm.Cause.ALARM_CAUSE_LOLO
            
        elif float(self.temp_warn_lower[label]) <= self.hk_list[idx] < float(self.temp_normal_lower[label]): 
            severity = giapi.alarm.Severity.ALARM_WARNING 
            cause = giapi.alarm.Cause.ALARM_CAUSE_LO
            
        elif float(self.temp_normal_lower[label]) <= self.hk_list[idx] <= float(self.temp_normal_upper[label]): 
            severity = giapi.alarm.Severity.ALARM_OK 
            cause = giapi.alarm.Cause.ALARM_CAUSE_OK
            
        elif float(self.temp_normal_upper[label]) < self.hk_list[idx] <= float(self.temp_warn_upper[label]): 
            severity = giapi.alarm.Severity.ALARM_WARNING 
            cause = giapi.alarm.Cause.ALARM_CAUSE_HI
            
        elif float(self.temp_warn_upper[label]) < self.hk_list[idx]: 
            severity = giapi.alarm.Severity.ALARM_FAILURE 
            cause = giapi.alarm.Cause.ALARM_CAUSE_HIHI
        
        #if severity != None and cause != None: 
        if severity != giapi.alarm.Severity.ALARM_OK: 
            if not self.simul:
                giapi.StatusUtil.setAlarm(cmd, severity, cause) 
            
            #add 20240105 
            if severity == giapi.alarm.Severity.ALARM_WARNING:
                self.log.send(self.iam, WARNING, GEA_Items[idx] + " warning") 
            elif severity == giapi.alarm.Severity.ALARM_FAILURE:
                self.log.send(self.iam, ERROR, GEA_Items[idx] + " failure")
        
        return severity, cause
            
        
    def alarm_temperature_m(self, label, idx): 
        cmd = "ig2:alm:" + GEA_Items[idx] 
        severity, cause = None, None
    
        if self.hk_list[idx] < float(self.temp_normal_lower[label]): 
            severity = giapi.alarm.Severity.ALARM_WARNING 
            cause = giapi.alarm.Cause.ALARM_CAUSE_LO
            
        elif float(self.temp_normal_lower[label]) <= self.hk_list[idx] <= float(self.temp_normal_upper[label]): 
            severity = giapi.alarm.Severity.ALARM_OK 
            cause = giapi.alarm.Cause.ALARM_CAUSE_OK
            
        elif float(self.temp_normal_upper[label]) < self.hk_list[idx] <= float(self.temp_warn_upper[label]): 
            severity = giapi.alarm.Severity.ALARM_WARNING 
            cause = giapi.alarm.Cause.ALARM_CAUSE_HI
            
        elif float(self.temp_warn_upper[label]) < self.hk_list[idx]: 
            severity = giapi.alarm.Severity.ALARM_FAILURE 
            cause = giapi.alarm.Cause.ALARM_CAUSE_HIHI
            
        #if severity != None and cause != None: 
        if severity != giapi.alarm.Severity.ALARM_OK: 
            if not self.simul:
                giapi.StatusUtil.setAlarm(cmd, severity, cause) 
                        
            #add 20240105 
            if severity == giapi.alarm.Severity.ALARM_WARNING:
                self.log.send(self.iam, WARNING, GEA_Items[idx] + " warning") 
            elif severity == giapi.alarm.Severity.ALARM_FAILURE:
                self.log.send(self.iam, ERROR, GEA_Items[idx] + " failure")
        
        return severity, cause
    
    
    def publish_dewar_list(self):

        #add 20240119, modify 20240426 
        if not self.simul: 
            info = ["tcs:telescopeRA", "tcs:telescopeDec", "tcs:sad:currentRA",
                "tcs:sad:currentDec", "tcs:sad:airMass", "tcs:sad:instrPA",
                "tcs:sad:sourceAInputFrame.VAL", "tcs:sad:sourceAEpoch.VAL"]
            for idx in range(len(info)): 
                for _ in range(3): 
                    try: 
                        pStatus = giapi.GeminiUtil.getChannel(info[idx], 1000)
                        
                        if idx == 0:    
                            value = pStatus.getDataAsDouble(0)
                            self.tel_ra = value 
                        elif idx == 1:  
                            value = pStatus.getDataAsDouble(0) 
                            self.tel_dec = value 
                        elif idx == 2:  
                            value = pStatus.getDataAsString(0)
                            self.cur_ra = value 
                        elif idx == 3:  
                            value = pStatus.getDataAsString(0) 
                            self.cur_dec = value 
                        elif idx == 4:  
                            value = pStatus.getDataAsDouble(0)
                            self.cur_am = value 
                        elif idx == 5:
                            value = pStatus.getDataAsDouble(0) 
                            self.cur_pa = value 
                        elif idx == 6: 
                            value = pStatus.getDataAsString(0) 
                            self.RADecSys = value 
                        elif idx == 7: 
                            value = pStatus.getDataAsString(0) 
                            self.epoch = value
                    
                        #print (f'The {info} is: {self.tel_ra}')
                        self.log.send(self.iam, INFO, f"The {info[idx]} is: {value}") 
                        break
                    
                    except: 
                        self.log.send(self.iam, ERROR, "Error getting tcs info: " + info[idx])
        
        ''' try: if not self.simul: pStatus =
        giapi.GeminiUtil.getChannel("tcs:telescopeRA", 1000) self.tel_ra =
        pStatus.getDataAsDouble(0) print (f'The tcs:telescopeDec is:
        {self.tel_ra}')
                
                pStatus =  giapi.GeminiUtil.getChannel("tcs:telescopeDec",
                        1000) self.tel_dec = pStatus.getDataAsDouble(0) print
                (f'The tcs:telescopeDec is: {self.tel_dec}')

                pStatus =  giapi.GeminiUtil.getChannel("tcs:sad:currentRA",
                        1000) self.cur_ra = pStatus.getDataAsString(0) print
                (f'The tcs:sad:currentRA is: {self.cur_ra}')
                
                pStatus =  giapi.GeminiUtil.getChannel("tcs:sad:currentDec",
                        1000) self.cur_dec = pStatus.getDataAsString(0) print
                (f'The tcs:sad:currentDec is: {self.cur_dec}')
                
                pStatus =  giapi.GeminiUtil.getChannel("tcs:sad:airMass", 1000)
                self.cur_am = pStatus.getDataAsDouble(0) print (f'The
                tcs:sad:airMass is: {self.cur_am}')
                
                #modify 20240107 pStatus =
                giapi.GeminiUtil.getChannel("tcs:sad:instrPA", 1000)
                self.cur_pa = pStatus.getDataAsDouble(0) print (f'The
                tcs:sad:instrPA is: {self.cur_pa}')
        
        except: self.log.send(self.iam, ERROR, "Error getting tcs info") '''
                                
        hk_entries = [self.hk_list[GEA_VACUUM], self.hk_list[GEA_BENCH],
                        self.hk_list[GEA_BENCH_SP], self.hk_list[GEA_GRATING],
                        self.hk_list[GEA_GRATING_SP], self.hk_list[GEA_DETS],
                        self.hk_list[GEA_DETS_SP], self.hk_list[GEA_DETK],
                        self.hk_list[GEA_DETK_SP], self.hk_list[GEA_CAMH],
                        self.hk_list[GEA_DETH],      self.hk_list[GEA_DETH_SP],
                        self.hk_list[GEA_BENCHCEN], self.hk_list[GEA_COLDHEAD1],
                        self.hk_list[GEA_COLDHEAD2],    self.hk_list[GEA_COLDSTOP],
                        self.hk_list[GEA_CHARCOALBOX],    self.hk_list[GEA_CAMK],
                        self.hk_list[GEA_SHIELDTOP], self.hk_list[GEA_AIR], self.cur_ra,
                        self.cur_dec, self.cur_am, #self.slit_img_flip, 
                        self.slit_cen[0], self.slit_cen[1], self.cur_pa, self.pixelscale, self.tel_ra,
                        self.tel_dec, self.RADecSys, self.epoch]  #add 20240119->20240426
        
        str_log = "    ".join(list(map(str, hk_entries)))     
        msg = "%s %s" % (UPLOAD_Q, str_log)
        self.publish_to_queue(msg)

        threading.Timer(self.upload_interval, self.publish_dewar_list).start()
        
    # add 20240419
    def publish_tel_ra_dec(self):
        try:
            if not self.simul:
                pStatus =  giapi.GeminiUtil.getChannel("tcs:telescopeRA", 2000)
                self.tel_ra = pStatus.getDataAsDouble(0)
                print (f'The tcs:telescopeRA is: {self.tel_ra}')

                pStatus =  giapi.GeminiUtil.getChannel("tcs:telescopeDec", 2000)
                self.tel_dec = pStatus.getDataAsDouble(0)
                print (f'The tcs:telescopeDec is: {self.tel_dec}')

        except:
            self.log.send(self.iam, ERROR, "Error getting tel_ra and tel_dec info")

        msg = "%s %f %f" % (UPLOAD_TELRADEC, self.tel_ra, self.tel_dec)
        self.publish_to_queue(msg)

        
    def uploade_to_GEA(self):
        '''
        # --------------------------------------------------------------
        # upload status items
        for key, value in GEA_Items.items():
            if key > 20:
                break
            cmd = "ig2:sts:" + value
          #  if key == 0:
          #      giapi.StatusUtil.setValueAsDouble(cmd, self.hk_list[key])
          #  else:
            stalePrevention = random.uniform(0.000001, 0.000009)
            giapi.StatusUtil.setValueAsFloat(cmd, self.hk_list[key] + stalePrevention)
            msg = "Updating %s" % cmd
            self.log.send(self.iam, DEBUG, msg)
        '''

        
        # --------------------------------------------------------------
        # upload health items        
        # giapi.health.Health.GOOD
        # giapi.health.Health.WARNING
        # giapi.health.Health.BAD        
        
        health = [giapi.health.Health.GOOD for _ in range(5)]    
        
        # ***************************************************************************
        # ICS HEALTH_IG2
        com = True
        if not self.simul:
            for idx in range(6):
                if not self.hk_list[GEA_COM_TC1+idx]:
                    com = False
                    break
    
        alive = True
        for idx in range(6):
            if not self.alive[idx]:
                alive = False
                break
        
        state_ics = GOOD
        
        if self.temp_sts_bench == giapi.alarm.Severity.ALARM_WARNING or \
            self.temp_sts_grating == giapi.alarm.Severity.ALARM_WARNING or \
                self.temp_sts_air == giapi.alarm.Severity.ALARM_WARNING:
            health[HEALTH_ICS] = giapi.health.Health.WARNING
            
            state_ics = TMP_WARN
            
            #add 20240105
            self.log.send(self.iam, WARNING, "ics warning")
            
        state_ics_detail = 111111   #tc1, tc2, tc3, tm, vm, pdu
        if not com or not alive or not self.hk_list[GEA_PDU2_PWR] or \
            self.temp_sts_bench == giapi.alarm.Severity.ALARM_FAILURE or \
            self.temp_sts_grating == giapi.alarm.Severity.ALARM_FAILURE or \
            self.temp_sts_air == giapi.alarm.Severity.ALARM_FAILURE:
            health[HEALTH_ICS] = giapi.health.Health.BAD
            
            if not com:                             state_ics = DISCON
            elif not alive:                         state_ics = STOPPED
            elif not self.hk_list[GEA_PDU2_PWR]:    state_ics = PWR_OFF
            else:                                   state_ics = TMP_ERR 
                
            # add 20240426 if TC1 error
            if not self.hk_list[GEA_COM_TC1] or not self.alive[TMC1] or \
                self.temp_sts_bench == giapi.alarm.Severity.ALARM_FAILURE or \
                self.temp_sts_grating == giapi.alarm.Severity.ALARM_FAILURE:
                state_ics_detail -= pow(10, 5)
                
            # TC2 error
            if not self.hk_list[GEA_COM_TC2] or not self.alive[TMC2]:   state_ics_detail -= pow(10, 4)
            
            # TC3 error
            if not self.hk_list[GEA_COM_TC3] or not self.alive[TMC3]:   state_ics_detail -= pow(10, 3)
                
            # TM error
            if not self.hk_list[GEA_COM_TM] or not self.alive[TM] or \
                self.temp_sts_air == giapi.alarm.Severity.ALARM_FAILURE:     
                state_ics_detail -= pow(10, 2)
                
            # VM error
            if not self.hk_list[GEA_COM_VM] or not self.alive[VM] or \
                not self.hk_list[GEA_PDU2_PWR]:     
                state_ics_detail -= pow(10, 1)
                
            # PDU error
            if not self.hk_list[GEA_COM_PDU] or not self.alive[PDU]:   state_ics_detail -= pow(10, 0)
                                
            self.log.send(self.iam, ERROR, "ics failure")
        
        if not self.simul:    
            giapi.StatusUtil.setHealth("ig2:ics:health", health[HEALTH_ICS])    
        
        # ***************************************************************************
        # DCSH
        state_dcsh = GOOD
        if not self.hk_list[GEA_PDU1_PWR] or not self.dcs_enable[H] or not self.alive[UPLOADER+H] or self.temp_sts_detH == giapi.alarm.Severity.ALARM_FAILURE:
            health[HEALTH_DCSH] = giapi.health.Health.BAD
            
            if not self.dcs_enable[H]:              state_dcsh = DISCON
            elif not self.alive[UPLOADER+H]:        state_dcsh = STOPPED
            elif not self.hk_list[GEA_PDU1_PWR]:    state_dcsh = PWR_OFF
            else:                                   state_dcsh = TMP_ERR
                
            #add 20240105
            self.log.send(self.iam, ERROR, "dcsh failure")
            
        elif self.temp_sts_detH == giapi.alarm.Severity.ALARM_WARNING:
            health[HEALTH_DCSH] = giapi.health.Health.WARNING
            
            state_dcsh = TMP_WARN
            
            #add 20240105
            self.log.send(self.iam, WARNING, "dcsh warning")
        
        if not self.simul:     
            giapi.StatusUtil.setHealth("ig2:dcsh:health", health[HEALTH_DCSH])  
        
        # ***************************************************************************
        # DCSK
        state_dcsk = GOOD
        
        if self.temp_sts_detK == giapi.alarm.Severity.ALARM_WARNING:
            health[HEALTH_DCSK] = giapi.health.Health.WARNING
            
            state_dcsk = TMP_WARN
            
            #add 20240105
            self.log.send(self.iam, WARNING, "dcsk warning")
            
        if not self.hk_list[GEA_PDU1_PWR] or not self.dcs_enable[K] or not self.alive[UPLOADER+K] or self.temp_sts_detK == giapi.alarm.Severity.ALARM_FAILURE:
            health[HEALTH_DCSK] = giapi.health.Health.BAD
            
            if not self.dcs_enable[K]:              state_dcsk = DISCON
            elif not self.alive[UPLOADER+K]:        state_dcsk = STOPPED
            elif not self.hk_list[GEA_PDU1_PWR]:    state_dcsk = PWR_OFF
            else:                                   state_dcsk = TMP_ERR
            
            #add 20240105
            self.log.send(self.iam, ERROR, "dcsk failure")
            
        if not self.simul: 
            giapi.StatusUtil.setHealth("ig2:dcsk:health", health[HEALTH_DCSK])  
        
        # ***************************************************************************
        # DCSS
        state_dcss = GOOD
        
        if self.temp_sts_detS == giapi.alarm.Severity.ALARM_WARNING:
            health[HEALTH_DCSS] = giapi.health.Health.WARNING
            
            state_dcss = TMP_WARN
            
            #add 20240105
            self.log.send(self.iam, WARNING, "dcss warning")
            
        if not self.hk_list[GEA_PDU1_PWR] or not self.dcs_enable[SVC] or not self.alive[UPLOADER+SVC] or self.temp_sts_detS == giapi.alarm.Severity.ALARM_FAILURE:
            health[HEALTH_DCSS] = giapi.health.Health.BAD
            
            if not self.dcs_enable[SVC]:            state_dcss = DISCON
            elif not self.alive[UPLOADER+SVC]:      state_dcss = STOPPED
            elif not self.hk_list[GEA_PDU1_PWR]:    state_dcss = PWR_OFF
            else:                                   state_dcss = TMP_ERR
            
            #add 20240105
            self.log.send(self.iam, ERROR, "dcss failure")
                
        if not self.simul: 
            giapi.StatusUtil.setHealth("ig2:dcss:health", health[HEALTH_DCSS])  
        
        # ***************************************************************************
        # ig2
        for idx in range(1, 5): #change 20240104
            if health[idx] == giapi.health.Health.WARNING:
                health[HEALTH_IG2] = giapi.health.Health.WARNING
                #add 20240105
                self.log.send(self.iam, WARNING, "ig2 warning")
                break
            
        for idx in range(1, 5): #change 20240104
            if health[idx] == giapi.health.Health.BAD:
                health[HEALTH_IG2] = giapi.health.Health.BAD
                #add 20240105
                self.log.send(self.iam, ERROR, "ig2 failure")
                break
            
        if not self.simul:
            # FR for testiong TODO.revert
            #giapi.StatusUtil.setHealth("ig2:health", health[HEALTH_IG2])    
            giapi.StatusUtil.postStatus()
          
        #for i in range(5):
        #    if health[i] == giapi.health.Health.GOOD:       health[i] = 0
        #    elif health[i] == giapi.health.Health.WARNING:  health[i] = 1
        #    elif health[i] == giapi.health.Health.BAD:      health[i] = 2  
        
        # modify 20240215
        try:
            msg = "%s %d %d %d %06d %d %d %d %d %d %d %d %d %.3f %d %d %.3f %d %d %.3f" % (IG2_HEALTH, health[HEALTH_IG2], 
                        health[HEALTH_ICS], state_ics, state_ics_detail, health[HEALTH_DCSS], state_dcss, 
                        health[HEALTH_DCSH], state_dcsh, health[HEALTH_DCSK], state_dcsk,
                        self.temp_sts_detS, self.temp_cause_detS, self.hk_list[GEA_DETS],    # temp S
                        self.temp_sts_detH, self.temp_cause_detH, self.hk_list[GEA_DETH],    # temp H
                        self.temp_sts_detK, self.temp_cause_detK, self.hk_list[GEA_DETK])    # temp K
            self.publish_to_queue(msg)
        except:
            msg = "publish fail"
            self.log.send(self.iam, WARNING, msg)

         # --------------------------------------------------------------
        # upload status items
        if not self.simul:
            for key, value in GEA_Items.items():
                if key > 20:
                    break
                cmd = "ig2:sts:" + value
            #  if key == 0:
            #      giapi.StatusUtil.setValueAsDouble(cmd, self.hk_list[key])
            #  else:
                stalePrevention = random.uniform(0.000001, 0.000009)
                giapi.StatusUtil.setValueAsFloat(cmd, self.hk_list[key] + stalePrevention)
                msg = "Updating %s" % cmd
                self.log.send(self.iam, DEBUG, msg)

        threading.Timer(self.publish_interval, self.uploade_to_GEA).start()
        
            

if __name__ == "__main__":
    
    fb = uploader()
    
    fb.connect_to_server_ex()
    fb.connect_to_server_q()
    
    fb.connect_to_server_dcs_q()
    fb.connect_to_server_taking_image_q()
    
    
    
