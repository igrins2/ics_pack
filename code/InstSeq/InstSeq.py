# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2023

Modified on Apr 17, 2023

@author: hilee
"""

import os, sys
import threading

import time as ti
from distutils.util import strtobool

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from InstSeq_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import cppyy
giapi_root=os.environ.get("GIAPI_ROOT")
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/StatusUtil.h")
cppyy.include("giapi/SequenceCommandHandler.h")
cppyy.include("giapi/CommandUtil.h")
cppyy.include("giapi/HandlerResponse.h")
cppyy.include("giapi/DataUtil.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")
cppyy.include("DataResponse.h")
cppyy.include("InstCmdHandler.h")
from cppyy.gbl import giapi
from cppyy.gbl import instDummy

class Inst_Seq(threading.Thread):
    
    def __init__(self):
        
        self.iam = "InstSeq"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")

        self._callback_giapi = self.callback_giapi
                    
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
                        
        self.simulation_mode = strtobool(self.cfg.get(MAIN, "simulation"))
        
        self.exptime = [0.0, 0.0]   # SVC, H_K
        self.FS_number = [0, 0]     # SVC, H_K
                        
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]    # for receive
        self.dcs_target = ["SVC", "H_K", "all"]     # for command
        self.dcs_ready = [False for _ in range(DCS_CNT)]

        instDummy.InstCmdHandler.create(self._callback_giapi)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.DATUM, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.OBSERVE, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        print(f'Subscribing APPLY {giapi.CommandUtil.subscribeApply("ig", giapi.command.ActivitySet.SET_PRESET,self._handler)}')
                                            
        
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
        

    def callback_giapi(self, action_id, seq_cmd, activity, config):
        t = ti.time()
        try:
            print(f'callGiapi python function {action_id} - {seq_cmd} {activity} ')
            print([f"{str(k)} : {config.getValue(k)}" for k in config.getKeys()])
            for k in config.getKeys():
                # TODO. It is necessary to do a regular expression instead of using split
                # It is necessary to know if the apply detector will consume more than 300 milisenconds 
                # in that case, it would be necessary to reponse with STARTED
                if (seq_cmd == giapi.command.seq_cmd.APPLY):
                    keys = k.split(':')
                    if keys[1] == 'dc':
                        dc = keys[2]
                        det= self._dtkProd if (dc == 'k') else self._dthProd
                        # The detector process will execute the order and will call the result using rabbitMq
                        self._actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':1}
                        det.sendMessage(self._routingDetPro, f"{action_id};{keys[3]};{config.getValue(k)}")   
                elif seq_cmd == giapi.command.SequenceCommand.OBSERVE:
                        self._actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':2}
                        self._dtkProd.sendMessage(self._routingDetPro, f"{action_id};observe;k_{config.getValue(k)}")
                        self._dthProd.sendMessage(self._routingDetPro, f"{action_id};observe;y_{config.getValue(k)}")
                        return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                else:
                        print('Not implemented yet')
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                t2 = ti.time() - t 
                while (t2 < 0.300):
                    ti.sleep(0.010)
                    if self._actRequested[action_id]['response']:
                        break
                        t2 = time.time() - t
                if t2 >= 0.300 or self._actRequested[action_id]['response'] == giapi.HandlerResponse.ERROR:
                    print(f'Error detected time: {t2} seconds')
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "") 

        except Exception as e:
            print (e)
            return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
        for k in self._actRequested:
            if self._actRequested[k] is None or self._actRequested[k]['response'] == giapi.HandlerResponse.ERROR:
                return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
        
        return instDummy.DataResponse(giapi.HandlerResponse.COMPLETED, "")
    
    #--------------------------------------------------------
    # Inst. Sequencer Publisher
    def connect_to_server_ex(self):
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
            
            
    def publish_to_queue(self, msg):
        if self.producer == None:
            return
        
        self.producer.send_message(self.InstSeq_q, msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        
    
    #--------------------------------------------------------
    # ObsApp queue
    def connect_to_server_ObsApp_q(self):
        self.consumer_ObsApp = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.ObsApp_ex)      
        self.consumer_ObsApp.connect_to_server()
        self.consumer_ObsApp.define_consumer(self.ObsApp_q, self.callback_ObsApp)       
        
        th = threading.Thread(target=self.consumer_ObsApp.start_consumer)
        th.start()
    
    
    def callback_ObsApp(self, ch, method, properties, body):
        cmd = body.decode()
    
        param = cmd.split()
        
        if param[0] == EXIT:
            self.__del__()  
            
        else:
            return
        
        msg = "<- [ObsApp] %s" % cmd
        self.log.send(self.iam, INFO, msg)        
        
                      
    #--------------------------------------------------------
    # dcs queue
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
        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[SVC] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[SVC])
            self.publish_to_queue(msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
        
        else:
            return
        
        msg = "<- [DCSS] %s" % cmd
        self.log.send(self.iam, INFO, msg)
                   
    
    def callback_h(self, ch, method, properties, body):
        cmd = body.decode()        
        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[H] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[H])
            self.publish_to_queue(msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
        
        else:
            return
        
        msg = "<- [DCSH] %s" % cmd
        self.log.send(self.iam, INFO, msg)

                    
                    
    def callback_k(self, ch, method, properties, body):
        cmd = body.decode()        
        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[1] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[K] = True
    
        elif param[0] == CMD_SETFSPARAM_ICS:    
            pass
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            msg = "%s %s" % (CMD_COMPLETED, self.dcs_list[K])
            self.publish_to_queue(msg)
            
        elif param[0] == CMD_STOPACQUISITION:
            pass
        
        else:
            return
        
        msg = "<- [DCSK] %s" % cmd
        self.log.send(self.iam, INFO, msg)
            

    #-------------------------------
    # dcs command
    
    # SVC, H_K, ALL
    def initialize2(self, target_idx):
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, self.dcs_target[target_idx], self.simulation_mode)
        self.publish_to_queue(msg)
        
        
    # SVC or H_K, Not ALL!!!!
    def set_exp(self, target_idx):                        
        _fowlerTime = self.exptime[target_idx] - T_frame * self.FS_number[target_idx]
        msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_target[target_idx], self.simulation_mode, self.exptime[target_idx], self.FS_number, _fowlerTime)
        self.publish_to_queue(msg)

        
    def start_acquisition(self, target_idx):     
        msg = "%s %s %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_target[target_idx], self.simulation_mode)
        self.publish_to_queue(msg)
        
                
        
    def save_fits_cube(self):
        pass



if __name__ == "__main__":
        
    proc = Inst_Seq()

    ti.sleep(10)
        
    proc.connect_to_server_ex()
        
    proc.connect_to_server_ObsApp_q()
    proc.connect_to_server_dcs_q()