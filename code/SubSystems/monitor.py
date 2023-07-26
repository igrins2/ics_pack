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

class monitor(threading.Thread) :
    
    def __init__(self, idx):  
        
        self.iam = ""
        if idx == '4':
            self.iam = "tm"
        elif idx == '5':
            self.iam = "vm"
            
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)
        self.log.send(self.iam, INFO, "start")  
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(cfg.get(HK, "tout"))
        REBUFSIZE = int(cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, 'ip_addr')
        self.ics_id = cfg.get(MAIN, 'id')
        self.ics_pwd = cfg.get(MAIN, 'pwd')
        
        self.hk_sub_ex = cfg.get(MAIN, 'hk_exchange')     
        self.hk_sub_q = cfg.get(MAIN, 'hk_routing_key')
        self.sub_q = self.iam+'.q'
        
        self.Period = int(cfg.get(HK,'hk-monitor-intv'))
                
        simul = strtobool(cfg.get(MAIN, "simulation"))
        if simul:
            self.ip = "localhost"
        else:
            self.ip = cfg.get(HK, "device-server-ip")
        self.comport = cfg.get(HK, self.iam + "-port")
                
        self.comSocket = None
        self.comStatus = False
        
        self.producer = None    
        self.consumer = None 
                
        
    
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.close_component()
        
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None

        self.consumer = None

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

        #self.th_monitoring.cancel()
        
        msg = "trying to connect again"
        self.log.send(self.iam, WARNING, msg)
            
        if self.comSocket != None:
            self.close_component()
        self.connect_to_component()        

           
    def close_component(self):
        self.comSocket.close()
        self.comStatus = False
        

    # TM-Monitorig
    def get_value_fromTM(self, port=0):
        cmd = "KRDG? %s" % port
        cmd += "\r\n"
        return self.socket_send(cmd)
        
        
    # VM-Monitorig
    def get_value_fromVM(self):
        #PR1 - MicroPirani, PR2/PR5 - Cold Cathode, PR3 - both (3 digits), PR4 - both (4 digits)
        cmd = "@253PR3?;FF"
        cmd += "\r\n"
        return self.socket_send(cmd)
            
    
    def socket_send(self, cmd):
        if self.comStatus is False: return

        try:         
            #send
            self.comSocket.send(cmd.encode())
            #self.comSocket.sendall(cmd.encode())

            log = "send >>> %s" % cmd[:-2]
            self.log.send(self.iam, INFO, log)
            
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            log = "recv <<< %s" % info[:-2]
            if len(info) < 20:
                self.log.send(self.iam, INFO, log)   
                                            
            if self.iam == "tm":
                if info.find('\r\n') < 0:
                    for i in range(10):
                        try:
                            res0 = self.comSocket.recv(REBUFSIZE)
                            info += res0.decode()

                            log = "recv <<< %s (again)" % info[:-2]
                            self.log.send(self.iam, INFO, log)

                            if info.find('\r\n') >= 0:
                                break
                        except:
                            continue
                
                return info[:-2]
            else:
                return info[7:-3]
            
        except:
            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error") 
            self.re_connect_to_component()

            return DEFAULT_VALUE
            
                    
    def start_monitoring(self):
        
        value = [DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE, DEFAULT_VALUE]
        vm = DEFAULT_VALUE

        if self.iam == "tm":
            value = (self.get_value_fromTM().split(","))
        elif self.iam == "vm":
            vm = self.get_value_fromVM()    
            
        if self.iam == "tm":
            msg = HK_REQ_GETVALUE
            for i in range(TM_CNT):
                try:
                    msg += " "
                    msg += value[i]
                except:
                    msg += DEFAULT_VALUE
                    
        elif self.iam == "vm":
            msg = "%s %s" % (HK_REQ_GETVALUE, vm)
        self.publish_to_queue(msg) 

        ti.sleep(self.Period)
        threading.Thread(target=self.start_monitoring).start()
    
    
    #-------------------------------
    # monitor publisher   
    def connect_to_server_ex(self):
        # RabbitMQ connect        
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.sub_q, msg)
        
        if len(msg) > 30:   return
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        
        
    #-------------------------------
    # hk queue
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_sub_ex)      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.hk_sub_q, self.callback_hk)
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.start()
        
    
    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_MANUAL_CMD): return
                      
        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_MANUAL_CMD:       
                if self.iam != param[1]:    return     
                cmd = ""
                for idx in range(len(param)-2):
                    cmd += param[idx+2] + " "
                cmd = cmd[:-1] + "\r\n"
                value = self.socket_send(cmd)
                msg = "%s %s" % (param[0], value) 
                self.publish_to_queue(msg)
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
            
if __name__ == "__main__":
    
    proc = monitor(sys.argv[1])
        
    proc.connect_to_server_ex()
    proc.connect_to_server_hk_q()
    
    proc.connect_to_component()
    
    proc.start_monitoring()