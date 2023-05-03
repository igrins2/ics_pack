# -*- coding: utf-8 -*-
"""
Created on Nov 8, 2022

Modified on Apr 17, 2023

@author: hilee
"""

import os, sys
from socket import *
import threading
import time as ti

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
        
        simul = bool(cfg.get(MAIN, "simulation"))
        if simul:
            self.ip = "localhost"
        else:   
            self.ip = cfg.get(HK, "device-server-ip")            
        self.comport = cfg.get(HK, self.iam + "-port")
         
        self.setpoint = [DEFAULT_VALUE, DEFAULT_VALUE]
                
        self.comSocket = None
        self.comStatus = False
        
        self.producer = None
        self.consumer_hk, self.consumer_uploader = None, None
        
        #self.pause = False
        
        self.wait_time = float(Period/4)
                
        
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.close_component()
        
        self.producer.channel.close()
        self.consumer_hk.channel.close()
        self.consumer_uploader.channel.close()

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
        return self.socket_send(cmd)
            

    # TMC-Heating Value
    def get_heating_power(self, port):
        cmd = "HTR? %d" % port
        cmd += "\r\n"
        return self.socket_send(cmd)
    
    
    # TMC-Monitorig
    def get_value(self, port):  
        cmd = "KRDG? " + port
        cmd += "\r\n"
        return self.socket_send(cmd)


    def socket_send(self, cmd):
        if self.comStatus is False:
            return

        try:    
            #send     
            self.comSocket.send(cmd.encode())
            
            log = "send >>> %s" % cmd[:-2]
            self.log.send(self.iam, INFO, log)
                    
            #rev
            res0 = self.comSocket.recv(REBUFSIZE)
            info = res0.decode()
                    
            log = "recv <<< %s" % info[:-2]
            self.log.send(self.iam, INFO, log)   
            
            if info.find('\r\n') < 0 or info.find('+') < 0:                
                for i in range(5):
                    try:
                        res0 = self.comSocket.recv(REBUFSIZE)
                        info_buffer = res0.decode()

                        log = "recv <<< %s (again)" % info_buffer[:-2]
                        self.log.send(self.iam, INFO, log)

                        if info_buffer.find('\r\n') >= 0:
                            break
                    except:
                        continue

                return DEFAULT_VALUE

            else:
                return info[:-2]
            
        except:

            self.comStatus = False
            self.log.send(self.iam, ERROR, "communication error") 
            self.re_connect_to_component()

            return DEFAULT_VALUE
            
    
    def start_monitoring(self):
        
        #if self.pause:
        #    return
        
        value = [DEFAULT_VALUE, DEFAULT_VALUE]
        heat = [DEFAULT_VALUE, DEFAULT_VALUE]
            
        value[0] = self.get_value("A")
        ti.sleep(self.wait_time)  
        value[1] = self.get_value("B")     
        ti.sleep(self.wait_time)
        if self.iam != "tmc3":
            heat[0] = self.get_heating_power(1)
            ti.sleep(self.wait_time)
        heat[1] = self.get_heating_power(2)
        ti.sleep(self.wait_time)
        
        for i in range(2):
            if value[i] == None:
                value[i] = DEFAULT_VALUE
            if heat[i] == None:
                heat[i] = DEFAULT_VALUE

        if self.iam != "tmc3":
            msg = "%s %s %s %s %s" % (HK_REQ_GETVALUE, value[0], value[1], heat[0], heat[1]) 
        else:
            msg = "%s %s %s %s" % (HK_REQ_GETVALUE, value[0], value[1], heat[1]) 
        self.publish_to_queue(msg)

        threading.Thread(target=self.start_monitoring).start()

    
    #-------------------------------
    # temp ctrl publisher
    def connect_to_server_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam+'.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
    
    def publish_to_queue(self, msg):
        if self.producer == None:
            return
        
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
                            
        if param[0] == HK_REQ_GETSETPOINT:           
            #self.pause = True
            
            if self.iam != "tmc3":
                self.setpoint[0] = self.get_setpoint(1)
                ti.sleep(1)
            self.setpoint[1] = self.get_setpoint(2)
            
            if self.iam != "tmc3":
                msg = "%s %s %s" % (HK_REQ_GETSETPOINT, self.setpoint[0], self.setpoint[1]) 
            else:
                msg = "%s %s" % (HK_REQ_GETSETPOINT, self.setpoint[1])
            self.publish_to_queue(msg)
            
            #self.pause = False
            #self.start_monitoring()            
                                    
        elif param[0] == HK_REQ_MANUAL_CMD:            
            if self.iam != param[1]:
                return
            
            #self.pause = True
            
            cmd = ""
            for idx in range(len(param)-2):
                cmd += param[idx+2] + " "
            cmd = cmd[:-1] + "\r\n"
            value = self.socket_send(cmd)
            msg = "%s %s" % (param[0], value) 
            self.publish_to_queue(msg)
            
            #self.pause = False
            self.start_monitoring() 
            
        else:
            return
        
        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
            
            
    #-------------------------------
    # uploader queue
    def connect_to_server_uploader_q(self):
        # RabbitMQ connect
        self.consumer_uploader = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, "uploader.ex")      
        self.consumer_uploader.connect_to_server()
        self.consumer_uploader.define_consumer("uploader.q", self.callback_uploader)
        
        th = threading.Thread(target=self.consumer_uploader.start_consumer)
        th.start()


    def callback_uploader(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
                            
        if param[0] == HK_REQ_GETSETPOINT:   
            #self.pause = True

            if self.iam != "tmc3":
                self.setpoint[0] = self.get_setpoint(1)
                ti.sleep(1)
            self.setpoint[1] = self.get_setpoint(2)
            
            if self.iam != "tmc3":
                msg = "%s %s %s" % (HK_REQ_GETSETPOINT, self.setpoint[0], self.setpoint[1]) 
            else:
                msg = "%s %s" % (HK_REQ_GETSETPOINT, self.setpoint[1])
            self.publish_to_queue(msg)
            
            #self.pause = False
            #self.start_monitoring() 
        
        else:
            return
        
        msg = "<- [DB uploader] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                                            

if __name__ == "__main__":
        
    proc = temp_ctrl(sys.argv[1])
    
    proc.connect_to_server_ex()
    
    proc.connect_to_server_hk_q()
    proc.connect_to_server_uploader_q()
    
    proc.connect_to_component()
    proc.start_monitoring()

    