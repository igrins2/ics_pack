# -*- coding: utf-8 -*-
"""
Created on Nov 9, 2022

Created on July 26, 2023

@author: hilee
"""

import os, sys
from socket import *
import threading
import time as ti
from distutils.util import strtobool

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SubSystems_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

class pdu(threading.Thread) :
    
    def __init__(self):
        
        self.iam = "pdu"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)    
        self.log.send(self.iam, INFO, "start")
                        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, TSLEEP, REBUFSIZE
        TOUT = int(cfg.get(HK, "tout"))
        TSLEEP = int(cfg.get('HK','tsleep'))
        REBUFSIZE = int(cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_routing_key')
        self.dt_sub_ex = cfg.get(MAIN, 'dt_exchange')     
        self.dt_sub_q = cfg.get(MAIN, 'dt_routing_key')
        self.sub_q = self.iam+'.q'
                
        self.power_str = cfg.get(HK, "pdu-list").split(',')
        self.pow_flag = [OFF for _ in range(PDU_IDX)]
        
        simul = strtobool(cfg.get(MAIN, "simulation"))
        if simul:
            self.ip = "localhost"
            self.comport = int(cfg.get(HK, "pdu-port")) + 50000
        else:
            self.ip = cfg.get(HK, "pdu-ip")
            self.comport = cfg.get(HK, "pdu-port")
        
        #---------------------------------------------------------
        # start        
        self.comSocket = None
        self.comStatus = False
                
        self.producer = None
        self.consumer_hk = None
        self.consumer_dt = None
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.close_component()
        
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None
        self.consumer_hk = None
        self.consumer_dt = None
        
        self.log.send(self.iam, DEBUG, "Closed!")                    
            
                    
        
    def connect_to_component(self):
            
        try:            
            self.comSocket = socket(AF_INET, SOCK_STREAM)
            self.comSocket.settimeout(TOUT)
            self.comSocket.connect((self.ip, int(self.comport)))
            self.comStatus = True
            
            msg = "connected"
            self.log.send(self.iam, INFO, msg)
            
        except:
            self.comSocket = None
            self.comStatus = False
            
            msg = "disconnected"
            self.log.send(self.iam, ERROR, msg)
            
            self.re_connect_to_component()
                        
        msg = "%s %d" % (HK_REQ_COM_STS, self.comStatus)   
        self.publish_to_queue(msg)
    
    
    def re_connect_to_component(self):
        #self.th.cancel()
        
        msg = "trying to connect again"
        self.log.send(self.iam, WARNING, msg)
            
        if self.comSocket != None:
            self.close_component()
        ti.sleep(1)
        self.connect_to_component()        

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        

    def initPDU(self):
        if not self.comStatus:  return 
        
        try:
            cmd = "@@@@\r"
            self.comSocket.send(cmd.encode())
            log = "send >>> %s" % cmd
            self.log.send(self.iam, INFO, log)
            
            res = self.comSocket.recv(REBUFSIZE)
            #log = "recv <<< %s" % res.decode()
            log = "recv <<< IPC ONLINE!"
            self.log.send(self.iam, INFO, log)
            
            cmd = "DN0\r"   
            self.power_status(cmd) 
                
            self.log.send(self.iam, INFO, "powctr init is completed")
                    
        except:
            self.log.send(self.iam, ERROR, "powctr init is error")
                   
            self.comStatus = False
            self.re_connect_to_component()
        
                    
    def power_status(self, cmd):
        if not self.comStatus:  return      
        
        try:
            self.comSocket.send(cmd.encode())
            log = "send >>> %s" % cmd
            self.log.send(self.iam, INFO, log)
            ti.sleep(TSLEEP)
            res = self.comSocket.recv(REBUFSIZE)
            sRes = res.decode()
            #log = "recv <<< %s" % sRes
            log = "recv <<< powctr infor"
            self.log.send(self.iam, INFO, log)
            
            # check PDU status
            pow_flag = ""
            for i in range(PDU_IDX):
                if sRes.find("OUTLET %d ON" % (i + 1,)) >= 0:
                    self.pow_flag[i] = ON
                else:
                    self.pow_flag[i] = OFF
                    
                pow_flag += self.pow_flag[i]
                pow_flag += " "
                
            return pow_flag
            
            #print(pow_flag)
        except:                  
            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error")
            self.re_connect_to_component()
            

    # on/off
    def change_power(self, idx, onoff):  # definition OnOff: ON, OFF
        # this function is used when received PDU On/Off status and change status
        
        if not self.comStatus:  return
        
        cmd = ""
        if onoff == OFF:
            self.pow_flag[idx-1] = OFF
            cmd = "F0%d\r" % idx
        elif onoff == ON:
            self.pow_flag[idx-1] = ON
            cmd = "N0%d\r" % idx
            
        msg = " %s Button clicked"  % self.pow_flag[idx-1]
        self.log.send(self.iam, INFO, self.power_str[idx-1] + msg)
    
        return self.power_status(cmd)
            
    
    #-------------------------------
    # pdu publisher
    def connect_to_server_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()     
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.sub_q, msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
           
           
    #-------------------------------
    # hk queue
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer_hk = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        self.consumer_hk.connect_to_server()
        self.consumer_hk.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=self.consumer_hk.start_consumer)
        th.start()
                          
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_PWR_STS or param[0] == HK_REQ_PWR_ONOFF_IDX or param[0] == HK_REQ_PWR_ONOFF):    return

        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                     
        try:                                  
            if param[0] == HK_REQ_PWR_STS:
                pow_flag = self.power_status("DN0\r")
                msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
                self.publish_to_queue(msg)
                
            elif param[0] == HK_REQ_PWR_ONOFF_IDX:
                pow_flag = self.change_power(int(param[1]), param[2]) 
                msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
                self.publish_to_queue(msg)
                
            elif param[0] == HK_REQ_PWR_ONOFF:
                #print('CLI >> PDU', param)
                for idx in range(PDU_IDX):
                    pow_flag = self.change_power(idx+1, param[idx+1])
                    
                msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
                self.publish_to_queue(msg)
        
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
                
                
    #-------------------------------
    # dt queue
    def connect_to_server_dt_q(self):
        # RabbitMQ connect
        self.consumer_dt = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_sub_ex)      
        self.consumer_dt.connect_to_server()
        self.consumer_dt.define_consumer(self.dt_sub_q, self.callback_dt)
        
        th = threading.Thread(target=self.consumer_dt.start_consumer)
        th.start()
                          
    
    def callback_dt(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_PWR_STS or param[0] == HK_REQ_PWR_ONOFF):    return

        msg = "<- [DTP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                                 
        try:                      
            if param[0] == HK_REQ_PWR_STS:
                pow_flag = self.power_status("DN0\r")
                msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
                self.publish_to_queue(msg)
                
            #elif param[0] == HK_REQ_PWR_ONOFF_IDX:
            #    pow_flag = self.change_power(int(param[1]), param[2]) 
            #    msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
            #    self.publish_to_queue(msg)

            elif param[0] == HK_REQ_PWR_ONOFF:
                #pow_flag = self.power_status("DN0\r")
                #pow_sts = pow_flag.split()
                pow_flag = ""
                for idx in range(PDU_IDX):
                    pow_flag += self.pow_flag[idx]
                    pow_flag += " "

                for idx in range(PDU_IDX):
                    if self.pow_flag[idx] != param[idx+1]:
                        pow_flag = self.change_power(idx+1, param[idx+1])
                    
                msg = "%s %sdone" % (HK_REQ_PWR_STS, pow_flag)
                self.publish_to_queue(msg)
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
                        
            
if __name__ == "__main__":
    
    proc = pdu()
            
    proc.connect_to_server_ex()
    
    proc.connect_to_server_hk_q()
    proc.connect_to_server_dt_q()
    
    proc.connect_to_component()
    proc.initPDU()
    
    #for i in range(1, 9):
    #proc.change_power(1, ON)
    #proc.change_power(1, OFF)
    
    '''
    proc = pdu("50023")
    proc.connect_to_component()
    
    proc.initPDU()
    
    st = ti.time()
    
    for i in range(1, 9):
        proc.change_power(i, ON)
    
    duration = ti.time() - st
    print(duration)
    
    #del proc
    '''
    
    
    
    

    

 