# -*- coding: utf-8 -*-
"""
Created on Nov 8, 2022

Modified on May 24, 2023

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

class temp_ctrl(threading.Thread):
    
    def __init__(self, idx):               
            
        self.iam = "tmc%s" % idx        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)
        self.log.send(self.iam, INFO, "start")    
     
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        global TOUT, REBUFSIZE
        TOUT = int(cfg.get(HK, "tout"))
        REBUFSIZE = int(cfg.get(HK, "rebufsize")) 
        
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_sub_ex = cfg.get(MAIN, "hk_exchange")     
        self.hk_sub_q = cfg.get(MAIN, "hk_routing_key")
        self.sub_q = self.iam+'.q'
        
        Period = int(cfg.get(HK,'hk-monitor-intv'))
        
        simul = strtobool(cfg.get(MAIN, "simulation"))
        if simul:
            self.ip = "localhost"
        else:   
            self.ip = cfg.get(HK, "device-server-ip")            
        self.comport = cfg.get(HK, self.iam + "-port")
         
        #self.setpoint = [DEFAULT_VALUE, DEFAULT_VALUE]
                
        self.comSocket = None
        self.comStatus = False
        
        self.producer = None
        self.consumer_hk, self.consumer_uploader = None, None
        
        self.prev_cmd = ""
        self.pause = False
        
        self.wait_time = float(Period/6)
                
        
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
        self.consumer_uploader = None

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
        if self.comSocket != None:
            self.comSocket.close()
        self.comStatus = False
        
        
    # TMC-Get SetPoint
    def get_setpoint(self, port):
        cmd = "SETP? %d" % port
        cmd += "\r\n"
        return cmd
        #return self.socket_send(cmd)
            

    # TMC-Heating Value
    def get_heating_power(self, port):
        cmd = "HTR? %d" % port
        cmd += "\r\n"
        return cmd
        #return self.socket_send(cmd)
    
    
    # TMC-Monitorig
    def get_value(self, port):  
        cmd = "KRDG? " + port
        cmd += "\r\n"
        return cmd
        #return self.socket_send(cmd)


    def socket_send(self, cmd):
        if self.comStatus is False: return

        def send_to(cmd):
            #send     
            self.comSocket.send(cmd.encode())
            
            log = "send >>> %s" % cmd[:-2]
            self.log.send(self.iam, INFO, log)

        def recv_from(again = False) :
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            if again:
                log = "recv <<< %s (again)" % info[:-2]
            else:
                log = "recv <<< %s" % info[:-2]
            self.log.send(self.iam, INFO, log)

            return info

        try:    
            send_to(cmd)
            info = recv_from()
            
            if info.find('\r\n') < 0 or info.find('+') < 0:                
                for _ in range(5):
                    try:
                        info_buffer = recv_from(True)
                        if info_buffer.find('\r\n') >= 0:
                            break
                    except:
                        continue
                
                ti.sleep(self.wait_time)

                #send_to(cmd)
                #info = recv_from()

            return info[:-2]
            
        except:

            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error") 
            self.re_connect_to_component()

            return DEFAULT_VALUE
            
    
    def start_monitoring(self):
        
        #if self.pause:
        #    return
        
        '''
        value = [DEFAULT_VALUE, DEFAULT_VALUE]
        heat = [DEFAULT_VALUE, DEFAULT_VALUE]
        setp = [DEFAULT_VALUE, DEFAULT_VALUE]
            
        value[0] = self.get_value("A")
        ti.sleep(self.wait_time)  
        value[1] = self.get_value("B")     
        ti.sleep(self.wait_time)

        if self.iam != "tmc3":
            heat[0] = self.get_heating_power(1)
            ti.sleep(self.wait_time) 
        heat[1] = self.get_heating_power(2)
        ti.sleep(self.wait_time)

        if self.iam != "tmc3":
            setp[0] = self.get_setpoint(1)
            ti.sleep(self.wait_time)
        setp[1] = self.get_setpoint(2)
        ti.sleep(self.wait_time)
        
        for i in range(2):
            if value[i] == None:
                value[i] = DEFAULT_VALUE
            if heat[i] == None:
                heat[i] = DEFAULT_VALUE
            if setp[i] == None:
                setp[i] = DEFAULT_VALUE

        if self.iam != "tmc3":
            msg = "%s %s %s %s %s %s %s" % (HK_REQ_GETVALUE, value[0], value[1], heat[0], heat[1], setp[0], setp[1]) 
        else:
            msg = "%s %s %s %s %s" % (HK_REQ_GETVALUE, value[0], value[1], heat[1], setp[1]) 
        self.publish_to_queue(msg)
        '''
        
        if self.pause:
            return

        # need to test!!!        
        if self.iam != "tmc3":
            com_len = 6
            res = [DEFAULT_VALUE for _ in range(com_len)]
            cmd_list = [self.get_value("A"), self.get_value("B"), self.get_heating_power(1), self.get_heating_power(2), self.get_setpoint(1), self.get_setpoint(2)]
            idx = 0
            while idx < com_len:
                res[idx] = self.socket_send(cmd_list[idx])
                ti.sleep(self.wait_time)
                if res[idx] == DEFAULT_VALUE:
                    continue
                elif res[idx] == None:
                    res[idx] = DEFAULT_VALUE
                idx += 1
            
            msg = "%s %s %s %s %s %s %s" % (HK_REQ_GETVALUE, res[0], res[1], res[2], res[3], res[4], res[5]) 
            
        else:
            com_len = 4
            res = [DEFAULT_VALUE for _ in range(com_len)]
            cmd_list = [self.get_value("A"), self.get_value("B"), self.get_heating_power(2), self.get_setpoint(2)]
            idx = 0
            while idx < com_len:
                res[idx] = self.socket_send(cmd_list[idx])
                ti.sleep(self.wait_time)
                if res[idx] == DEFAULT_VALUE:
                    continue
                elif res[idx] == None:
                    res[idx] = DEFAULT_VALUE
                idx += 1
            
            msg = "%s %s %s %s %s" % (HK_REQ_GETVALUE, res[0], res[1], res[2], res[3]) 
            
        self.publish_to_queue(msg)
            
        if not self.pause:
            threading.Thread(target=self.start_monitoring).start()

    
    #-------------------------------
    # temp ctrl publisher
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

        if not (param[0] == HK_REQ_MANUAL_CMD): return

        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                            
        if param[0] == HK_REQ_MANUAL_CMD:            
            if self.iam != param[1]:    return
            
            self.pause = True
            
            cmd = ""
            for idx in range(len(param)-2):
                cmd += param[idx+2] + " "
            cmd = cmd[:-1] + "\r\n"
            value = self.socket_send(cmd)
            msg = "%s %s" % (param[0], value) 
            self.publish_to_queue(msg)
            
            self.pause = False
            self.start_monitoring() 
            
            
   
if __name__ == "__main__":
        
    proc = temp_ctrl(sys.argv[1])
    
    proc.connect_to_server_ex()
    
    proc.connect_to_server_hk_q()
    
    proc.connect_to_component()
    proc.start_monitoring()

    
