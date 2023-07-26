# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on July 26, 2023

@author: hilee
"""

from pickletools import read_unicodestring1
import sys, os
from matplotlib.figure import Figure

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from ui_DTP import *
from DT_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import subprocess

import time as ti
import datetime
import threading

import numpy as np
import astropy.io.fits as fits 
import Libs.zscale as zs

import glob

from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        #self.setFixedSize(1314, 703)
        
        self.iam = DT
        
        self.log = LOG(WORKING_DIR + "IGRINS", "DTP")  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        
        self.setFixedSize(1030, 741)
        self.setGeometry(0, 0, 1030, 741)
        self.setWindowTitle("Data Taking Package 2.0")        
        
        # canvas
        #self.image_fig = []
        self.image_ax = [None for _ in range(DCS_CNT)]
        self.image_canvas = [None for _ in range(DCS_CNT)]
        for i in range(DCS_CNT):
            _image_fig = Figure(figsize=(4, 4), dpi=100)
            self.image_ax[i] = _image_fig.add_subplot(111)
            _image_fig.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99) 
            self.image_canvas[i] = FigureCanvas(_image_fig)
        
        vbox_svc = QVBoxLayout(self.frame_svc)
        vbox_svc.addWidget(self.image_canvas[SVC])
        vbox_H = QVBoxLayout(self.frame_H)
        vbox_H.addWidget(self.image_canvas[H])
        vbox_K = QVBoxLayout(self.frame_K)
        vbox_K.addWidget(self.image_canvas[K])

        for i in range(DCS_CNT):
            self.clean_ax(self.image_ax[i])
                
        # load ini file
        self.cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.dt_ex = self.cfg.get(MAIN, 'dt_exchange')     
        self.dt_q = self.cfg.get(MAIN, 'dt_routing_key')
        
        self.EngTools_ex = self.cfg.get(MAIN, 'engtools_exchange')
        self.EngTools_q = self.cfg.get(MAIN, 'engtools_routing_key')

        motor_utpos = self.cfg.get(HK, "ut-pos").split(",")                        
        motor_ltpos = self.cfg.get(HK, "lt-pos").split(",")

        self.com_list = ["pdu", "lt", "ut"]
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]
        
        self.sel_mode = MODE_HK
        
        self.init_events()
        
        self.bt_take_image.setText("Take Image")
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, False)
        self.enable_dcs(K, False)
        
        self.label_zscale_range.setText("---")
        self.e_mscale_min.setText("1000")
        self.e_mscale_max.setText("5000")
        
        for i in range(DCS_CNT):
            self.e_exptime[i].setText("1.63")
            self.e_FS_number[i].setText("1")
            self.e_repeat[i].setText("1")

            self.label_prog_sts[i].setText("Idle")
            self.label_prog_time[i].setText("---")
            self.label_prog_elapsed[i].setText("0.0 sec")
                    
        for i in range(DCS_CNT):
            self.label_cur_num[i].setText("0 / 0")
                    
        for i in range(CAL_CNT):
            self.cal_e_exptime[i].setText("1.63")
            self.cal_e_repeat[i].setText("1")
        
        self.label_utpos.setText("---")
        self.label_ltpos.setText("---")
        
        self.sts_ut_pos[0].setText(motor_utpos[0])
        self.sts_ut_pos[1].setText(motor_utpos[1])
        
        self.sts_lt_pos[0].setText(motor_ltpos[0])
        self.sts_lt_pos[1].setText(motor_ltpos[1])
        self.sts_lt_pos[2].setText(motor_ltpos[2])
        self.sts_lt_pos[3].setText(motor_ltpos[3])
        self.sts_lt_pos[4].setText(motor_ltpos[4])
        
        self.e_movinginterval.setText("1")        
        
        self.simulation = False     #from EngTools
        
        self.mode = SINGLE_MODE
        self.continuous = [False for _ in range(DCS_CNT)]
        
        self.cal_mode = False

        self.dcs_ready = [False for _ in range(DCS_CNT)]
        self.acquiring = [False for _ in range(DCS_CNT)]
        self.all_acquired = False
                
        self.producer = None
        self.consumer_EngTools = None
        self.consumer_sub = [None for _ in range(COM_CNT)]
        self.consumer_dcs = [None for _ in range(DCS_CNT)]
        
        self.img = [None for _ in range(DCS_CNT)]
        
        self.output_channel = 32
        
        self.cur_cnt = [0 for _ in range(DCS_CNT)]
        self.measure_T = [0 for _ in range(DCS_CNT)]
        self.header = [None for _ in range(DCS_CNT)]
        
        self.radio_HK_sync.setChecked(True)
        self.set_HK_sync()
        
        #self.stop_clicked = False
        self.cal_stop_clicked = False
        
        self.motor_initialized = [False, False]     #ut, lt

        self.cal_cur = 0
        self.ut_moved = False
        self.lt_moved = False
        self.lamp_on = False
        
        self.power_status = [OFF for _ in range(PDU_IDX)] # motor, FLAT, THAR
           
        self.bt_run.setEnabled(False)
        for i in range(CAL_CNT):
            self.cal_set_enabled(i)         
        
        # progress bar     
        self.prog_timer = [None for _ in range(DCS_CNT)]
        self.cur_prog_step = [0 for _ in range(DCS_CNT)]
        for dc_idx in range(DCS_CNT):
            self.progressBar[dc_idx].setValue(0)
        
        # elapsed
        self.elapsed_timer = [None for _ in range(DCS_CNT)]
        self.elapsed = [0.0 for _ in range(DCS_CNT)]
        
        self.proc_sub = [None for _ in range(COM_CNT)]
        
        self.alarm_status = ALM_OK
        
        # connect to server
        self.connect_to_server_ex()
        
        self.connect_to_server_EngTools_q()
        self.connect_to_server_sub_q()  #motors, pdu
        self.connect_to_server_dcs_q() 
                    
        msg = "%s %s" % (DT_STATUS, self.alarm_status)
        self.publish_to_queue(msg)
                    
        
    def closeEvent(self, event: QCloseEvent) -> None:                    
        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")
            
        self.power_status[MOTOR-1] = OFF
        self.power_status[FLAT-1] = OFF
        self.power_status[THAR-1] = OFF
        self.power_onoff()
        
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                self.proc_sub[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc_sub[i].pid) + " exit")
                        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
                                                    
        self.publish_to_queue(EXIT)

        if self.producer != None:
            self.producer.__del__()
            self.producer = None
        
        for idx in range(COM_CNT):
            self.consumer_sub[idx] = None
        for idx in range(DCS_CNT):
            self.consumer_dcs[idx] = None

        self.log.send(self.iam, DEBUG, "Closed!") 
                
        return super().closeEvent(event)          

        
        
    def init_events(self):
                
        self.radio_zscale.clicked.connect(self.auto_scale)
        self.radio_mscale.clicked.connect(self.manual_scale)
        self.bt_scale_apply.clicked.connect(self.scale_apply)
        
        self.radio_HK_sync.clicked.connect(self.set_HK_sync)
        self.radio_whole_sync.clicked.connect(self.set_whole_sync)
        self.radio_SVC.clicked.connect(self.set_svc)
        self.radio_H.clicked.connect(self.set_H)
        self.radio_K.clicked.connect(self.set_K)
        
        self.radio_zscale.setChecked(True)
        self.radio_mscale.setChecked(False)
        self.bt_scale_apply.setEnabled(False)
        
        self.bt_take_image.clicked.connect(self.btn_click)   
        
        self.radio_exptime = [self.radio_exptime_svc, self.radio_exptime_H, self.radio_exptime_K]
        self.radio_N_fowler = [self.radio_number_fowler_svc, self.radio_number_fowler_H, self.radio_number_fowler_K]
                
        self.e_exptime = [self.e_exptime_svc, self.e_exptimeH, self.e_exptimeK]
        self.e_FS_number = [self.e_FS_number_svc, self.e_FSnumberH, self.e_FSnumberK]
        self.e_repeat = [self.e_repeat_number_svc, self.e_repeatH, self.e_repeatK]
                
        self.label_prog_sts = [self.label_prog_stats_svc, self.label_prog_sts_H, self.label_prog_sts_K]
        self.label_prog_time = [self.label_prog_time_svc, self.label_prog_time_H, self.label_prog_time_K]
        self.label_prog_elapsed = [self.label_prog_elapsed_svc, self.label_prog_elapsed_H, self.label_prog_elapsed_K]
        self.label_cur_num = [self.label_cur_num_svc, self.label_cur_num_H, self.label_cur_num_K]
        self.progressBar = [self.progressBar_svc, self.progressBar_H, self.progressBar_K]
        
        self.label_ongoing_filename = [self.label_ongoing_filename_svc, self.label_ongoing_filename_H, self.label_ongoing_filename_K]

        self.bt_init = [self.bt_init_SVC, self.bt_init_H, self.bt_init_K]
        self.chk_ds9 = [self.chk_ds9_svc, self.chk_ds9_H, self.chk_ds9_K]
                    
        self.e_path = [self.e_path_svc, self.e_path_H, self.e_path_K]
        self.e_savefilename = [self.e_savefilename_svc, self.e_savefilename_H, self.e_savefilename_K]
        
        for i in range(DCS_CNT):
            self.radio_exptime[i].setChecked(True)
            
            self.e_exptime[i].setEnabled(False)
            self.e_FS_number[i].setEnabled(False)
            self.e_repeat[i].setEnabled(False)
            
            self.chk_ds9[i].setEnabled(False)            
            self.bt_init[i].setEnabled(False)

            
        self.radio_exptime[SVC].clicked.connect(lambda: self.judge_exp_time(SVC)) 
        self.radio_N_fowler[SVC].clicked.connect(lambda: self.judge_FS_number(SVC))
        self.e_exptime[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_FS_number[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_repeat[SVC].editingFinished.connect(lambda: self.change_name(SVC))
        
        self.e_exptime[SVC].textChanged.connect(self.sync_apply_HK())
        self.e_FS_number[SVC].textChanged.connect(self.sync_apply_HK())
        self.e_repeat[SVC].textChanged.connect(self.sync_apply_HK())
        
        self.radio_exptime[H].clicked.connect(lambda: self.judge_exp_time(H)) 
        self.radio_N_fowler[H].clicked.connect(lambda: self.judge_FS_number(H))
        self.e_exptime[H].editingFinished.connect(lambda: self.judge_param(H))
        self.e_FS_number[H].editingFinished.connect(lambda: self.judge_param(H)) 
        self.e_repeat[H].editingFinished.connect(lambda: self.change_name(H))
        
        self.e_exptime[H].textChanged.connect(self.sync_apply_K())
        self.e_FS_number[H].textChanged.connect(self.sync_apply_K())
        self.e_repeat[H].textChanged.connect(self.sync_apply_K())
        
        self.radio_exptime[K].clicked.connect(lambda: self.judge_exp_time(K)) 
        self.radio_N_fowler[K].clicked.connect(lambda: self.judge_FS_number(K))
        self.e_exptime[K].editingFinished.connect(lambda: self.judge_param(K))
        self.e_FS_number[K].editingFinished.connect(lambda: self.judge_param(K)) 
        self.e_repeat[K].editingFinished.connect(lambda: self.change_name(K)) 
        
        self.bt_init[SVC].clicked.connect(lambda: self.initialize2(SVC))            
        self.bt_init[H].clicked.connect(lambda: self.initialize2(H))            
        self.bt_init[K].clicked.connect(lambda: self.initialize2(K))                
            
        #------------------
        #calibration

        self.chk_open_calibration.setEnabled(False)
        
        self.chk_open_calibration.clicked.connect(self.open_calilbration)
        
        self.cal_chk = [self.chk_dark, self.chk_flat_on, self.chk_flat_off, self.chk_ThAr_on, self.chk_ThAr_off, self.chk_pinhole_flat, self.chk_pinhole_ThAr, self.chk_pinhole_offslit, self.chk_USAF_on, self.chk_USAF_off]
        
        self.cal_e_exptime = [self.e_dark_exptime, self.e_flaton_exptime, self.e_flatoff_exptime, self.e_ThAr_exptime_on, self.e_ThAr_exptime_off, self.e_pinholeflat_exptime, self.e_pinholeThAr_exptime, self.e_pinholeoffslit_exptime, self.e_USAFon_exptime, self.e_USAFoff_exptime]
        
        self.cal_e_repeat = [self.e_dark_repeat, self.e_flaton_repeat, self.e_flatoff_repeat, self.e_ThAr_repeat_on, self.e_ThAr_repeat_off, self.e_pinholeflat_repeat, self.e_pinholeThAr_repeat, self.e_pinholeoffslit_repeat, self.e_USAFon_repeat, self.e_USAFoff_repeat]
        
        self.sts_ut_pos = [self.sts_ut_pos1, self.sts_ut_pos2]
        self.sts_lt_pos = [self.sts_lt_pos1, self.sts_lt_pos2, self.sts_lt_pos3, self.sts_lt_pos4, self.sts_lt_pos5]
        
        self.bt_ut_move_to = [self.bt_ut_move_to_0, self.bt_ut_move_to_1]
        self.bt_lt_move_to = [self.bt_lt_move_to_0, self.bt_lt_move_to_1, self.bt_lt_move_to_2, self.bt_lt_move_to_3, self.bt_lt_move_to_4]
        
        self.e_utpos.setHidden(True)
        self.e_ltpos.setHidden(True)

        self.chk_whole.clicked.connect(self.cal_whole_check)
        self.bt_run.clicked.connect(self.cal_run)
        self.bt_parking.clicked.connect(self.cal_parking)
        
        self.bt_ut_motor_init.clicked.connect(lambda: self.motor_init(UT))
        self.bt_lt_motor_init.clicked.connect(lambda: self.motor_init(LT))
                
        #for i in range(CAL_CNT):
        self.chk_dark.clicked.connect(lambda: self.cal_set_enabled(0))
        self.chk_flat_on.clicked.connect(lambda: self.cal_set_enabled(1))
        self.chk_flat_off.clicked.connect(lambda: self.cal_set_enabled(2))
        self.chk_ThAr_on.clicked.connect(lambda: self.cal_set_enabled(3))
        self.chk_ThAr_off.clicked.connect(lambda: self.cal_set_enabled(4))
        self.chk_pinhole_flat.clicked.connect(lambda: self.cal_set_enabled(5))
        self.chk_pinhole_ThAr.clicked.connect(lambda: self.cal_set_enabled(6))
        self.chk_pinhole_offslit.clicked.connect(lambda: self.cal_set_enabled(7))
        self.chk_USAF_on.clicked.connect(lambda: self.cal_set_enabled(8))
        self.chk_USAF_off.clicked.connect(lambda: self.cal_set_enabled(9))
        
        self.bt_utpos_prev.clicked.connect(lambda: self.move_motor_delta(UT, PREV))
        self.bt_utpos_next.clicked.connect(lambda: self.move_motor_delta(UT, NEXT))
        
        self.bt_utpos_set1.clicked.connect(lambda: self.motor_pos_set(UT, 0))
        self.bt_utpos_set2.clicked.connect(lambda: self.motor_pos_set(UT, 1))
        
        self.bt_ut_move_to_0.clicked.connect(lambda: self.move_motor(UT, 0))
        self.bt_ut_move_to_1.clicked.connect(lambda: self.move_motor(UT, 1))
        
        self.bt_ltpos_prev.clicked.connect(lambda: self.move_motor_delta(LT, PREV))
        self.bt_ltpos_next.clicked.connect(lambda: self.move_motor_delta(LT, NEXT))
        
        self.bt_ltpos_set1.clicked.connect(lambda: self.motor_pos_set(LT, 0))
        self.bt_ltpos_set2.clicked.connect(lambda: self.motor_pos_set(LT, 1))
        self.bt_ltpos_set3.clicked.connect(lambda: self.motor_pos_set(LT, 2))
        self.bt_ltpos_set4.clicked.connect(lambda: self.motor_pos_set(LT, 3))
        self.bt_ltpos_set5.clicked.connect(lambda: self.motor_pos_set(LT, 4))
        
        self.bt_lt_move_to_0.clicked.connect(lambda: self.move_motor(LT, 0))
        self.bt_lt_move_to_1.clicked.connect(lambda: self.move_motor(LT, 1))
        self.bt_lt_move_to_2.clicked.connect(lambda: self.move_motor(LT, 2))
        self.bt_lt_move_to_3.clicked.connect(lambda: self.move_motor(LT, 3))
        self.bt_lt_move_to_4.clicked.connect(lambda: self.move_motor(LT, 4))
        
        self.protect_btn_ut(False)
        self.protect_btn_lt(False)     
        
        self.bt_lt_motor_init.setEnabled(False)
        self.bt_ut_motor_init.setEnabled(False)  
    
        
        
    #-------------------------------
    # dt publisher
    def connect_to_server_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        ti.sleep(0.2)
        self.producer.send_message(self.dt_q, msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
        
    
    #-------------------------------
    # EngTools queue
    def connect_to_server_EngTools_q(self):
        # RabbitMQ connect
        self.consumer_EngTools = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.EngTools_ex)      
        self.consumer_EngTools.connect_to_server()
        self.consumer_EngTools.define_consumer(self.EngTools_q, self.callback_EngTools)       
        
        th = threading.Thread(target=self.consumer_EngTools.start_consumer)
        th.daemon = True
        th.start()
        
        
    def callback_EngTools(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split() 

        if not (param[0] == ALIVE): return

        msg = "<- [EngTools] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == ALIVE:
                self.simulation = bool(int(param[1]))   
                
                for idx in range(DCS_CNT):
                    if self.simulation:
                        path = WORKING_DIR + "IGRINS/Demo/"
                    else:
                        path = WORKING_DIR + "IGRINS/" + self.dcs_list[idx].lower() + "/"
                    
                    self.e_path[idx].setText(path)
                    self.e_savefilename[idx].setText("")
                    
                msg = "%s %s %d" % (CMD_INIT2_DONE, "all", self.simulation)
                self.publish_to_queue(msg)
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                            
       
    #-------------------------------
    # sub queue
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        sub_dt_ex = [self.com_list[i]+'.ex' for i in range(COM_CNT)]
        for idx in range(COM_CNT):
            self.consumer_sub[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_dt_ex[idx])      
            self.consumer_sub[idx].connect_to_server()
            
        self.consumer_sub[PDU].define_consumer(self.com_list[PDU]+'.q', self.callback_pdu)       
        self.consumer_sub[LT].define_consumer(self.com_list[LT]+'.q', self.callback_lt)
        self.consumer_sub[UT].define_consumer(self.com_list[UT]+'.q', self.callback_ut)
        
        for idx in range(COM_CNT):
            th = threading.Thread(target=self.consumer_sub[idx].start_consumer)
            th.daemon = True
            th.start()
            
        self.publish_to_queue(HK_REQ_PWR_STS)
                    
    
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_REQ_COM_STS or param[0] == HK_REQ_PWR_STS):  return        

        msg = "<- [PDU] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == HK_REQ_COM_STS:
                #self.com_status[PDU] = bool(int(param[1])) 
                pass
                
            elif param[0] == HK_REQ_PWR_STS:
                for i in range(PDU_IDX):
                    self.power_status[i] = param[i+1]

                if self.power_status[0] == ON and self.power_status[1] == ON:
                    self.chk_open_calibration.setEnabled(True)

                if param[-1] == "done" and self.lamp_on:
                    self.bt_take_image.click()
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                    
        
    def callback_lt(self, ch, method, properties, body):
        cmd = body.decode()                 
        param = cmd.split()     

        if not (param[0] == HK_REQ_COM_STS or param[0] == DT_REQ_INITMOTOR or param[0] == DT_REQ_MOVEMOTOR or param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK or param[0] == DT_REQ_SETLT):
            return

        msg = "<- [LT] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_REQ_COM_STS:
                self.bt_lt_motor_init.setEnabled(bool(int(param[1])))
            
            elif param[0] == DT_REQ_INITMOTOR:
                if param[1] == "TRY":
                    msg = "%s - need to initialize" % param[1]
                    self.log.send(self.iam, INFO, msg)  
                elif param[1] == "OK":
                    self.protect_btn_lt(True)
                    self.label_ltpos.setText("0")
                    self.QWidgetBtnColor(self.bt_lt_motor_init, "white", "green")
                    self.motor_initialized[LT-1] = True
                    
            elif param[0] == DT_REQ_MOVEMOTOR:
                self.lt_moved = True
                self.protect_btn_lt(True)
                self.label_ltpos.setText(param[2])
                
                self.QWidgetBtnColor(self.bt_lt_move_to[int(param[1])], "black")

                if self.cal_mode:
                    #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "lt: here!!!!")
                    if self.ut_moved and self.lt_moved:
                        #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "lt: self.ut_moved and self.lt_moved")
                        self.func_lamp(self.cal_cur)
                        #ti.sleep(1)
                    
                        #self.bt_take_image.click()
                    
            elif param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                self.lt_moved = True
                self.protect_btn_lt(True)
                self.label_ltpos.setText(param[1])

            elif param[0] == DT_REQ_SETLT:
                self.label_ltpos.setText(param[2])
                self.sts_lt_pos[int(param[1])].setText(param[2])
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                
        
    def callback_ut(self, ch, method, properties, body):
        cmd = body.decode()           
        param = cmd.split()   
        
        if not (param[0] == HK_REQ_COM_STS or param[0] == DT_REQ_INITMOTOR or param[0] == DT_REQ_MOVEMOTOR or param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK or param[0] == DT_REQ_SETUT):
            return

        msg = "<- [UT] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == HK_REQ_COM_STS:
                self.bt_ut_motor_init.setEnabled(bool(int(param[1])))
                                                
            elif param[0] == DT_REQ_INITMOTOR:
                if param[1] == "TRY":
                    msg = "%s - need to initialize" % param[1]
                    self.log.send(self.iam, INFO, msg)
                elif param[1] == "OK":
                    self.protect_btn_ut(True)
                    self.label_utpos.setText("0")                
                    self.QWidgetBtnColor(self.bt_ut_motor_init, "white", "green")
                    self.motor_initialized[UT-1] = True
                                
            elif param[0] == DT_REQ_MOVEMOTOR:
                self.ut_moved = True
                self.protect_btn_ut(True)
                self.label_utpos.setText(param[2])
                
                self.QWidgetBtnColor(self.bt_ut_move_to[int(param[1])], "black")
                
                if self.cal_mode:
                    #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "ut: here!!!!")
                    if self.ut_moved and self.lt_moved:
                        #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "ut: self.ut_moved and self.lt_moved")
                        self.func_lamp(self.cal_cur)
                        #ti.sleep(1)
                    
                        #self.bt_take_image.click()
            
            elif param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                self.ut_moved = True
                self.protect_btn_ut(True)
                self.label_utpos.setText(param[1])

            elif param[0] == DT_REQ_SETUT:
                self.label_utpos.setText(param[2])
                self.sts_ut_pos[int(param[1])].setText(param[2])
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                                        

    #-------------------------------
    # dcs queue
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        dcs_dt_ex = [self.dcs_list[i]+'.ex' for i in range(DCS_CNT)]
        for idx in range(DCS_CNT):
            self.consumer_dcs[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, dcs_dt_ex[idx])
            self.consumer_dcs[idx].connect_to_server()
        
        self.consumer_dcs[SVC].define_consumer(self.dcs_list[SVC]+'.q', self.callback_svc)  
        self.consumer_dcs[H].define_consumer(self.dcs_list[H]+'.q', self.callback_h)
        self.consumer_dcs[K].define_consumer(self.dcs_list[K]+'.q', self.callback_k)   
        
        for idx in range(DCS_CNT):
            th = threading.Thread(target=self.consumer_dcs[idx].start_consumer)
            th.daemon = True
            th.start()

        msg = "%s %s %d" % (CMD_INIT2_DONE, "all", self.simulation)
        self.publish_to_queue(msg)
            
    
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()
        
        param = cmd.split()
        if not (param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS or param[0] == CMD_SETFSPARAM_ICS or param[0] == CMD_ACQUIRERAMP_ICS or param[0] == CMD_STOPACQUISITION):
            return

        msg = "<- [DCSS] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        self.dcs_status(SVC, cmd)
        
    
    def callback_h(self, ch, method, properties, body):
        cmd = body.decode()

        param = cmd.split()
        if not (param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS or param[0] == CMD_SETFSPARAM_ICS or param[0] == CMD_ACQUIRERAMP_ICS or param[0] == CMD_STOPACQUISITION):
            return

        msg = "<- [DCSH] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        self.dcs_status(H, cmd)
    
    def callback_k(self, ch, method, properties, body):
        cmd = body.decode()

        param = cmd.split()
        if not (param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS or param[0] == CMD_SETFSPARAM_ICS or param[0] == CMD_ACQUIRERAMP_ICS or param[0] == CMD_STOPACQUISITION):
            return

        msg = "<- [DCSK] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        self.dcs_status(K, cmd)
        
        
    def dcs_status(self, dc_idx, cmd):
        param = cmd.split()
        
        try:

            if param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
                self.dcs_ready[dc_idx] = True
                self.bt_init_status(dc_idx)

                if self.radio_HK_sync.isChecked():
                    self.set_HK_sync()
                elif self.radio_whole_sync.isChecked():
                    self.set_whole_sync()
                elif self.radio_SVC.isChecked():
                    self.set_svc()
                elif self.radio_H.isChecked():
                    self.set_H()
                elif self.radio_K.isChecked():
                    self.set_K()
                
            elif param[0] == CMD_SETFSPARAM_ICS:
                next_idx = self.get_next_idx()
                
                msg = "%s %s %d %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_list[dc_idx], self.simulation, next_idx)
                self.publish_to_queue(msg)

            elif param[0] == CMD_ACQUIRERAMP_ICS:                        
                self.cur_cnt[dc_idx] += 1
                self.label_prog_sts[dc_idx].setText("Done")
                
                end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
                self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)
                            
                self.prog_timer[dc_idx].stop()
                self.cur_prog_step[dc_idx] = 100
                self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])           

                self.elapsed_timer[dc_idx].stop()

                self.measure_T[dc_idx] = float(param[1])
                
                # load data
                self.load_data(dc_idx, param[2])
            
                self.acquiring[dc_idx] = False
                #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "self.acquiring[dc_idx]:", dc_idx, self.acquiring[dc_idx])
                
                if self.cal_mode:
                    show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.cal_e_repeat[self.cal_cur].text())
                    self.label_cur_num[dc_idx].setText(show_cur_cnt)

                    if self.cur_cnt[dc_idx] < int(self.cal_e_repeat[self.cal_cur].text()):
                        if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:
                            self.all_acquired = True
                            #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "repeat: not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]", dc_idx)
                            self.bt_take_image.click()

                    else:                                                    
                        if self.cal_stop_clicked:
                            self.enable_dcs(dc_idx, True)

                            if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:   
                                self.func_lamp(self.cal_cur, False)
                                self.all_acquired = True
                                #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "stop: not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]", dc_idx) 
                                self.cal_mode = False
                                self.bt_run.setText("RUN")
                                self.QWidgetBtnColor(self.bt_run, "black")

                                self.QWidgetCheckBoxColor(self.cal_chk[self.cal_cur], "black")                    
                                self.QWidgetEditColor(self.cal_e_exptime[self.cal_cur], "black")
                                self.QWidgetEditColor(self.cal_e_repeat[self.cal_cur], "black")

                                for i in range(DCS_CNT):
                                    self.cur_cnt[i] = 0
                            
                            return             

                        self.enable_dcs(dc_idx, True)
                        if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]: 
                            self.func_lamp(self.cal_cur, False)
                            self.all_acquired = True
                            #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "next frame: not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]", dc_idx)   
                            self.cal_mode = False  
                            self.cal_cur += 1
                            #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "next frame: self.cal_cur += 1")

                            for i in range(DCS_CNT):
                                self.cur_cnt[i] = 0

                            self.cal_run_cycle()

                else:
                    show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.e_repeat[dc_idx].text())
                    self.label_cur_num[dc_idx].setText(show_cur_cnt)
                    
                    '''
                    if self.mode == CONT_MODE and self.stop_clicked:
                        self.enable_dcs(dc_idx, True)
                        
                        if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:    
                            self.all_acquired = True
                            self.protect_btn(True) 
                            self.bt_take_image.setText("Continuous")
                            self.QWidgetBtnColor(self.bt_take_image, "black")
                            self.stop_clicked = False

                            for i in range(DCS_CNT):
                                self.cur_cnt[i] = 0
                        
                    el
                    '''
                    if self.cur_cnt[dc_idx] < int(self.e_repeat[dc_idx].text()):
                        self.continuous[dc_idx] = True
                        self.bt_take_image.click()

                    else:
                        self.enable_dcs(dc_idx, True)

                        if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:                                                    
                            self.all_acquired = True
                            if self.mode == CONT_MODE:
                                self.bt_take_image.setText("Continuous")
                            else:
                                self.bt_take_image.setText("Take Image")
                                
                            self.protect_btn(True) 
                            self.QWidgetBtnColor(self.bt_take_image, "black")
                            #self.stop_clicked = False

                            for i in range(DCS_CNT):
                                self.cur_cnt[i] = 0
        
            elif param[0] == CMD_STOPACQUISITION:
                
                end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
                self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)

                self.enable_dcs(dc_idx, True)

                self.acquiring[dc_idx] = False

                if not self.all_acquired and not self.acquiring[SVC] and not self.acquiring[H] and not self.acquiring[K]:    
                    self.all_acquired = True
                    self.protect_btn(True)                    
                    self.bt_take_image.setText("Take Image")  
                    self.QWidgetBtnColor(self.bt_take_image, "black")
                    #self.stop_clicked = False  
                    
        except:
            self.log.send(self.iam, WARNING, "parsing error")
        
        
    #-------------------------------
    # dcs command
    def initialize2(self, dc_idx):        
        self.dcs_ready[dc_idx] = False
        self.QWidgetBtnColor(self.bt_init[dc_idx], "yellow", "blue")
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, self.dcs_list[dc_idx], self.simulation)
        self.publish_to_queue(msg)
            
        
    def set_fs_param(self, dc_idx):     
        if not self.dcs_ready[dc_idx]:  return

        self.enable_dcs(dc_idx, False)
        
        if self.cal_mode:
            show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.cal_e_repeat[self.cal_cur].text())
            self.e_repeat[dc_idx].setText(self.cal_e_repeat[self.cal_cur].text())
            self.e_exptime[dc_idx].setText(self.cal_e_exptime[self.cal_cur].text())
        
        show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.e_repeat[dc_idx].text())
        self.label_cur_num[dc_idx].setText(show_cur_cnt)   

        #setparam
        _exptime = float(self.e_exptime[dc_idx].text())
        _FS_number = int(self.e_FS_number[dc_idx].text())
        _fowlerTime = _exptime - T_frame * _FS_number
        _cal_waittime = T_br + (T_frame + _fowlerTime + (2 * T_frame * _FS_number))
            
        start_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())       
        
        self.label_prog_sts[dc_idx].setText("Running")
        self.label_prog_time[dc_idx].setText(start_time)

        # progress bar 
        self.prog_timer[dc_idx] = QTimer(self)
        self.prog_timer[dc_idx].setInterval(int(_cal_waittime*10))   
        self.prog_timer[dc_idx].timeout.connect(lambda: self.show_progressbar(dc_idx))    

        self.cur_prog_step[dc_idx] = 0
        self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])    
        self.prog_timer[dc_idx].start()    
        
        # elapsed               
        self.elapsed_timer[dc_idx] = QTimer(self) 
        self.elapsed_timer[dc_idx].setInterval(1)
        self.elapsed_timer[dc_idx].timeout.connect(lambda: self.show_elapsed(dc_idx))

        self.elapsed[dc_idx] = ti.time()
        self.label_prog_elapsed[dc_idx].setText("0.0")    
        self.elapsed_timer[dc_idx].start()

        if self.cur_cnt[dc_idx] == 0:
            msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_list[dc_idx], self.simulation, _exptime, _FS_number, _fowlerTime)
        else:
            next_idx = self.get_next_idx()
            ongoing_filename = "SDC%s_%s_%04d" % (self.dcs_list[dc_idx][-1], self.cur_date, next_idx)
            self.label_ongoing_filename[dc_idx].setText(ongoing_filename)
            msg = "%s %s %d %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_list[dc_idx], self.simulation, next_idx)
        self.publish_to_queue(msg)

        self.acquiring[dc_idx] = True        

        
    def stop_acquistion(self, dc_idx):        
        if self.cur_prog_step[dc_idx] > 0:
            self.prog_timer[dc_idx].stop()
            self.elapsed_timer[dc_idx].stop()

        self.acquiring[dc_idx] = True
                
        msg = "%s %s %d" % (CMD_STOPACQUISITION, self.dcs_list[dc_idx], self.simulation)
        self.publish_to_queue(msg)
        
        
    def get_next_idx(self):
        
        _t = datetime.datetime.utcnow()
        self.cur_date = "%04d%02d%02d" % (_t.year, _t.month, _t.day)
        
        dir_names = []
        if self.sel_mode == MODE_WHOLE or self.sel_mode == MODE_HK or self.sel_mode == MODE_H:
            filepath_h = "%sIGRINS/dcsh/Fowler/%s/" % (WORKING_DIR, self.cur_date)
            for names in os.listdir(filepath_h):
                if names.find(".fits") < 0:
                    dir_names.append(names)

        if self.sel_mode == MODE_WHOLE or self.sel_mode == MODE_HK or self.sel_mode == MODE_K:
            filepath_k = "%sIGRINS/dcsk/Fowler/%s/" % (WORKING_DIR, self.cur_date)   
            for names in os.listdir(filepath_k):
                if names.find(".fits") < 0:
                    dir_names.append(names)
                
        numbers = list(map(int, dir_names))
        
        if len(numbers) > 0:
            next_idx = max(numbers) + 1
        else:
            next_idx = 1
            
        return next_idx
            
    
    def load_data(self, dc_idx, folder_name):
        
        self.label_prog_sts[dc_idx].setText("Transfer")
        
        try:
            filepath = ""
            if self.simulation:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/Demo/SDCS_demo1.fits" % WORKING_DIR
                elif dc_idx == H:
                    filepath = "%sIGRINS/Demo/SDCH_demo.fits" % WORKING_DIR
                elif dc_idx == K:
                    filepath = "%sIGRINS/Demo/SDCK_demo.fits" % WORKING_DIR
            else:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/dcss/Fowler/%s" % (WORKING_DIR, folder_name)
                elif dc_idx == H:
                    filepath = "%sIGRINS/dcsh/Fowler/%s" % (WORKING_DIR, folder_name)
                elif dc_idx == K:
                    filepath = "%sIGRINS/dcsk/Fowler/%s" % (WORKING_DIR, folder_name)
            
            filename = filepath.split("/")
            path = "/"
            for dir in filename:
                if dir != "" and dir.find(".fits") < 0:
                    path += dir + "/"
            self.e_path[dc_idx].setText(path)
            self.e_savefilename[dc_idx].setText(filename[-1])
            
            frm = fits.open(filepath)
            data = frm[0].data
            self.header[dc_idx] = frm[0].header
            _img = np.array(data, dtype = "f")
            #_img = np.flipud(np.array(data, dtype = "f"))
            self.img[dc_idx] = _img#[0:FRAME_Y, 0:FRAME_X]
            #self.img = _img
            
            self.zmin, self.zmax = zs.zscale(self.img[dc_idx])
            range = "%d ~ %d" % (self.zmin, self.zmax)
            
            if dc_idx == SVC:
                self.label_zscale_range.setText(range)
            
                self.mmin, self.mmax = np.min(self.img[SVC]), np.max(self.img[SVC])
                self.e_mscale_min.setText("%.1f" % self.mmin)
                self.e_mscale_max.setText("%.1f" % self.mmax)
                    
            if self.chk_ds9[dc_idx].isChecked():
                ds9 = WORKING_DIR + 'IGRINS/ds9'
                subprocess.Popen([ds9, filepath])
                            
            self.reload_img(dc_idx)
        
        except:
            self.img[dc_idx] = None
            self.log.send(self.iam, WARNING, "No image")
            
        
    def reload_img(self, dc_idx):   
        
        try:
            #_img = np.flipud(self.img[dc_idx])
            #_img = np.fliplr(np.rot90(self.img[dc_idx])
            
            _img = self.img[dc_idx]
                            
            if dc_idx == SVC:
                _min, _max = 0, 0
                if self.radio_zscale.isChecked():
                    _min, _max = self.zmin, self.zmax
                elif self.radio_mscale.isChecked():
                    _min, _max = self.mmin, self.mmax
            else:
                _min, _max = self.zmin, self.zmax
                                
            self.image_ax[dc_idx].imshow(_img, vmin=_min, vmax=_max, cmap='gray', origin='lower')
            self.image_canvas[dc_idx].draw()
            
            self.label_prog_sts[dc_idx].setText("Idle")
                
        except:
            self.img[dc_idx] = None
            self.log.send(self.iam, WARNING, "No image")


    def clean_ax(self, ax, ticks_off = True):
        ax.cla()
        if ticks_off:
            ax.set_xticklabels([])
            ax.set_yticklabels([])

            ax.set_frame_on(False)
            ax.set_xticks([])
            ax.set_yticks([])
                        
            
    def enable_dcs(self, dc_idx, enable):
        self.radio_exptime[dc_idx].setEnabled(enable)
        self.e_exptime[dc_idx].setEnabled(enable)

        self.radio_N_fowler[dc_idx].setEnabled(enable)
        self.e_FS_number[dc_idx].setEnabled(enable)

        self.e_repeat[dc_idx].setEnabled(enable)
        self.chk_ds9[dc_idx].setEnabled(enable)
                
        if self.radio_exptime[dc_idx].isChecked() and enable:
            self.judge_exp_time(dc_idx)
        elif self.radio_N_fowler[dc_idx].isChecked() and enable:
            self.judge_FS_number(dc_idx)
            
            
    def show_elapsed(self, dc_idx):
        cur_elapsed = ti.time() - self.elapsed[dc_idx]
        if self.measure_T[dc_idx] > 0 and cur_elapsed >= self.measure_T[dc_idx]: # or (self.mode == SINGLE_MODE and self.stop_clicked):
            self.elapsed_timer[dc_idx].stop()
            return
        
        msg = "%.3f sec" % (ti.time() - self.elapsed[dc_idx])
        self.label_prog_elapsed[dc_idx].setText(msg)


    def show_progressbar(self, dc_idx):
        if self.cur_prog_step[dc_idx] >= 100: # or (self.mode == SINGLE_MODE and self.stop_clicked):
            self.prog_timer[dc_idx].stop()
            #self.log.send(self.iam, INFO, "progress bar end!!!")
            return
        
        self.cur_prog_step[dc_idx] += 1
        self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])


    def protect_btn(self, enable):
        self.radio_HK_sync.setEnabled(enable)
        self.radio_whole_sync.setEnabled(enable)
        self.radio_SVC.setEnabled(enable)
        self.radio_H.setEnabled(enable)
        self.radio_K.setEnabled(enable)
        
        #if enable == False and self.bt_take_image.text() == "Stop":
        #    self.bt_take_image.setEnabled(True)
        #else:
        #    self.bt_take_image.setEnabled(enable)

        for dc_idx in range(DCS_CNT):
            self.bt_init[dc_idx].setEnabled(enable)
            self.bt_init_status(dc_idx)
            
    
    def protect_btn_ut(self, enable):
        self.bt_utpos_prev.setEnabled(enable)
        #self.label_utpos.setEnabled(enable)
        self.bt_utpos_next.setEnabled(enable)
                
        self.bt_utpos_set1.setEnabled(enable)
        self.bt_utpos_set2.setEnabled(enable)
        
        for i in range(2):
            self.bt_ut_move_to[i].setEnabled(enable)
            if not enable:
                color = "silver"
            else:
                color = "black"
            self.QWidgetBtnColor(self.bt_ut_move_to[i], color)
        
    
    def protect_btn_lt(self, enable):
        self.bt_ltpos_prev.setEnabled(enable)
        #self.label_ltpos.setEnabled(enable)
        self.bt_ltpos_next.setEnabled(enable)
                
        self.bt_ltpos_set1.setEnabled(enable)
        self.bt_ltpos_set2.setEnabled(enable)
        self.bt_ltpos_set3.setEnabled(enable)
        self.bt_ltpos_set4.setEnabled(enable)
        self.bt_ltpos_set5.setEnabled(enable)
        
        for i in range(5):
            self.bt_lt_move_to[i].setEnabled(enable)
            if not enable:
                color = "silver"
            else:
                color = "black"
            self.QWidgetBtnColor(self.bt_lt_move_to[i], color)
                                    
        
    def QWidgetEditColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QLineEdit {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QLineEdit {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
        
        
    def QWidgetCheckBoxColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QCheckBox {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QCheckBox {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
            
            
    def QWidgetBtnColor(self, widget, textcolor, bgcolor=None):
        if bgcolor == None:
            label = "QPushButton {color:%s}" % textcolor
            widget.setStyleSheet(label)
        else:
            label = "QPushButton {color:%s;background:%s}" % (textcolor, bgcolor)
            widget.setStyleSheet(label)
        
    
    #---------------------------------
    # button 
    
    def auto_scale(self):
        self.reload_img(SVC)
        self.bt_scale_apply.setEnabled(False)
    
    
    def manual_scale(self):
        self.reload_img(SVC)
        self.bt_scale_apply.setEnabled(True)
    
    
    def scale_apply(self):
        self.mmin = float(self.e_mscale_min.text())
        self.mmax = float(self.e_mscale_max.text())
        
        self.reload_img(SVC)
    
    
    def set_HK_sync(self):
        self.sel_mode = MODE_HK
        self.bt_init[SVC].setEnabled(False)
        if self.dcs_ready[H]:
            self.bt_init[H].setEnabled(True)
            self.enable_dcs(H, True)
        if self.dcs_ready[K]:
            self.bt_init[K].setEnabled(True)
        for idx in range(DCS_CNT):
            self.bt_init_status(idx)
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(K, False)
            
    
    def set_whole_sync(self):
        self.sel_mode = MODE_WHOLE
        for idx in range(DCS_CNT):
            if self.dcs_ready[idx]:
                self.bt_init[idx].setEnabled(True)
                if idx == SVC:
                    self.enable_dcs(idx, True)
                else:
                    self.enable_dcs(idx, False)
            self.bt_init_status(idx)
                    
    
    def set_svc(self):
        self.sel_mode = MODE_SVC
        if self.dcs_ready[SVC]:
            self.bt_init[SVC].setEnabled(True)
            self.enable_dcs(SVC, True)
        self.bt_init[H].setEnabled(False)
        self.bt_init[K].setEnabled(False)
        
        for idx in range(DCS_CNT):
            self.bt_init_status(idx)
        
        self.enable_dcs(H, False)
        self.enable_dcs(K, False)
    
    
    def set_H(self):
        self.sel_mode = MODE_H
        self.bt_init[SVC].setEnabled(False)
        if self.dcs_ready[H]:
            self.bt_init[H].setEnabled(True)
            self.enable_dcs(H, True)
        self.bt_init[K].setEnabled(False)
        
        for idx in range(DCS_CNT):
            self.bt_init_status(idx)
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(K, False)
    
    
    def set_K(self):
        self.sel_mode = MODE_K
        self.bt_init[SVC].setEnabled(False)
        self.bt_init[H].setEnabled(False)
        if self.dcs_ready[K]:
            self.bt_init[K].setEnabled(True)
            self.enable_dcs(K, True)
            
        for idx in range(DCS_CNT):
            self.bt_init_status(idx)
        
        self.enable_dcs(SVC, False)
        self.enable_dcs(H, False)
        
        
    def bt_init_status(self, idx):
        if self.dcs_ready[idx] and self.bt_init[idx].isEnabled():
                self.QWidgetBtnColor(self.bt_init[idx], "white", "green")
        else:
            self.QWidgetBtnColor(self.bt_init[idx], "black", "silver")
        
        
    # click: when to start or when to stop
    def btn_click(self):
        self.all_acquired = False
        
        if self.cal_mode:
            self.call_set_fs_param()

        else:
            if self.mode == CONT_MODE:                
                if self.continuous[H] and not self.continuous[K] and not self.continuous[SVC]:
                    self.set_fs_param(H)
                    self.continuous[H] = False
                elif not self.continuous[H] and self.continuous[K] and not self.continuous[SVC]:
                    self.set_fs_param(K)
                    self.continuous[K] = False
                elif not self.continuous[H] and not self.continuous[K] and self.continuous[SVC]:
                    self.set_fs_param(SVC)
                    self.continuous[SVC] = False
                '''
                else:
                    self.stop_clicked = False
                    if btn_name == "Stop":
                        self.stop_clicked = True
                    else:
                        self.single_exposure()
            else:
                self.stop_clicked = False
                '''
                     
            if self.bt_take_image.text() == "Abort":
                self.abort_acquisition()
            else:
                self.single_exposure()
                
        
    def single_exposure(self):    
        self.QWidgetBtnColor(self.bt_take_image, "yellow", "blue")
        
        #if int(self.e_repeat[SVC].text()) > 1 or int(self.e_repeat[H].text()) > 1 or int(self.e_repeat[K].text()) > 1:
        #    self.bt_take_image.setText("Stop")
        #else:
        self.bt_take_image.setText("Abort")
                    
        self.call_set_fs_param()
        
        self.protect_btn(False)
                            

    def call_set_fs_param(self):   
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.set_fs_param(H)
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.set_fs_param(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.set_fs_param(SVC)


    def abort_acquisition(self):        
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.stop_acquistion(H)
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.stop_acquistion(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.stop_acquistion(SVC)
                    
    
    def judge_exp_time(self, dc_idx):
        self.e_exptime[dc_idx].setEnabled(True)
        self.e_FS_number[dc_idx].setEnabled(False)
        
        if dc_idx == SVC and self.sel_mode == MODE_WHOLE:
            for idx in range(2):
                self.e_exptime[idx+1].setEnabled(True)
                self.e_FS_number[idx+1].setEnabled(False)
        elif dc_idx == H and self.sel_mode == MODE_HK:
            self.e_exptime[K].setEnabled(True)
            self.e_FS_number[K].setEnabled(False)
        
        
    def judge_FS_number(self, dc_idx):
        self.e_exptime[dc_idx].setEnabled(False)
        self.e_FS_number[dc_idx].setEnabled(True)
        
        if dc_idx == SVC and self.sel_mode == MODE_WHOLE:
            for idx in range(2):
                self.e_exptime[idx+1].setEnabled(False)
                self.e_FS_number[idx+1].setEnabled(True)
        elif dc_idx == H and self.sel_mode == MODE_HK:
            self.e_exptime[K].setEnabled(False)
            self.e_FS_number[K].setEnabled(True)
        
        
    def judge_param(self, dc_idx):
        if self.e_exptime[dc_idx].text() == "" or self.e_FS_number[dc_idx].text() == "":    return
        
        # calculation fowler number & exp time
        _expTime = float(self.e_exptime[dc_idx].text())
        _fowler_num = int(self.e_FS_number[dc_idx].text())

        _fowler_time = T_exp

        if self.radio_exptime[dc_idx].isChecked():
            _max_fowler_number = int((_expTime - T_minFowler) / T_frame)
            if _fowler_num > _max_fowler_number:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'exposure time'!")
                self.log.send(self.iam, WARNING, "please change 'exposure time'!")
                return

        elif self.radio_N_fowler[dc_idx].isChecked():
            _fowler_time = _expTime - T_frame * _fowler_num
            if _fowler_time < T_minFowler:
                #dialog box
                QMessageBox.warning(self, WARNING, "please change 'fowler sampling number'!")
                self.log.send(self.iam, WARNING, "please change 'fowler sampling number'!")
                return        
            
    
    def change_name(self, dc_idx):
        if int(self.e_repeat[dc_idx].text()) > 1:
            self.bt_take_image.setText("Continuous")
            self.mode = CONT_MODE
        else:
            self.bt_take_image.setText("Take Image")
            self.mode = SINGLE_MODE
        self.QWidgetBtnColor(self.bt_take_image, "black")
        #self.stop_clicked = False
        
        
    def sync_apply_HK(self):
        if self.sel_mode != MODE_WHOLE:
            return
        
        for idx in range(2):
            self.e_exptime[idx+1].setText(self.e_exptime[SVC].text())
            self.e_FS_number[idx+1].setText(self.e_exptime[SVC].text())
            self.e_repeat[idx+1].setText(self.e_exptime[SVC].text())   
            
            
    def sync_apply_K(self):
        if self.sel_mode != MODE_HK:
            return
        
        self.e_exptime[K].setText(self.e_exptime[H].text())
        self.e_FS_number[K].setText(self.e_exptime[H].text())
        self.e_repeat[K].setText(self.e_exptime[H].text())
                    
    
    def open_calilbration(self):                
        if self.chk_open_calibration.isChecked():
            self.setFixedSize(1315, 741)
            self.setGeometry(0, 0, 1315, 741)
            self.power_status[MOTOR-1] = ON
            self.power_onoff()

            cmd = "%sics_pack/code/SubSystems/motor.py" % WORKING_DIR
            if self.proc_sub[LT] == None:
                self.proc_sub[LT] = subprocess.Popen(['python', cmd, self.com_list[LT]])          
            if self.proc_sub[UT] == None:
                self.proc_sub[UT] = subprocess.Popen(['python', cmd, self.com_list[UT]])
                
            self.bt_take_image.setEnabled(False)
            
        else:
            self.setFixedSize(1030, 741)
            self.setGeometry(0, 0, 1030, 741)
            self.power_status[MOTOR-1] = OFF
            self.power_onoff()
            
            self.bt_take_image.setEnabled(True)

                
         
        


    #-------------------------------------------------
    # calibration
    def cal_whole_check(self):
        check = self.chk_whole.isChecked()
        
        for i in range(CAL_CNT):
            self.cal_chk[i].setChecked(check)
            self.cal_set_enabled(i)


    def set_run_status(self):        
        run = False
        for idx in self.cal_chk:
            if idx.isChecked():
                run = True                
                break

        if run:
            color = "black"
            self.bt_run.setEnabled(True)
        else:
            color = "silver"
            self.bt_run.setEnabled(False)
        self.QWidgetBtnColor(self.bt_run, color)

    
    def cal_set_enabled(self, cal_cnt):
        if self.cal_chk[cal_cnt].isChecked():
            self.cal_e_exptime[cal_cnt].setEnabled(True)
            self.cal_e_repeat[cal_cnt].setEnabled(True)
            self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "black")
            self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "black")
        else:
            self.cal_e_exptime[cal_cnt].setEnabled(False)
            self.cal_e_repeat[cal_cnt].setEnabled(False)
            self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "silver")
            self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "silver")

        self.set_run_status()
        
        
    def cal_run(self):

        if not self.motor_initialized[LT-1] or not self.motor_initialized[UT-1]:    return

        btn_name = self.bt_run.text()
        self.cal_stop_clicked = False
        if btn_name == "STOP":
            self.cal_stop_clicked = True
            self.cal_cur = 0
            self.bt_run.setText("RUN")
            self.QWidgetBtnColor(self.bt_run, "black") 
        elif btn_name == "RUN":
            self.cal_cur = 0
            self.bt_run.setText("STOP")
            self.QWidgetBtnColor(self.bt_run, "yellow", "blue")
        
            self.cal_run_cycle()   
        
            
    def cal_run_cycle(self):

        self.cal_mode = True
        
        nothing = True
        for cal_cnt in range(CAL_CNT):
            if self.cal_chk[cal_cnt].isChecked():
                if cal_cnt == self.cal_cur:
                    #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "current idx:", self.cal_cur)
                    self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt], "blue") 
                    self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "blue")
                    self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "blue")
                    self.func_motor(cal_cnt)   
                    nothing = False
                    break
                else:
                    self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt], "black")                    
                    self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "black")
                    self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "black")
            else:
                if cal_cnt >= self.cal_cur:
                    self.cal_cur += 1
                    #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "self.cal_cur += 1, in def cal_run_cycle", self.cal_cur)
        
        if nothing:
            self.bt_run.setText("RUN")
            self.QWidgetBtnColor(self.bt_run, "black")
            self.cal_stop_clicked = True
            self.cal_mode = False
            
            
    def cal_parking(self):
        self.power_status[FLAT-1] = OFF
        self.power_status[THAR-1] = OFF
        self.power_onoff()
        
        self.move_motor(UT, 0)
        self.move_motor(LT, 0)
        
                        
    def power_onoff(self):
        pwr_list = ""
        for i in range(PDU_IDX):
            pwr_list += self.power_status[i] + " "
        msg = "%s %s" % (HK_REQ_PWR_ONOFF, pwr_list)
        self.publish_to_queue(msg)
        #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "power:", pwr_list)



    def func_lamp(self, idx, on=True):        

        self.lamp_on = on

        if on:
            self.power_status[FLAT-1] = LAMP_FLAT[idx]
        else:
            self.power_status[FLAT-1] = OFF          
        
        if on:
            self.power_status[THAR-1] = LAMP_THAR[idx]
        else:
            self.power_status[THAR-1] = OFF            
       
        self.power_onoff()
                        
            
    def func_motor(self, idx):       
        self.bt_ut_move_to[MOTOR_UT_POS[idx]].click()
        self.bt_lt_move_to[MOTOR_LT_POS[idx]].click()
                                
        
    def motor_init(self, motor):
        if motor == UT:
            self.protect_btn_ut(False)
            self.QWidgetBtnColor(self.bt_ut_motor_init, "yellow", "blue")
            self.bt_ut_motor_init.setEnabled(False)
        elif motor == LT:
            self.protect_btn_lt(False)
            self.QWidgetBtnColor(self.bt_lt_motor_init, "yellow", "blue")
            self.bt_lt_motor_init.setEnabled(False)
            
        msg = "%s %s" % (DT_REQ_INITMOTOR, self.com_list[motor])
        self.publish_to_queue(msg)
            
    
    def move_motor(self, motor, pos): #motor-UT/LT, position number
        if motor == UT:
            self.ut_moved = False
            self.protect_btn_ut(False)
            self.QWidgetBtnColor(self.bt_ut_move_to[pos], "yellow", "blue")
        elif motor == LT:
            self.lt_moved = False
            self.protect_btn_lt(False)
            self.QWidgetBtnColor(self.bt_lt_move_to[pos], "yellow", "blue")
            
        msg = "%s %s %d" % (DT_REQ_MOVEMOTOR, self.com_list[motor], pos)
        self.publish_to_queue(msg)
        #print(ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime()), "move_motor", motor, pos)
        

    def move_motor_delta(self, motor, direction): #motor-UT/LT, direction-prev, next
        if motor == UT:
            if direction == PREV:
                curpos = int(self.label_utpos.text()) - int(self.e_movinginterval.text())
                self.label_utpos.setText(str(curpos))
                msg = "%s %s %s" % (DT_REQ_MOTORBACK, self.com_list[motor], self.e_movinginterval.text())
            else:
                curpos = int(self.label_utpos.text()) + int(self.e_movinginterval.text())
                self.label_utpos.setText(str(curpos))
                msg = "%s %s %s" % (DT_REQ_MOTORGO, self.com_list[motor], self.e_movinginterval.text())
            self.protect_btn_ut(False)
            
        elif motor == LT:
            if direction == PREV:
                curpos = int(self.label_ltpos.text()) - int(self.e_movinginterval.text())
                self.label_ltpos.setText(str(curpos))
                msg = "%s %s %s" % (DT_REQ_MOTORBACK, self.com_list[motor], self.e_movinginterval.text())
            else:
                curpos = int(self.label_ltpos.text()) + int(self.e_movinginterval.text())
                self.label_ltpos.setText(str(curpos))
                msg = "%s %s %s" % (DT_REQ_MOTORGO, self.com_list[motor], self.e_movinginterval.text())
                
            self.protect_btn_lt(False)
        self.publish_to_queue(msg)
                
    
    def motor_pos_set(self, motor, position): #motor-UT/LT, direction-UT(0/1), LT(0-4)
        msg = "Do you really want to modify the position %s value?" % str(position)
        reply = QMessageBox.question(self, WARNING, msg, QMessageBox.Yes | QMessageBox.No)
        if reply == QMessageBox.No: return
        
        if motor == UT:
            msg = "%s %d" % (DT_REQ_SETUT, position)
        elif motor == LT:
            msg = "%s %d" % (DT_REQ_SETLT, position)
        self.publish_to_queue(msg)
    


if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    dt = MainWindow()
    dt.show()
        
    app.exec()