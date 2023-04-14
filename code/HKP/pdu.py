# -*- coding: utf-8 -*-
"""
Created on Nov 9, 2022

Created on Dec 14, 2022

@author: hilee
"""

import os, sys
from socket import *
import threading
import time as ti

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

class pdu(threading.Thread) :
    
    def __init__(self, simul='0'):
        
        self.iam = "pdu"
        
        self.log = LOG(WORKING_DIR + "IGRINS", "HW")    
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
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_sub_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_sub_routing_key')
        self.sub_hk_q = self.iam+'.q'
                
        self.power_str = cfg.get(HK, "pdu-list").split(',')
        self.pow_flag = [OFF for _ in range(PDU_IDX)]
        
        if bool(int(simul)):
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
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.close_component()
        
        self.producer.__del__()

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
        self.producer.send_message(self.sub_hk_q, msg) 
                 
    
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
        if not self.comStatus:
            return 
        
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
        if not self.comStatus:
            return      
        
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
                
            msg = "%s %s" % (HK_REQ_PWR_STS, pow_flag)
            self.producer.send_message(self.sub_hk_q, msg)  
            print(pow_flag)
        except:                  
            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error")
            self.re_connect_to_component()
            

    # on/off
    def change_power(self, idx, onoff):  # definition OnOff: ON, OFF
        # this function is used when received PDU On/Off status and change status
        
        if not self.comStatus:
            return
        
        cmd = ""
        if onoff == OFF:
            self.pow_flag[idx] = OFF
            cmd = "F0%d\r" % (idx+1)
        elif onoff == ON:
            self.pow_flag[idx] = ON
            cmd = "N0%d\r" % (idx+1)
            
        msg = " %s Button clicked"  % self.pow_flag[idx]
        self.log.send(self.iam, INFO, self.power_str[idx] + msg)
    
        self.power_status(cmd)
            
    
    #-------------------------------
    # sub -> hk    
    def connect_to_server_sub_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()     
           
           
    #-------------------------------
    # hk -> sub
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=consumer.start_consumer)
        th.start()
            
                            
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
                                                       
        if param[0] == HK_REQ_PWR_STS:
            self.power_status("DN0\r")
            
        elif param[0] == HK_REQ_PWR_ONOFF_IDX:
            self.change_power(int(param[1]), param[2]) 
            
        elif param[0] == HK_REQ_PWR_ONOFF:
            print('CLI >> PDU', param)
            for idx in range(PDU_IDX):
                self.change_power(idx, param[idx+1])
                        
            
if __name__ == "__main__":
    
    proc = pdu(sys.argv[1])
            
    proc.connect_to_server_sub_ex()
    proc.connect_to_server_hk_q()
    
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
    
    
    
    

    

 