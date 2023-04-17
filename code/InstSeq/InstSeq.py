# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2023

Modified on Apr 17, 2023

@author: hilee
"""

import os, sys
import threading

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from InstSeq_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

class Inst_Seq(threading.Thread):
    
    def __init__(self, simul='0'):
        
        self.iam = "InstSeq"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
                    
        # ---------------------------------------------------------------   
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(ini_file)
                
        self.ics_ip_addr = self.cfg.get(MAIN, "ip_addr")
        self.ics_id = self.cfg.get(MAIN, "id")
        self.ics_pwd = self.cfg.get(MAIN, "pwd")
        
        self.InstSeq_ex = self.cfg.get(MAIN, 'instseq_exchange')
        self.InstSeq_q = self.cfg.get(MAIN, 'instseq_routing_key')
        self.ObsApp_ex = self.cfg.get(MAIN, 'obsapp_exchange')     
        self.ObsApp_q = self.cfg.get(MAIN, 'obsapp_routing_key')
         
        self.producer = None
        self.consumer_ObsApp = None
        self.consumer_dcs = [None for _ in range(DCS_CNT)]
                        
        self.simulation_mode = bool(int(simul))
        
        self.exptime = [0.0, 0.0]   # SVC, H_K
        self.FS_number = [0, 0]     # SVC, H_K
                        
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]    # for receive
        self.dcs_target = ["SVC", "H_K", "all"]     # for command
        self.dcs_ready = [False for _ in range(DCS_CNT)]
                        
        self.connect_to_server_ex()
        
        self.connect_to_server_ObsApp_q()
        self.connect_to_server_dcs_q()
                                     
        
    def __del__(self):
        msg = "Closing %s" % self.iam
        self.log.send(self.iam, DEBUG, msg)
                    
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
            
        self.producer.channel.close()
        self.consumer_ObsApp.channel.close()
        for i in range(DCS_CNT):
            self.consumer_dcs[i].channel.close()

        self.log.send(self.iam, DEBUG, "Closed!") 
        #exit()
        
    
    #--------------------------------------------------------
    # Publish Inst. Sequencer
    def connect_to_server_ex(self):
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
            
        
    
    #--------------------------------------------------------
    # consumer from ObsApp
    def connect_to_server_ObsApp_q(self):
        self.consumer_ObsApp = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_ex)      
        self.consumer_ObsApp.connect_to_server()
        self.consumer_ObsApp.define_consumer(self.ObsApp_q, self.callback_ObsApp)       
        
        th = threading.Thread(target=self.consumer_ObsApp.start_consumer)
        th.start()
    
    
    def callback_ObsApp(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
    
        param = cmd.split()
        
        if param[0] == EXIT:
            self.__del__()          
        
                      
    #--------------------------------------------------------
    # consumer from dcs
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        dcs_InstSeq_ex = [self.dcs_list[i]+'.ex' for i in range(DCS_CNT)]
        for idx in range(DCS_CNT):
            self.consumer_dcs[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, dcs_InstSeq_ex[idx])      
            self.consumer_dcs[idx].connect_to_server()
            
        self.consumer_dcs[SVC].define_consumer(self.dcs_list[SVC]+'.q', self.callback_svc)
        self.consumer_dcs[H].define_consumer(self.dcs_list[H]+'.q', self.callback_h)
        self.consumer_dcs[K].define_consumer(self.dcs_list[K]+'.q', self.callback_k)
        
        for idx in range(DCS_CNT):
            th = threading.Thread(target=self.consumer_dcs[idx].start_consumer)
            th.start()
                        
                
            
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[SVC] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[SVC])
            self.producer.send_message(self.InstSeq_q, msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
                   
    
    def callback_h(self, ch, method, properties, body):
        cmd = body.decode()        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[H] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[H])
            self.producer.send_message(self.InstSeq_q, msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
                    
                    
    def callback_k(self, ch, method, properties, body):
        cmd = body.decode()        
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)

        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[K] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[K])
            self.producer.send_message(self.InstSeq_q, msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
            

    #-------------------------------
    # dcs command
    
    # SVC, H_K, ALL
    def initialize2(self, target_idx):
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, self.dcs_target[target_idx], self.simulation_mode)
        self.producer.send_message(self.InstSeq_q, msg)
        
        
    # SVC or H_K, Not ALL!!!!
    def set_exp(self, target_idx):                        
        _fowlerTime = self.exptime[target_idx] - T_frame * self.FS_number[target_idx]
        msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_target[target_idx], self.simulation_mode, self.exptime[target_idx], self.FS_number, _fowlerTime)
        self.producer.send_message(self.InstSeq_q, msg)

        
    def start_acquisition(self, target_idx):     
        msg = "%s %s %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_target[target_idx], self.simulation_mode)
        self.producer.send_message(self.InstSeq_q, msg)
        
        
        
        
    def save_fits_cube(self):
        pass




if __name__ == "__main__":
        
    #sys.argv.append('1')
    Inst_Seq(sys.argv[1])
    