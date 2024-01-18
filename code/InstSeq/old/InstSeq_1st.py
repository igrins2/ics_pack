# -*- coding: utf-8 -*-
"""
Created on Feb 15, 2023

Modified on Nov 27, 2023

@author: hilee
"""

import os, sys
import threading

import time as ti
import datetime
from distutils.util import strtobool


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from InstSeq_def import *

import svc_process
from add_wcs_header import update_header2

import astropy.io.fits as pyfits
import numpy as np

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import FITSHD_v3 as LFHD

import cppyy
giapi_root=os.environ.get("GIAPI_ROOT")
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/StatusUtil.h")
cppyy.include("giapi/SequenceCommandHandler.h")
cppyy.include("giapi/CommandUtil.h")
cppyy.include("giapi/HandlerResponse.h")
cppyy.include("giapi/DataUtil.h")
cppyy.include("giapi/GeminiUtil.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")
cppyy.include("DataResponse.h")
cppyy.include("InstCmdHandler.h")

from cppyy.gbl import giapi
from cppyy.gbl import instDummy

cppyy.cppdef("""
             struct TcsContext {
                double time;      //Gemini raw time
                double x,y,z;     //Cartesian elements of mount pre-flexure az/el
                //Telescope Parameters structure
                struct Tel {
                    double fl;    //Telescope focal length (mm)
                    double rma;   //Rotator mechanical angle (rads)
                    double an;    //Azimuth axis tilt NS (rads)
                    double aw;    //Azimuth axis tilt EW (rads)
                    double pnpae; //Az/El nonperpendicularity (rads)
                    double ca;    //Net left-right(horizontal) collimation (rads)
                    double ce;    //Net up-down(vertical) collimation (rads)
                    double pox;   //Pointing origin x-component (mm)
                    double poy;   //Pointing origin y-component (mm)
                } tel;
                double aoprms[15]; //Target independent apparent to observed parameters
                double m2xy[3][2]; //M2 tip/tilt (3 chop states)
                //Point Origin structure
                struct PO {
                    double mx; //Mount point origin in X
                    double my; //Mount point origin in Y
                    double ax; //Source chop A pointing origin in X
                    double ay; //Source chop A pointing origin in Y
                    double bx; //Source chop B pointing origin in X
                    double by; //Source chop B pointing origin in Y
                    double cx; //Source chop C pointing origin in X
                    double cy; //Source chop C pointing origin in Y
                } po;
                double ao2t[6]; //Optical distortion coefficients (Not used to date)
            };
            """)

class Inst_Seq(threading.Thread):
    
    def __init__(self):
        
        self.iam = "InstSeq"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")

        self.log.send(self.iam, INFO, giapi_root)
        
        self._callback_giapi = self.callback_giapi
        
        self._offsetCallBack = self.offsetCallBack
                    
        # ---------------------------------------------------------------   
        # load ini file
        self.ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(self.ini_file)
                
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.InstSeq_ex = cfg.get(MAIN, 'instseq_exchange')
        self.InstSeq_q = cfg.get(MAIN, 'instseq_routing_key')
        self.ObsApp_ex = cfg.get(MAIN, 'obsapp_exchange')     
        self.ObsApp_q = cfg.get(MAIN, 'obsapp_routing_key')
         
        self.producer = None
        self.producer_gmp = None
        self.consumer_ObsApp = None
        self.consumer_dcs = [None for _ in range(DCS_CNT)]
                        
        self.simulation_mode = strtobool(cfg.get(MAIN, "simulation"))
        
        self.reboot = strtobool(cfg.get(INST_SEQ, "reboot"))
        reboot_action_id = int(cfg.get(INST_SEQ, "reboot-action-id"))
        self.tcs_waitTime = int(cfg.get(INST_SEQ, "tcs-wait-time"))
        
        tmp = cfg.get(SC, "slit-cen").split(',')
        self.slit_cen = [int(tmp[0]), int(tmp[1])]
        self.pixel_scale = float(cfg.get(SC, "pixelscale"))
        self.slit_width = float(cfg.get(SC,'slit-wid'))
        self.slit_len = float(cfg.get(SC,'slit-len'))
        self.slit_ang = float(cfg.get(SC,'slit-ang'))
        
        self.out_of_number_svc = int(cfg.get(SC, 'out-of-number-svc'))
        self.cur_number_svc = 0
        self.svc_file_list = []    
        
        self.cur_ObsApp_taking = False    
                
        self.cur_expTime = 1.63
                        
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]    # for receive
        self.dcs_ready = [False for _ in range(DCS_CNT)]
        self.dcs_setparam = [False for _ in range(DCS_CNT)]
        self.acquiring = [False for _ in range(DCS_CNT)]
        self.rebooting = [False for _ in range(DCS_CNT)]

        self.actRequested = {}
        self.tcs_info = {}
        self.cur_action_id = 0
        self.apply_mode = ACQ_MODE
        self.data_label = ""
        self.filepath = ["", ""]
        
        self.frame_mode = ""    #A, B, ON, OFF
                                
        self.airmass = [0.0, 0.0]
        self.HA = [None, None]
        self.LST = [None, None]
        self.ZD = [0.0, 0.0]
        self.PA = [0.0, 0.0]
        
        #***************************************************
        self.FHD_TEL = dict()
        
        self.FHD_TEL["DATEOBS"] = "2023-06-12T16:21:45.037"
        self.FHD_TEL["DATEEND"] = "2023-06-12T16:21:49.215"
        self.FHD_TEL["UTOBS"] = 16.36251
        self.FHD_TEL["UTEND"] = 16.36367
        self.FHD_TEL["JDOBS"] = 2460108.181771
        self.FHD_TEL["JDEND"] = 2460108.18182
        self.FHD_TEL["MJDOBS"] = 60107.681771
        self.FHD_TEL["tel_para_angle"] = 0 
        self.FHD_TEL["tel_ra"] = '--:--:--.-'
        self.FHD_TEL["tel_dec"] = '--:--:--.-'

        TCS_INFO = {"tel_airmass":0,
                    "tel_hourangle":0,
                    "lst":0,
                    "tel_zd":0,
                    "tel_position_angle":90}

        self.FHD_TEL["start"] = TCS_INFO
        self.FHD_TEL["end"] = TCS_INFO
        #***************************************************
        
        _hdul = pyfits.open(WORKING_DIR + "ics_pack/code/InstSeq/slitmaskv0_igrins2.fits")
        _mask = _hdul[0].data
        slit_image_flip_func = lambda m: np.fliplr(np.rot90(m))
        self.mask_svc = slit_image_flip_func(_mask)   
        _hdul.close()   
        
        self._handler = instDummy.InstCmdHandler.create(self._callback_giapi)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.TEST, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.REBOOT, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.INIT, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        giapi.CommandUtil.subscribeApply("ig2", giapi.command.ActivitySet.SET_PRESET_START, self._handler)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.OBSERVE, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        giapi.CommandUtil.subscribeSequenceCommand(giapi.command.SequenceCommand.ABORT, giapi.command.ActivitySet.SET_PRESET_START,self._handler)
        
        #print(f'Subscribing APPLY {giapi.CommandUtil.subscribeApply("ig", giapi.command.ActivitySet.SET_PRESET, self._handler)}')
        
        if self.reboot:
                                            
            self.publish_to_queue(CMD_RESTART)
            
            for idx in range(DCS_CNT):
                self.rebooting[idx] = True
                                
            cfg = sc.LoadConfig(self.ini_file)
            cfg.set(MAIN, "reboot", "False")
            cfg.set(MAIN, "reboot-action-id", str(0))
                                        
            sc.SaveConfig(cfg, self.ini_file)         
            
            self.cur_action_id = reboot_action_id
            
            self.reboot = False    
        
        # for test    
        #self.req_from_TCS()                   
            
        
    def __del__(self):
        #msg = "Closing %s" % self.iam
        #self.log.send(self.iam, DEBUG, msg)
                    
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")

        if self.producer != None:
            self.producer.__del__()    
            self.producer = None
            
        if self.producer_gmp != None:
            self.producer_gmp.__del__()    
            self.producer_gmp = None

        self.consumer_ObsApp = None
        for i in range(DCS_CNT):
            self.consumer_dcs[i] = None

        self.log.send(self.iam, DEBUG, "Closed!") 
        #exit()
        

    # receiving from giapi ?
    # seq_cmd = ?:TEST / ?:REBOOT / 2:INIT / ?:APPLY / 10:OBSERVE / 16:ABORT
    # activity = 0:ACCEPTED, 1:STARTED, 2:COMPLETED, 3:ERROR
    # config = DATA_LABEL=~~.fits / ig2:dcs:expTime= / ig2:seq:state="acq" or "sci"
    def callback_giapi(self, action_id, seq_cmd, activity, config):
        t = ti.time()
        try:
            self.cur_action_id = action_id  # check!!! whether integer or not
            print(f'########## callGiapi python function {action_id} - {seq_cmd} {activity} ##########')
            print([f"{str(k)} : {config.getValue(k)}" for k in config.getKeys()])
            
            # TODO. It is necessary to do a regular expression instead of using split
            # It is necessary to know if the apply detector will consume more than 300 milisenconds 
            # in that case, it would be necessary to reponse with STARTED
            
            # ----------------------------------------------------
            # SequenceCommand.TEST
            if seq_cmd == giapi.command.SequenceCommand.TEST:                
                if activity == giapi.command.Activity.PRESET:
                    self.log.send(self.iam, INFO, "SequenceCommand.TEST, Activity.PRESET")
                    
                    if not self.dcs_ready[SVC] or not self.dcs_ready[H] or not self.dcs_ready[K]:
                        self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                    
                    for idx in range(DCS_CNT):
                        self.dcs_setparam[idx] = False
                    
                    self.apply_mode = TEST_MODE
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.ACCEPTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.ACCEPTED, "")
                
                elif activity == giapi.command.Activity.START:
                    self.log.send(self.iam, INFO, "SequenceCommand.TEST, Activity.START")
                    
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_TEST}            
                
                    self.set_exp("all")
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                elif activity == giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, INFO, "SequenceCommand.TEST, Activity.PRESET_START")
                    
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_TEST}   
                    
                    if not self.dcs_ready[SVC] or not self.dcs_ready[H] or not self.dcs_ready[K]:
                        self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                    
                    for idx in range(DCS_CNT):
                        self.dcs_setparam[idx] = False
                    
                    self.apply_mode = TEST_MODE
                
                    self.set_exp("all")
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                elif activity == giapi.command.Activity.CANCEL:
                    self.log.send(self.iam, INFO, "SequenceCommand.TEST, Activity.CANCEL")
                    self.actRequested[action_id] = {}
                    self.stop_acquistion()
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                else:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                    
            # ----------------------------------------------------
            # SequenceCommand.REBOOT    
            elif seq_cmd == giapi.command.SequenceCommand.REBOOT:
                if activity != giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                    
                self.log.send(self.iam, INFO, "SequenceCommand.REBOOT, Activity.PRESET_START")
                
                self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_REBOOT}
        
                # -----------------------------------
                # need to test with systemctl (InstSeq)
                cfg = sc.LoadConfig(self.ini_file)
                cfg.set(MAIN, "reboot", "True")
                cfg.set(MAIN, "reboot-action-id", str(action_id))
                                    
                sc.SaveConfig(cfg, self.ini_file)
                               
                self.power_onoff(False) 
                
                self.restart_icc()
                                
                self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                # -----------------------------------
            
            # ----------------------------------------------------
            # SequenceCommand.INIT    
            elif seq_cmd == giapi.command.SequenceCommand.INIT:
                if activity == giapi.command.Activity.PRESET:
                    self.log.send(self.iam, INFO, "SequenceCommand.INIT, Activity.PRESET")
                    
                    for idx in range(DCS_CNT):
                        self.dcs_ready[idx] = False
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.ACCEPTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.ACCEPTED, "")
                
                elif activity == giapi.command.Activity.START:
                    self.log.send(self.iam, INFO, "SequenceCommand.INIT, Activity.START")
                
                    for idx in range(DCS_CNT):
                        if self.dcs_ready[idx]:
                            self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                            return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                        
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_INIT}
                    
                    self.initialize2()
                
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                elif activity == giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, INFO, "SequenceCommand.INIT, Activity.PRESET_START")
                    
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_INIT}
                    
                    for idx in range(DCS_CNT):
                        self.dcs_ready[idx] = False
                        
                    self.initialize2()
                
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                else:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")                    
                                 
            # ----------------------------------------------------
            # SequenceCommand.APPLY                       
            elif seq_cmd == giapi.command.SequenceCommand.APPLY:
                _exptime_sci, _FS_number_sci = 0.0, 0
                if activity == giapi.command.Activity.PRESET:
                    self.log.send(self.iam, INFO, "SequenceCommand.APPLY, Activity.PRESET")
                    
                    offset_p, offset_q = "0", "0"
                    for k in config.getKeys():
                        keys = config.getValue(k)
                        # keys = ig2:dcs:expTime=1.63 / ig2:seq:state="acq" or "sci"
                        print('keys:', keys)
                        #print(f"SCI_MODE: {SCI_MODE} {k} == ig2:seq:state")
                        
                        if k == "ig2:dcs:expTime":
                            self.cur_expTime = float(keys.c_str())
                            print(f'after asigned {self.cur_expTime}')
                            
                            if self.cur_expTime < 1.63:     self.cur_expTime = 1.63
                        
                        elif k == "ig2:seq:state":  self.apply_mode = keys
                        elif k == "ig2:seq:p":      offset_p = keys.c_str()
                        elif k == "ig2:seq:q":      offset_q = keys.c_str()
                    
                    #send to ObsApp
                    print(offset_p, offset_q)
                    msg = "%s %s %s" % (INSTSEQ_PQ, offset_p, offset_q)
                    self.publish_to_queue(msg)
                    if int(offset_p) == 0 and int(offset_q) > 0:    self.frame_mode = "A"
                    elif int(offset_p) == 0 and int(offset_q) < 0:  self.frame_mode = "B"
                    elif int(offset_p) == 0 and int(offset_q) == 0: self.frame_mode = "ON"
                    elif int(offset_p) != 0 and int(offset_q) != 0: self.frame_mode = "OFF"
                    
                    if self.apply_mode == ACQ_MODE:
                        self.dcs_setparam[SVC] = False
                        
                    elif self.apply_mode == SCI_MODE:
                        self.dcs_setparam[SVC] = False
                        self.dcs_setparam[H] = False
                        self.dcs_setparam[K] = False
                        
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ACCEPTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.ACCEPTED, "")
                    
                elif activity == giapi.command.Activity.START:
                    self.log.send(self.iam, INFO, "SequenceCommand.APPLY, Activity.START")
                    
                    for idx in range(DCS_CNT):
                        if self.dcs_setparam[idx]:
                            self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                            return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                        
                    self.actRequested[action_id] = {'t': t, 'response': None, 'numAct': ACT_APPLY}
                    
                    if self.apply_mode == ACQ_MODE:
                        self.set_exp(self.dcs_list[SVC])
                                
                    elif self.apply_mode == SCI_MODE:
                        _exptime_sci = self.cur_expTime                        
                                
                        _max_fowler_number = int((_exptime_sci - T_minFowler) / T_frame)
                        _FS_number_sci = N_fowler_max
                        while _FS_number_sci > _max_fowler_number:
                            _FS_number_sci //= 2
                            
                        print(f'exptime_sci: {_exptime_sci} sending {_FS_number_sci}')
                        
                        if not self.cur_ObsApp_taking:  self.set_exp("all", _exptime_sci, _FS_number_sci)
                        else:                           self.set_exp("H_K", _exptime_sci, _FS_number_sci)
                            
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                elif activity == giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, INFO, "SequenceCommand.APPLY, Activity.PRESET_START")
                    
                    self.actRequested[action_id] = {'t': t, 'response': None, 'numAct': ACT_APPLY}
                    
                    offset_p, offset_q = "0", "0"
                    for k in config.getKeys():
                        keys = config.getValue(k)
                        # keys = ig2:dcs:expTime=1.63 / ig2:seq:state="acq" or "sci"
                        print('keys:', keys)
                        #print(f"SCI_MODE: {SCI_MODE} {k} == ig2:seq:state")
                        
                        if k == "ig2:dcs:expTime":
                            self.cur_expTime = float(keys.c_str())
                            if self.cur_expTime < 1.63:     self.cur_expTime = 1.63
                            print(f'after asigned {self.cur_expTime}')
                        
                        elif k == "ig2:seq:state":  self.apply_mode = keys
                        elif k == "ig2:seq:p":      offset_p = keys.c_str()
                        elif k == "ig2:seq:q":      offset_q = keys.c_str()
                    
                    #send to ObsApp
                    print(offset_p, offset_q)
                    msg = "%s %s %s" % (INSTSEQ_PQ, offset_p, offset_q)
                    self.publish_to_queue(msg)
                    ti.sleep(0.1)
                    if int(offset_p) == 0 and int(offset_q) > 0:    self.frame_mode = "A"
                    elif int(offset_p) == 0 and int(offset_q) < 0:  self.frame_mode = "B"
                    elif int(offset_p) == 0 and int(offset_q) == 0: self.frame_mode = "ON"
                    elif int(offset_p) != 0 and int(offset_q) != 0: self.frame_mode = "OFF"
                    
                    if self.apply_mode == ACQ_MODE:
                        self.dcs_setparam[SVC] = False
                        self.set_exp(self.dcs_list[SVC])
                        
                    elif self.apply_mode == SCI_MODE:
                        self.dcs_setparam[SVC] = False
                        self.dcs_setparam[H] = False
                        self.dcs_setparam[K] = False
                                                            
                        _exptime_sci = self.cur_expTime
                                
                        _max_fowler_number = int((_exptime_sci - T_minFowler) / T_frame)
                        _FS_number_sci = N_fowler_max
                        while _FS_number_sci > _max_fowler_number:
                            _FS_number_sci //= 2
                            
                        print(f'exptime_sci: {_exptime_sci} sending {_FS_number_sci}')
                        
                        if not self.cur_ObsApp_taking:  self.set_exp("all", _exptime_sci, _FS_number_sci)
                        else:                           self.set_exp("H_K", _exptime_sci, _FS_number_sci)
                            
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.STARTED")                                                
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                else:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")                    
            
            # ----------------------------------------------------
            # SequenceCommand.OBSERVE                                                        
            elif seq_cmd == giapi.command.SequenceCommand.OBSERVE:
                if activity == giapi.command.Activity.PRESET:
                    self.log.send(self.iam, INFO, "SequenceCommand.OBSERVE, Activity.PRESET")

                    for k in config.getKeys():                    
                        keys = config.getValue(k)
                        print('keys:', keys)
                        
                        if k == "DATA_LABEL":
                            self.data_label = keys.c_str()
                            
                        else:
                            _t = datetime.datetime.utcnow()
                            _tmp = "%04d%02d%02d_temp.fits" % (_t.year, _t.month, _t.day)

                            self.data_label = _tmp
                            
                    self.cur_number_svc = 1
                    self.filepath[H-1] = ""
                    self.filepath[K-1] = ""
                
                    self.svc_file_list = []
                    
                    if self.apply_mode == ACQ_MODE:
                        self.acquiring[SVC] = True
                        
                    elif self.apply_mode == SCI_MODE:               
                        self.acquiring[H] = True
                        self.acquiring[K] = True
                        if not self.cur_ObsApp_taking:  
                            self.acquiring[SVC] = True
                            
                    else:
                        self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "") 
                            
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ACCEPTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.ACCEPTED, "")
                
                elif activity == giapi.command.Activity.START:
                    self.log.send(self.iam, INFO, "SequenceCommand.OBSERVE, Activity.START")
                        
                    for idx in range(DCS_CNT):
                        if not self.acquiring[idx]:
                            self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                            return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                        
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_OBSERVE}
                    
                    self.send_to_GDS(giapi.data.ObservationEvent.OBS_PREP, self.data_label)
                    self.send_to_GDS(giapi.data.ObservationEvent.OBS_START_ACQ, self.data_label)
                    
                    if self.apply_mode == ACQ_MODE:
                        self.start_acquisition(self.dcs_list[SVC])
                        
                    elif self.apply_mode == SCI_MODE:                                                    
                        if not self.cur_ObsApp_taking:  self.start_acquisition()
                        else:                           self.start_acquisition("H_K")
                        
                    else:
                        self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")                       

                    # request TCS info
                    self.req_from_TCS()
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                elif activity == giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, INFO, "SequenceCommand.OBSERVE, Activity.START")
                    
                    self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_OBSERVE}
                    
                    for k in config.getKeys():                    
                        keys = config.getValue(k)
                        print('keys:', keys)
                        
                        if k == "DATA_LABEL":
                            self.data_label = keys.c_str()
                            
                        else:
                            _t = datetime.datetime.utcnow()
                            _tmp = "%04d%02d%02d_temp.fits" % (_t.year, _t.month, _t.day)

                            self.data_label = _tmp
                            
                    self.cur_number_svc = 1
                    self.filepath[H-1] = ""
                    self.filepath[K-1] = ""
                
                    self.svc_file_list = []
                    
                    self.send_to_GDS(giapi.data.ObservationEvent.OBS_PREP, self.data_label)
                    self.send_to_GDS(giapi.data.ObservationEvent.OBS_START_ACQ, self.data_label)
                    
                    if self.apply_mode == ACQ_MODE:
                        self.acquiring[SVC] = True
                        self.start_acquisition(self.dcs_list[SVC])
                        
                    elif self.apply_mode == SCI_MODE:                                                    
                        self.acquiring[H] = True
                        self.acquiring[K] = True
                        if not self.cur_ObsApp_taking:  
                            self.acquiring[SVC] = True
                            self.start_acquisition()
                        else:
                            self.start_acquisition("H_K")
                        
                    else:
                        self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                        return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")                       

                    # request TCS info
                    self.req_from_TCS()
                    
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
                else:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "") 
            
            # ----------------------------------------------------
            # SequenceCommand.ABORT        
            elif seq_cmd == giapi.command.SequenceCommand.ABORT:
                if activity != giapi.command.Activity.PRESET_START:
                    self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                    return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
                
                self.log.send(self.iam, INFO, "SequenceCommand.ABORT, Activity.PRESET_START")
                
                self.actRequested[action_id] = {'t' : t, 'response' : None, 'numAct':ACT_ABORT}

                if self.apply_mode == ACQ_MODE:
                    self.stop_acquistion(self.dcs_list[SVC])
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                        
                elif self.apply_mode == SCI_MODE:   
                    if not self.cur_ObsApp_taking:  self.stop_acquistion()
                    else:                           self.stop_acquistion("H_K")
                        
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.STARTED")
                    return instDummy.DataResponse(giapi.HandlerResponse.STARTED, "")
                
            '''
            #from getting the TCS info. PA!
            elif seq_cmd == giapi.command.SequenceCommand.TCS:  #temporarly
                PA = "90"
                msg = "%s %s" % (INSTSEQ_SHOW_TCS_INFO, PA)
                self.publish_to_queue(msg)
            else:
                print('Not implemented yet')
                return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
            '''
            
            t2 = ti.time() - t
            while (t2 < 0.300):
                ti.sleep(0.010)
                if self.actRequested[action_id]['response'] == giapi.HandlerResponse.COMPLETED:
                    #break
                    self.log.send(self.iam, INFO, "giapi.HandlerResponse.COMPLETED")
                    return instDummy.DataResponse(giapi.HandlerResponse.COMPLETED, "")
                #print(t2)
                t2 = ti.time() - t
                
            if self.actRequested[action_id]['response'] == giapi.HandlerResponse.ERROR:
                print(f'Error detected time: {t2} seconds')
                self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")

        except Exception as e:
            print (e)
            self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
            return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")
        
        for k in self.actRequested:
            if self.actRequested[k] is None or self.actRequested[k]['response'] == giapi.HandlerResponse.ERROR:
                self.log.send(self.iam, ERROR, "giapi.HandlerResponse.ERROR")
                return instDummy.DataResponse(giapi.HandlerResponse.ERROR, "")

    
    #--------------------------------------------------------
    # send to Gemini system
    def send_to_GDS(self, event, data_label):     
        msg = "send to GDS: %d" % event
        self.log.send(self.iam, INFO, msg)
        giapi.DataUtil.postObservationEvent(event, data_label)
                      
    
    #--------------------------------------------------------
    # Inst. Sequencer Publisher
    def connect_to_server_ex(self):
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
            
            
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
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

        #if not param[0] == OBSAPP_CAL_OFFSET:  return
        
        msg = "<- [ObsApp] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        print(msg)    
        
        if param[0] == OBSAPP_CAL_OFFSET:           self.send_to_TCS(float(param[1]), float(param[2]), int(param[3]))
        elif param[0] == OBSAPP_OUTOF_NUMBER_SVC:   self.out_of_number_svc = int(param[1])
        elif param[0] == OBSAPP_TAKING_IMG:         self.cur_ObsApp_taking = bool(int(param[1]))
                
    
    def offsetCallBack(self, offsetApplied, msg): 
        print(f'The offset was applied: {offsetApplied}')
        self.log.send(self.iam, INFO, "Msg from GMP: " + msg)         
    
       
    def send_to_TCS(self, p, q, mode):
        #res = giapi.GeminiUtil.tcsApplyOffset(p, q, giapi.OffsetType.ACQ, 0)
        #res = giapi.GeminiUtil.tcsApplyOffset(p, q, giapi.OffsetType.SLOWGUIDING, 0)
        
        try:
            if mode == giapi.OffsetType.ACQ:
                res = giapi.GeminiUtil.tcsApplyOffset(p, q, mode, self.tcs_waitTime)    # after wait time, no response, res = 0 : wait time -> config.ini
            else:
                res = giapi.GeminiUtil.tcsApplyOffset(p, q, mode, 10000, self._offsetCallBack)
            
            msg = "Finished! result is: %d" % res               
            self.log.send(self.iam, INFO, msg)
        
        except:
            self.log.send(self.iam, WARNING, "Time out!!!")
            
            
    def req_from_TCS(self):
        
        return

        tcsContext = cppyy.gbl.TcsContext()
        print(tcsContext)
        
        res = giapi.GeminiUtil.getTcsContext(tcsContext, self.tcs_waitTime)
        
        print(giapi.TcsContext.time)
        print(giapi.TcsContext.x)
        print(giapi.TcsContext.y)
        print(giapi.TcsContext.z)
        
        print(giapi.TcsContext.Tel.fl)
        print(giapi.TcsContext.Tel.rma)
        print(giapi.TcsContext.Tel.an)
        print(giapi.TcsContext.Tel.aw)
        print(giapi.TcsContext.Tel.pnpae)
        print(giapi.TcsContext.Tel.ca)
        print(giapi.TcsContext.Tel.ce)
        print(giapi.TcsContext.Tel.pox)
        print(giapi.TcsContext.Tel.poy)
        
        print(giapi.TcsContext.aoprms)
        print(giapi.TcsContext.m2xy)
        
        print(f'Finished! result is: {res}')
        
        '''
        #port, rma, PA, RA, Dec, AM, HA, LST, ZD                    
        for info in param:
            val = info.split('=')
            if info[0] == "ag:port:igrins2":
                self.tcs_info = {'port': val[1]}
            elif info[0] == "tcs:currentRMA":
                self.tcs_info = {'rma': val[1]}
            elif info[0] == "tcs:instrPA":
                self.tcs_info = {'PA': val[1]}
            elif info[0] == "tcs:sad:currentRA":
                self.tcs_info = {'RA': val[1]}
            elif info[0] == "tcs:sad:currentDec":
                self.tcs_info = {'Dec': val[1]}
            elif info[0] == "tcs:sad:airMassNow":
                self.tcs_info = {'AM': val[1]}
            elif info[0] == "tcs:sad:currentHAString":
                self.tcs_info = {'HA': val[1]}
            elif info[0] == "tcs:sad:LST":
                self.tcs_info = {'LST': val[1]}
            elif info[0] == "tcs:sad:currentZD":
                self.tcs_info = {'ZD': val[1]}
        '''
        '''
        struct TcsContext {
            double time;      //Gemini raw time
            double x,y,z;     //Cartesian elements of mount pre-flexure az/el
            //Telescope Parameters structure
            struct Tel {
                double fl;    //Telescope focal length (mm)
                double rma;   //Rotator mechanical angle (rads)
                double an;    //Azimuth axis tilt NS (rads)
                double aw;    //Azimuth axis tilt EW (rads)
                double pnpae; //Az/El nonperpendicularity (rads)
                double ca;    //Net left-right(horizontal) collimation (rads)
                double ce;    //Net up-down(vertical) collimation (rads)
                double pox;   //Pointing origin x-component (mm)
                double poy;   //Pointing origin y-component (mm)
            } tel;
            double aoprms[15]; //Target independent apparent to observed parameters
            double m2xy[3][2]; //M2 tip/tilt (3 chop states)
            //Point Origin structure
            struct PO {
                double mx; //Mount point origin in X
                double my; //Mount point origin in Y
                double ax; //Source chop A pointing origin in X
                double ay; //Source chop A pointing origin in Y
                double bx; //Source chop B pointing origin in X
                double by; //Source chop B pointing origin in Y
                double cx; //Source chop C pointing origin in X
                double cy; //Source chop C pointing origin in Y
            } po;
            double ao2t[6]; //Optical distortion coefficients (Not used to date)
        };
        '''
        
        return tcsContext
                      
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
            
        msg = "%s all %d" % (CMD_INIT2_DONE, self.simulation_mode)
        self.publish_to_queue(msg)
                        
                
            
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()        
        param = cmd.split()            

        msg = "<- [DCSS] %s" % cmd
        self.log.send(self.iam, INFO, msg)
 
        self.dcs_data_processing_SVC(param)
                                               
    
    def callback_h(self, ch, method, properties, body):
        cmd = body.decode()        
        param = cmd.split()

        msg = "<- [DCSH] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        self.dcs_data_processing_HK(param, H)
        
                    
    def callback_k(self, ch, method, properties, body):
        cmd = body.decode()        
        param = cmd.split()
                    
        msg = "<- [DCSK] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        self.dcs_data_processing_HK(param, K)
            
            
    def dcs_data_processing_SVC(self, param):
        if param[0] == CMD_INITIALIZE1:
            msg = "%s %s %d" % (CMD_INIT2_DONE, self.dcs_list[SVC], self.simulation_mode)
            self.publish_to_queue(msg)    
            
        elif param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
            if self.cur_action_id == 0: return
                        
            self.dcs_ready[SVC] = True
            
            if self.rebooting[SVC]:
                if self.rebooting[H] and self.rebooting[K]:
                    self.restart_done()
            else:
                if self.dcs_ready[SVC] and self.dcs_ready[H] and self.dcs_ready[K]:
                    self.response_complete(bool(int(param[1])))
    
        elif param[0] == CMD_SETFSPARAM_ICS:   
            if self.apply_mode == None or self.cur_action_id == 0:  return
            if self.cur_ObsApp_taking:                              return
            
            print('SVC(CMD_SETFSPARAM_ICS)', self.apply_mode) 
            
            self.dcs_setparam[SVC] = True  
            #self.actRequested[self.cur_action_id]['response'] = giapi.HandlerResponse.ACCEPTED
            
            res = bool(int(param[1]))
            if self.apply_mode == TEST_MODE:
                if res:
                    if self.dcs_setparam[SVC] and self.dcs_setparam[H] and self.dcs_setparam[K]:
                        for idx in range(DCS_CNT):
                            self.acquiring[idx] = True
                        self.start_acquisition()
                else:
                    self.response_complete(False)
                    
            elif self.apply_mode == ACQ_MODE:
                self.response_complete(res)

                # request TCS info     
                #self.req_from_TCS()
                
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            #if not self.acquiring[SVC]:
            #    return    
            
            if self.apply_mode == None or self.cur_action_id == 0: return
            
            print('SVC(CMD_ACQUIRERAMP_ICS)', self.apply_mode)
            
            # request TCS info
            #self.req_from_TCS()
            
            res = bool(int(param[3]))
            
            if self.apply_mode == TEST_MODE:
                self.acquiring[SVC] = False
                if not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]: 
                    self.apply_mode = None
                    self.response_complete(res)
                       
            elif self.apply_mode == ACQ_MODE:
                if not self.acquiring[SVC]:     return
                
                self.acquiring[SVC] = False
                self.apply_mode = None
                if res:
                    self.svc_file_list.append(param[2])
                    self.save_fits_MEF(self.dcs_list[SVC])
                else:
                    self.response_complete(False)
                
            elif self.apply_mode == SCI_MODE:
                
                self.acquiring[SVC] = False
                #print("self.cur_number_svc", self.cur_number_svc)
                if self.cur_number_svc == 1:                        self.svc_file_list.append(param[2])
                if self.cur_number_svc == self.out_of_number_svc:   self.cur_number_svc = 0
                
                self.cur_number_svc += 1
                if not self.cur_ObsApp_taking:
                    self.acquiring[SVC] = True
                    self.start_acquisition(self.dcs_list[SVC])
            
        elif param[0] == CMD_STOPACQUISITION:
            if self.apply_mode == None or self.cur_action_id == 0: return
            
            print('SVC(CMD_STOPACQUISITION)', self.apply_mode)
            
            self.acquiring[SVC] = False
                
            if not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:
                if self.apply_mode != None:
                    self.apply_mode = None
                    self.response_complete(True)
                    
                    
    def dcs_data_processing_HK(self, param, idx):
        if param[0] == CMD_INITIALIZE1:
            msg = "%s %s %d" % (CMD_INIT2_DONE, self.dcs_list[idx], self.simulation_mode)
            self.publish_to_queue(msg)    
            
        elif param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
            if self.cur_action_id == 0: return
            
            self.dcs_ready[idx] = True
            
            if self.rebooting[H]:
                if self.rebooting[SVC] and self.rebooting[K]:
                    self.restart_done()
            else:
                if self.dcs_ready[SVC] and self.dcs_ready[H] and self.dcs_ready[K]:
                    self.response_complete(bool(int(param[1])))
    
        elif param[0] == CMD_SETFSPARAM_ICS:   
            if self.apply_mode == None or self.cur_action_id == 0: return
            
            print(idx, '(CMD_SETFSPARAM_ICS)', self.apply_mode)
            
            self.dcs_setparam[idx] = True  
            #self.actRequested[self.cur_action_id]['response'] = giapi.HandlerResponse.ACCEPTED
            
            if self.apply_mode == TEST_MODE:
                if self.dcs_setparam[SVC] and self.dcs_setparam[H] and self.dcs_setparam[K]:
                    for idx in range(DCS_CNT):
                        self.acquiring[idx] = True
                    self.start_acquisition()
                    
            else:
                if self.dcs_setparam[H] and self.dcs_setparam[K]:
                    self.response_complete(bool(int(param[1])))
        
        elif param[0] == CMD_ACQUIRERAMP_ICS:
            if not self.acquiring[idx]:     return   
            if self.apply_mode == None or self.cur_action_id == 0: return
            
            print(idx, '(CMD_ACQUIRERAMP_ICS)', self.apply_mode)
            
            res = bool(int(param[3]))
            
            self.acquiring[idx] = False
            if self.apply_mode == TEST_MODE:
                if not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]: 
                    self.apply_mode = None
                    self.response_complete(res)
                
            if self.apply_mode == SCI_MODE:
                self.filepath[idx-1] = param[2]
                if not self.acquiring[H] and not self.acquiring[K]:
                    self.apply_mode = None
                    if res: self.save_fits_MEF()
                    else:   self.response_complete(False)
            
        elif param[0] == CMD_STOPACQUISITION:
            if self.apply_mode == None or self.cur_action_id == 0: return
            
            print(idx, '(CMD_STOPACQUISITION)', self.apply_mode)    
            
            self.acquiring[idx] = False
                
            if not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:
                if self.apply_mode != None:
                    self.apply_mode = None
                    self.response_complete(True)


    def response_complete(self, status=False):
        if self.cur_action_id == 0:     return 
        
        if status:  self.actRequested[self.cur_action_id]['response'] = giapi.HandlerResponse.COMPLETED
        else:       self.actRequested[self.cur_action_id]['response'] = giapi.HandlerResponse.ERROR
        
        _t = ti.time() - self.actRequested[self.cur_action_id]['t'] 

        '''
        if _t < 0.300:
            print("instDummy.DataResponse.COMPLETED")                    
        el
        '''
        print (f"time: {_t} response: {self.actRequested[self.cur_action_id]['response']}")
        #if _t >= 0.300:
        #    print("postCompetionInfo")
        giapi.CommandUtil.postCompletionInfo(self.cur_action_id, giapi.HandlerResponse.create(self.actRequested[self.cur_action_id]['response']))      
                    
        #if _t >= 0.300:
        #    print("postCompetionInfo")
        #    giapi.CommandUtil.postCompletionInfo(self.cur_action_id, giapi.HandlerResponse.create(self.actRequested[self.cur_action_id]['response']))      
                     
        self.cur_action_id = 0


    def restart_icc(self):
        os.system("shutdown -r -f")
        self.log.send(self.iam, INFO, "rebooting...")
        #self.__del__()
        
        
    def restart_done(self):
        self.log.send(self.iam, INFO, "postCompetionInfo")
        giapi.CommandUtil.postCompletionInfo(self.cur_action_id, giapi.HandlerResponse.create(self.actRequested[self.cur_action_id]['numAct']))   
        
        for idx in range(DCS_CNT):
            self.rebooting[idx] = False
            
            
    def power_onoff(self, onoff):
        if onoff:   pwr_list = "on on off off off off off off"
        else:       pwr_list = "off off off off off off off off"
        msg = "%s %s" % (HK_REQ_PWR_ONOFF, pwr_list)
        self.publish_to_queue(msg)

        
    #-------------------------------
    # dcs command
    
    # SVC, H_K, ALL
    def initialize2(self):
        msg = "%s all %d" % (CMD_INITIALIZE2_ICS, self.simulation_mode)
        self.publish_to_queue(msg)
        
        
    # acq:SVC, sci:H_K, test:ALL
    def set_exp(self, target, expTime=1.63, FS_number=1):  
        if target == self.dcs_list[SVC]:
            msg = "%s %s %d" % (CMD_SETFSPARAM_ICS, target, self.simulation_mode)
        else:                   
            _fowlerTime = expTime - T_frame * FS_number
            msg = "%s %s %d %.3f %d %.3f" % (CMD_SETFSPARAM_ICS, target, self.simulation_mode, expTime, FS_number, _fowlerTime)
        
        self.publish_to_queue(msg)

        
    def start_acquisition(self, target="all"): 
        next_idx = self.get_next_idx(target)
        #print(next_idx)
        msg = "%s %s %d %d %s" % (CMD_ACQUIRERAMP_ICS, target, self.simulation_mode, next_idx, self.data_label)
        self.publish_to_queue(msg)
        
        
    def input_TCS_info_header(self):
        ValHD=[]
        for ARR in LFHD.FHDARR:
            try:
                v = LFHD.ValHDLF(ARR[1], ARR[2], self.FHD_TEL)
            except (KeyError, AttributeError):
                v = pyfits.card.UNDEFINED
            except ValueError as e:
                msg = "Error in formatting : {} {} {}".format(*ARR)
                v = pyfits.card.UNDEFINED
                # raise e
            else:
                if isinstance(v, float) and np.isnan(v):
                    v = pyfits.card.UNDEFINED
            ValHD.append((ARR[0], v, ARR[3]))
            
        return ValHD
            
            
    def create_cube(self):
        self.log.send(self.iam, INFO, self.svc_file_list)
        if len(self.svc_file_list) == 0:    return [], [], [], []

        svc_list, cutout_list = [], []
        svc_list_header, cutout_list_header = [], []
        
        for idx, svc_name in enumerate(self.svc_file_list):
            # read data and header
            msg = "create_cube %d %s" % (idx, svc_name)
            self.log.send(self.iam, DEBUG, msg)
            filepath = "%sIGRINS/dcss/Fowler/%s" % (WORKING_DIR, svc_name)
            _hdul = pyfits.open(filepath)
            _img = _hdul[0].data
            _header = _hdul[0].header

            _hdul.close()
            msg = "closed %s" % svc_name
            self.log.send(self.iam, DEBUG, msg)
            
            #-----------------------------------------------------------
            # input TCS info to header list
            #ValHD = self.input_TCS_info_header()
            #InsHdInd = 7    # need to check
            #for i, hdrTup in enumerate(ValHD):
            #    _header.insert(InsHdInd+i,hdrTup)
            #-----------------------------------------------------------

            # make cube
            cx, cy = int(self.slit_cen[0]), int(self.slit_cen[1])
            #pixelscale = self.pixel_scale / 3600.
            
            svc_proc = svc_process.SlitviewProc(self.mask_svc)

            _header.set("SVC-IDX", idx+1, "Number of SVC data")

            slices = slice(cx-128, cx+128), slice(cx-128, cy+128)
            hdu_list = svc_proc.get_hdulist(_header, _img, slices)

            #update_header2(hdu_list[1].header, cx, cy, pixelscale)
            #update_header2(hdu_list[2].header, 128, 128, pixelscale)

            svc_list.append(hdu_list[1].data)
            cutout_list.append(hdu_list[2].data)
            
            svc_list_header.append(hdu_list[1].header)
            cutout_list_header.append(hdu_list[2].header)
                
        self.svc_file_list = []
        
        return svc_list, cutout_list, svc_list_header, cutout_list_header
        
                
    def save_fits_MEF(self, target="all"):
        if target == self.dcs_list[SVC]:
            if self.acquiring[SVC]:     return
        else:
            if self.acquiring[H] or self.acquiring[K]:  return
            
        # request TCS info
        self.req_from_TCS()
        
        self.send_to_GDS(giapi.data.ObservationEvent.OBS_END_ACQ, self.data_label)
        self.send_to_GDS(giapi.data.ObservationEvent.OBS_START_DSET_WRITE, self.data_label)
        
        #----------------------------------------------------------------------------------------
        # time measurement
        start_t = ti.time()
        
        # bring cube
        svc_list, cutout_list, svc_list_header, cutout_list_header = self.create_cube()
    
        # make Primary
        hdu_list = []
        Primary_hdu = pyfits.PrimaryHDU()
        
        #-----------------------------------------------------------
        Primary_hdu.header.set("INSTRUME", "IGRINS-2", "Instrument used to acquire data")
        Primary_hdu.header.set("OBJTYPE", "TAR", "Type of exposure (FLAT/SKY/TAR)")  
        Primary_hdu.header.set("FRMTYPE", self.frame_mode, "Type of Frames (A/B/ON/OFF)")
        
        ValHD = self.input_TCS_info_header()
        InsHdInd = 7    # need to check
        for i, hdrTup in enumerate(ValHD):
            Primary_hdu.header.insert(InsHdInd+i,hdrTup)
        #-----------------------------------------------------------
            
        hdu_list.append(Primary_hdu)
        
        # create MEF
        if target == self.dcs_list[SVC]:
            # blank H, K, 1 SVC
            for idx in range(2):
                _new_hdul = pyfits.ImageHDU()
                hdu_list.append(_new_hdul)
        
        else:
            while True:
                try:
                    # H, K
                    filepath_h = "%sIGRINS/dcsh/Fowler/%s" % (WORKING_DIR, self.filepath[H-1])
                    filepath_k = "%sIGRINS/dcsk/Fowler/%s" % (WORKING_DIR, self.filepath[K-1])
                    img_path_list = [filepath_h, filepath_k]
                    for idx in range(2):
                        _hdul = pyfits.open(img_path_list[idx])
                        _data = _hdul[0].data
                        
                        #-----------------------------------------------------------
                        _header = _hdul[0].header
                        if idx == 0:    gain=2.5
                        else:           gain=1.8
                        _header.set("GAIN", gain, "[electrons/ADU], Conversion Gain")                
                        #-----------------------------------------------------------
                        
                        _hdul.close()

                        imgdata = np.rot90(_data, (idx*2)+1)
                        if idx == 0:    imgdata = np.fliplr(imgdata)

                        _new_hdul = pyfits.ImageHDU(imgdata, _header)
                        hdu_list.append(_new_hdul)
                        
                    break
                    
                except:
                    print("file open error!!!")
                    ti.sleep(1)
                
        # compressed SVC cube
        img_array = np.array(svc_list)
        
        #-----------------------------------------------------------------------
        if svc_list_header != []:
            svc_list_header[0].set("GAIN", 2.00, "[electrons/ADU], Conversion Gain")
            svc_list_header[0].set("RDNOISE", 9.00, "Read Noise of Fowler Sampled Image with NSAMP")
            svc_list_header[0].set("SLIT_CX", self.slit_cen[0], "Center position of slit in the SVC image")
            svc_list_header[0].set("SLIT_CY", self.slit_cen[1], "Center position of slit in the SVC image")
            svc_list_header[0].set("SLIT_WID", self.slit_width, "(px) Width of slit")
            svc_list_header[0].set("SLIT_LEN", self.slit_len, "(px) Length of slit")
            svc_list_header[0].set("SLIT_ANG", self.slit_ang, "(d) Position angle of slit in the image")
        #-----------------------------------------------------------------------
        
        if svc_list_header == []:   _new_hdul = pyfits.ImageHDU()
        else:                       _new_hdul = pyfits.CompImageHDU(data=img_array, header=svc_list_header[0], compression_type="HCOMPRESS_1", hcomp_scale=2.5)
        hdu_list.append(_new_hdul)

        # cutout SVC cube
        if cutout_list_header == []:
            _new_hdul = pyfits.ImageHDU()
        else:
            img_array = np.array(cutout_list)
            #_new_hdul = pyfits.ImageHDU(data=img_array, header=cutout_list_header[0])
            _new_hdul = pyfits.ImageHDU(data=img_array)
        hdu_list.append(_new_hdul)
        
        # table
        cols = []
        for idx in range(len(svc_list)):
            if svc_list_header != []:
                #table = pyfits.Column(name=str(idx+1), format='20000A', array=[str(svc_list_header[idx])], ascii=False)
                table = pyfits.Column(name=str(idx+1), format='20000A', array=[str(cutout_list_header[idx])], ascii=False)
                cols.append(table) 
        hdu_table = pyfits.BinTableHDU.from_columns(cols)
        hdu_list.append(hdu_table)
        
        _t = datetime.datetime.utcnow()
        path = "%sIGRINS/Data/%04d%02d%02d" % (WORKING_DIR, _t.year, _t.month, _t.day)
        self.log.createFolder(path)
        MEF_file = "%s/%s" % (path, self.data_label)
        
        new_hdul = pyfits.HDUList(hdu_list)
        new_hdul.writeto(MEF_file, overwrite=True) 

        end_t = ti.time() - start_t
        print(end_t) 

        #----------------------------------------------------------------------------------------
            
        self.send_to_GDS(giapi.data.ObservationEvent.OBS_END_DSET_WRITE, self.data_label)
        
        self.data_label = ""
        self.filepath[H-1] = ""
        self.filepath[K-1] = ""
        self.frame_mode = ""
        self.response_complete(True)


    def stop_acquistion(self, target="all"):     
        msg = "%s %s %d" % (CMD_STOPACQUISITION, target, self.simulation_mode)
        self.publish_to_queue(msg)
           
        
    def get_next_idx(self, target):
        
        _t = datetime.datetime.utcnow()
        cur_date = "%04d%02d%02d" % (_t.year, _t.month, _t.day)
        
        dir_names = []
        try:
            if target == self.dcs_list[SVC]:
                filepath_s = "%sIGRINS/%s/Fowler/%s/" % (WORKING_DIR, self.dcs_list[SVC].lower(), cur_date)
                for names in os.listdir(filepath_s):
                    if names.find(".fits") < 0:
                        dir_names.append(names)
            
            else:
                filepath_h = "%sIGRINS/%s/Fowler/%s/" % (WORKING_DIR, self.dcs_list[H].lower(), cur_date)
                for names in os.listdir(filepath_h):
                    if names.find(".fits") < 0:
                        dir_names.append(names)

                filepath_k = "%sIGRINS/%s/Fowler/%s/" % (WORKING_DIR, self.dcs_list[K].lower(), cur_date)   
                for names in os.listdir(filepath_k):
                    if names.find(".fits") < 0:
                        dir_names.append(names)

            numbers = list(map(int, dir_names))

            if len(numbers) > 0:    next_idx = max(numbers) + 1
            else:                   next_idx = 1

        except:
            next_idx = 1        
            
        return next_idx
        

if __name__ == "__main__":
        
    proc = Inst_Seq()
        
    proc.connect_to_server_ex()
        
    proc.connect_to_server_ObsApp_q()
    proc.connect_to_server_dcs_q()
    
    proc.power_onoff(True)
