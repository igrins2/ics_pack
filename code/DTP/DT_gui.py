# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Mar 10, 2023

@author: hilee
"""

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
        
        self.setFixedSize(1030, 700)
        self.setGeometry(0, 0, 1030, 700)
        self.setWindowTitle("Data Taking Package 1.0")        
        
        # canvas
        #self.image_fig = []
        self.image_ax = []
        self.image_canvas = []
        
        for i in range(DCS_CNT):
            _image_fig = Figure(figsize=(4, 4), dpi=100)
            self.image_ax.append(_image_fig.add_subplot(111))
            _image_fig.subplots_adjust(left=0.01,right=0.99,bottom=0.01,top=0.99) 
            self.image_canvas.append(FigureCanvas(_image_fig))
        
        vbox_svc = QVBoxLayout(self.frame_svc)
        vbox_svc.addWidget(self.image_canvas[SVC])
        vbox_H = QVBoxLayout(self.frame_H)
        vbox_H.addWidget(self.image_canvas[H])
        vbox_K = QVBoxLayout(self.frame_K)
        vbox_K.addWidget(self.image_canvas[K])
                
        # load ini file
        self.cfg = sc.LoadConfig(WORKING_DIR + "IGRINS/Config/IGRINS.ini")
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.dt_main_ex = self.cfg.get(MAIN, 'gui_main_exchange')     
        self.dt_main_q = self.cfg.get(MAIN, 'gui_main_routing_key')
        self.main_dt_ex = self.cfg.get(MAIN, 'main_gui_exchange')
        self.main_dt_q = self.cfg.get(MAIN, 'main_gui_routing_key')
        
        self.dt_sub_ex = self.cfg.get(MAIN, 'hk_sub_exchange')
        self.dt_sub_q = self.cfg.get(MAIN, 'hk_sub_routing_key')
        
        self.dt_dcs_ex = self.cfg.get(DT, 'dt_dcs_exchange')     
        self.dt_dcs_q = self.cfg.get(DT, 'dt_dcs_routing_key')
        
        self.fits_path = self.cfg.get(DT, 'fits_path')
        
        self.com_list = ["pdu", "lt", "ut"]
        self.dcs_list = ["DCSS", "DCSH", "DCSK"]
        
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
            
        self.today = ti.strftime("%04Y%02m%02d", ti.localtime())
        self.cur_frame = [0, 0, 0]
        
        for i in range(DCS_CNT):
            self.label_cur_num[i].setText("0 / 0")
            self.e_path[i].setText(self.fits_path + self.today)
            self.cur_frame[i] = self.new_seq(i)
            filename = "%s_%04d.fits" % (self.dcs_list[i], self.cur_frame[i])
            self.e_savefilename[i].setText(filename)
                    
        for i in range(CAL_CNT):
            self.cal_e_exptime[i].setText("1.63")
            self.cal_e_repeat[i].setText("1")
        
        self.e_utpos.setText("---")
        self.e_ltpos.setText("---")
        
        self.e_movinginterval.setText("1")        
        
        self.simulation = NONE_MODE     #from EngTools
        
        self.mode = SINGLE_MODE
        self.continuous = False
        
        self.cal_mode = False

        self.dcs_ready = [False for _ in range(DCS_CNT)]
        self.acquiring = [False for _ in range(DCS_CNT)]
                
        self.producer = [None for _ in range(SERV_CONNECT_CNT)]
        
        self.img = [None for _ in range(DCS_CNT)]
        
        self.output_channel = 32
        
        self.cur_cnt = [0 for _ in range(DCS_CNT)]
        self.measure_T = [0 for _ in range(DCS_CNT)]
        self.header = [None for _ in range(DCS_CNT)]
        
        self.sel_mode = MODE_HK
        self.radio_HK_sync.setChecked(True)
        self.set_HK_sync()
        
        self.stop_clicked = False
        self.cal_stop_clicked = False
        
        self.cal_cur = 0
        self.ut_moved = False
        self.lt_moved = False
        
        self.power_status = [OFF for _ in range(PDU_IDX)] # motor, FLAT, THAR
        self.com_status = [True for _ in range(COM_CNT)]
           
        for i in range(CAL_CNT):
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])         
        
        # progress bar     
        self.prog_timer = [None for _ in range(DCS_CNT)]
        self.cur_prog_step = [0 for _ in range(DCS_CNT)]
        for dc_idx in range(DCS_CNT):
            self.progressBar[dc_idx].setValue(0)
        
        # elapsed
        self.elapsed_timer = [None for _ in range(DCS_CNT)]
        self.elapsed = [0.0 for _ in range(DCS_CNT)]
        
        self.proc_sub = [None for _ in range(COM_CNT)]
        self.param_sub = ["" for _ in range(COM_CNT)]  #pdu, lt, ut
        self.param_dcs = ["" for _ in range(DCS_CNT)]   #h, k, s
        
        # connect to server
        self.connect_to_server_main_ex()
        self.connect_to_server_gui_q()
    
        self.connect_to_server_hk_ex()
        self.connect_to_server_sub_q()
        
        self.connect_to_server_dt_ex()
        self.connect_to_server_dcs_q() 
                    
        self.show_sub_timer = QTimer(self)
        self.show_sub_timer.setInterval(0.5)
        self.show_sub_timer.timeout.connect(self.sub_data_processing) 
        
        self.show_dcs_timer = QTimer(self)
        self.show_dcs_timer.setInterval(0.1)
        self.show_dcs_timer.timeout.connect(self.dcs_data_processing)     
        self.show_dcs_timer.start()           
        
        self.alive_check()       
        
        
    def closeEvent(self, event: QCloseEvent) -> None:   
        
        self.show_sub_timer.stop()
        self.show_dcs_timer.stop()
                 
        self.log.send(self.iam, DEBUG, "Closing %s : " % sys.argv[0])
        self.log.send(self.iam, DEBUG, "This may take several seconds waiting for threads to close")
            
        self.power_onoff(MOTOR, OFF)
        ti.sleep(1)
        self.power_onoff(FLAT, OFF)
        ti.sleep(1)
        self.power_onoff(THAR, OFF)
        ti.sleep(1)
        
        for i in range(COM_CNT):
            if self.proc_sub[i] != None:
                self.proc_sub[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc_sub[i].pid) + " exit")
                        
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")
                                                    
        for i in range(SERV_CONNECT_CNT):                
            if i == ENG_TOOLS:
                msg = "%s %s" % (EXIT, DT)
                self.producer[ENG_TOOLS].send_message(self.dt_main_q, msg)
            
            if self.producer[i] != None:
                self.producer[i].__del__()

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

        self.bt_init = [self.bt_init_SVC, self.bt_init_H, self.bt_init_K]
        self.chk_ds9 = [self.chk_ds9_svc, self.chk_ds9_H, self.chk_ds9_K]
        self.chk_autosave = [self.checkBox_autosave_svc, self.checkBox_autosave_H, self.checkBox_autosave_K]
        
        self.bt_save = [self.bt_save_svc, self.bt_save_H, self.bt_save_K]
        self.bt_path = [self.bt_path_svc, self.bt_path_H, self.bt_path_K]
                    
        self.e_path = [self.e_path_svc, self.e_path_H, self.e_path_K]
        self.e_savefilename = [self.e_savefilename_svc, self.e_savefilename_H, self.e_savefilename_K]
        
        for i in range(DCS_CNT):
            self.radio_exptime[i].setChecked(True)
            
            self.e_exptime[i].setEnabled(False)
            self.e_FS_number[i].setEnabled(False)
            self.e_repeat[i].setEnabled(False)
            
            self.chk_ds9[i].setEnabled(False)
            self.chk_autosave[i].setEnabled(False)
            
            self.bt_init[i].setEnabled(False)
            self.bt_save[i].setEnabled(False)
            self.bt_path[i].setEnabled(False)
            
            self.e_path[i].setEnabled(False)
            self.e_savefilename[i].setEnabled(False)               
            
        self.radio_exptime[SVC].clicked.connect(lambda: self.judge_exp_time(SVC)) 
        self.radio_N_fowler[SVC].clicked.connect(lambda: self.judge_FS_number(SVC))
        self.e_exptime[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_FS_number[SVC].editingFinished.connect(lambda: self.judge_param(SVC))
        self.e_repeat[SVC].editingFinished.connect(lambda: self.change_name(SVC))
        
        self.radio_exptime[H].clicked.connect(lambda: self.judge_exp_time(H)) 
        self.radio_N_fowler[H].clicked.connect(lambda: self.judge_FS_number(H))
        self.e_exptime[H].editingFinished.connect(lambda: self.judge_param(H))
        self.e_FS_number[H].editingFinished.connect(lambda: self.judge_param(H)) 
        self.e_repeat[H].editingFinished.connect(lambda: self.change_name(H))
        
        self.radio_exptime[K].clicked.connect(lambda: self.judge_exp_time(K)) 
        self.radio_N_fowler[K].clicked.connect(lambda: self.judge_FS_number(K))
        self.e_exptime[K].editingFinished.connect(lambda: self.judge_param(K))
        self.e_FS_number[K].editingFinished.connect(lambda: self.judge_param(K)) 
        self.e_repeat[K].editingFinished.connect(lambda: self.change_name(K)) 
        
        self.bt_init[SVC].clicked.connect(lambda: self.initialize2(SVC))    
        self.bt_save[SVC].clicked.connect(lambda: self.save_fits(SVC))
        self.bt_path[SVC].clicked.connect(lambda: self.open_path(SVC))
        
        self.bt_init[H].clicked.connect(lambda: self.initialize2(H))    
        self.bt_save[H].clicked.connect(lambda: self.save_fits(H))
        self.bt_path[H].clicked.connect(lambda: self.open_path(H))
        
        self.bt_init[K].clicked.connect(lambda: self.initialize2(K))    
        self.bt_save[K].clicked.connect(lambda: self.save_fits(K))
        self.bt_path[K].clicked.connect(lambda: self.open_path(K))
            
            
        #------------------
        #calibration
        
        self.chk_open_calibration.clicked.connect(self.open_calilbration)
        
        self.cal_chk = [self.chk_dark, self.chk_flat_on, self.chk_flat_off, self.chk_ThAr, self.chk_pinhole_flat, self.chk_pinhole_ThAr, self.chk_USAF_on, self.chk_USAF_off, self.chk_parking]
        
        self.cal_e_exptime = [self.e_dark_exptime, self.e_flaton_exptime, self.e_flatoff_exptime, self.e_ThAr_exptime, self.e_pinholeflat_exptime, self.e_pinholeThAr_exptime, self.e_USAFon_exptime, self.e_USAFoff_exptime, self.e_parking_exptime]
        
        self.cal_e_repeat = [self.e_dark_repeat, self.e_flaton_repeat, self.e_flatoff_repeat, self.e_ThAr_repeat, self.e_pinholeflat_repeat, self.e_pinholeThAr_repeat, self.e_USAFon_repeat, self.e_USAFoff_repeat, self.e_parking_repeat]
        
        self.chk_whole.clicked.connect(self.cal_whole_check)
        self.bt_run.clicked.connect(self.cal_run)
        
        self.bt_ut_motor_init.clicked.connect(lambda: self.motor_init(UT))
        self.bt_lt_motor_init.clicked.connect(lambda: self.motor_init(LT))
                
        #for i in range(CAL_CNT):
        self.chk_dark.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[0], self.cal_e_exptime[0], self.cal_e_repeat[0]))
        self.chk_flat_on.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[1], self.cal_e_exptime[1], self.cal_e_repeat[1]))
        self.chk_flat_off.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[2], self.cal_e_exptime[2], self.cal_e_repeat[2]))
        self.chk_ThAr.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[3], self.cal_e_exptime[3], self.cal_e_repeat[3]))
        self.chk_pinhole_flat.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[4], self.cal_e_exptime[4], self.cal_e_repeat[4]))
        self.chk_pinhole_ThAr.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[5], self.cal_e_exptime[5], self.cal_e_repeat[5]))
        self.chk_USAF_on.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[6], self.cal_e_exptime[6], self.cal_e_repeat[6]))
        self.chk_USAF_off.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[7], self.cal_e_exptime[7], self.cal_e_repeat[7]))
        self.chk_parking.clicked.connect(lambda: self.cal_use_parsing(self.cal_chk[8], self.cal_e_exptime[8], self.cal_e_repeat[8]))
        
        self.bt_utpos_prev.clicked.connect(lambda: self.move_motor_delta(UT, PREV))
        self.bt_utpos_next.clicked.connect(lambda: self.move_motor_delta(UT, NEXT))
        
        self.bt_utpos_set1.clicked.connect(lambda: self.motor_pos_set(UT, 0))
        self.bt_utpos_set2.clicked.connect(lambda: self.motor_pos_set(UT, 1))
        
        self.bt_ltpos_prev.clicked.connect(lambda: self.move_motor_delta(LT, PREV))
        self.bt_ltpos_next.clicked.connect(lambda: self.move_motor_delta(LT, NEXT))
        
        self.bt_ltpos_set1.clicked.connect(lambda: self.motor_pos_set(LT, 0))
        self.bt_ltpos_set2.clicked.connect(lambda: self.motor_pos_set(LT, 1))
        self.bt_ltpos_set3.clicked.connect(lambda: self.motor_pos_set(LT, 2))
        self.bt_ltpos_set4.clicked.connect(lambda: self.motor_pos_set(LT, 3))
        
        self.protect_btn_ut(False)
        self.protect_btn_lt(False)     
        
        self.bt_lt_motor_init.setEnabled(False)
        self.bt_ut_motor_init.setEnabled(False)  
        
        
    def alive_check(self):
        if self.simulation != NONE_MODE:
            return

        if self.producer[ENG_TOOLS] != None:
            msg = "%s %s" % (ALIVE, DT)
            self.producer[ENG_TOOLS].send_message(self.dt_main_q, msg) 
        
        threading.Timer(0.5, self.alive_check).start()
        
        
    #-------------------------------
    # dt -> main
    def connect_to_server_main_ex(self):
        # RabbitMQ connect  
        self.producer[ENG_TOOLS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_main_ex)      
        self.producer[ENG_TOOLS].connect_to_server()
        self.producer[ENG_TOOLS].define_producer()
    
         
    #-------------------------------
    # main -> dt
    def connect_to_server_gui_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.main_dt_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.main_dt_q, self.callback_main)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
        
        
    #-------------------------------
    # rev <- main        
    def callback_main(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()     
        
        if param[0] == ALIVE and param[1] == self.iam:
            self.simulation = bool(int(param[2]))   
            
            msg = "%s %s %d" % (CMD_INIT2_DONE, "all", self.simulation)
            self.producer[DCS].send_message(self.dt_dcs_q, msg)
    
                 


    #-------------------------------
    # dt -> sub: use hk ex
    def connect_to_server_hk_ex(self):
        # RabbitMQ connect  
        self.producer[HK_SUB] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_sub_ex)      
        self.producer[HK_SUB].connect_to_server()
        self.producer[HK_SUB].define_producer()
    
         
    #-------------------------------
    # sub -> dt: use hk q
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        sub_dt_ex = [self.com_list[i]+'.ex' for i in range(COM_CNT)]
        consumer = [None for _ in range(COM_CNT)]
        for idx in range(COM_CNT):
            consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_dt_ex[idx])      
            consumer[idx].connect_to_server()
            
        consumer[PDU].define_consumer(self.com_list[PDU]+'.q', self.callback_pdu)       
        consumer[LT].define_consumer(self.com_list[LT]+'.q', self.callback_lt)
        consumer[UT].define_consumer(self.com_list[UT]+'.q', self.callback_ut)
        
        for idx in range(COM_CNT):
            th = threading.Thread(target=consumer[idx].start_consumer)
            th.daemon = True
            th.start()
            
        self.producer[HK_SUB].send_message(self.dt_sub_q, HK_REQ_PWR_STS)
                    
    
    #-------------------------------
    # rev <- sub        
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_sub[PDU] = cmd
        
        param = cmd.split()
                
        if param[0] == HK_REQ_COM_STS:
            self.com_status[PDU] = bool(int(param[1])) 
        
        elif param[0] == HK_REQ_PWR_STS:
            for i in range(PDU_IDX):
                self.power_status[i] = param[i+1]
                
        
    def callback_lt(self, ch, method, properties, body):
        cmd = body.decode() 
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        self.param_sub[LT] = cmd
        
        param = cmd.split()       

        if param[0] == HK_REQ_COM_STS:
            self.com_status[LT] = bool(int(param[1]))
        
        elif param[0] == DT_REQ_INITMOTOR:
            if param[1] == "TRY":
                msg = "%s - need to initialize" % param[1]
                self.log.send(self.iam, INFO, msg)  
        
        elif param[0] == DT_REQ_SETLT:
            pass
        
        
    def callback_ut(self, ch, method, properties, body):
        cmd = body.decode()   
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        self.param_sub[UT] = cmd
        
        param = cmd.split()     
        
        if param[0] == HK_REQ_COM_STS:
            self.com_status[UT] = bool(int(param[1]))
        
        elif param[0] == DT_REQ_INITMOTOR:
            if param[1] == "TRY":
                msg = "%s - need to initialize" % param[1]
                self.log.send(self.iam, INFO, msg)

        elif param[0] == DT_REQ_SETUT:
            pass

    
    #-------------------------------
    # dt -> dcs    
    def connect_to_server_dt_ex(self):
        # RabbitMQ connect  
        self.producer[DCS] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_dcs_ex)      
        self.producer[DCS].connect_to_server()
        self.producer[DCS].define_producer()
        
    #-------------------------------
    # dcs -> dt
    def connect_to_server_dcs_q(self):
        # RabbitMQ connect
        dcs_dt_ex = [self.dcs_list[i]+'.ex' for i in range(DCS_CNT)]
        consumer = [None for _ in range(DCS_CNT)]
        for idx in range(DCS_CNT):
            consumer[idx] = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, dcs_dt_ex[idx])
            consumer[idx].connect_to_server()
        
        consumer[SVC].define_consumer(self.dcs_list[SVC]+'.q', self.callback_svc)  
        consumer[H].define_consumer(self.dcs_list[H]+'.q', self.callback_h)
        consumer[K].define_consumer(self.dcs_list[K]+'.q', self.callback_k)   
        
        for idx in range(DCS_CNT):
            th = threading.Thread(target=consumer[idx].start_consumer)
            th.daemon = True
            th.start()
            
    
    #-------------------------------
    # rev <- DCSs
    def callback_svc(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_dcs[SVC] = cmd
        
    
    def callback_h(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_dcs[H] = cmd
        
    
    def callback_k(self, ch, method, properties, body):
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        self.param_dcs[K] = cmd
        
        
    def dcs_status(self, dc_idx, cmd):
        param = cmd.split()
        
        if param[0] == CMD_INIT2_DONE or param[0] == CMD_INITIALIZE2_ICS:
            self.dcs_ready[dc_idx] = True
            self.bt_init_status(dc_idx)

        elif param[0] == CMD_SETFSPARAM_ICS or param[0] == CMD_ACQUIRERAMP_ICS:   
            self.lt_moved = False
            self.ut_moved = False
                     
            self.cur_cnt[dc_idx] += 1
            self.label_prog_sts[dc_idx].setText("Done")
            
            end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
            self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)
                        
            #self.prog_timer[dc_idx].stop()
            self.cur_prog_step[dc_idx] = 100
            self.progressBar[dc_idx].setValue(self.cur_prog_step[dc_idx])           

            #self.elapsed_timer[dc_idx].stop()

            self.measure_T[dc_idx] = float(param[1])
            
            # load data
            self.load_data(dc_idx, param[2])
        
            self.acquiring[dc_idx] = False
            
            if self.cal_mode:
                show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.cal_e_repeat[self.cal_cur].text())
                self.label_cur_num[dc_idx].setText(show_cur_cnt)

                if self.cal_stop_clicked:
                    self.cur_cnt[dc_idx] = 0
                    self.bt_run.setText("RUN")
                    self.QWidgetBtnColor(self.bt_run, "black", "white")
                    self.cal_stop_clicked = False 
                                
                elif self.cur_cnt[dc_idx] < int(self.cal_e_repeat[self.cal_cur].text()):
                    self.continuous = True
                    self.bt_take_image.click()
                
                else:
                    self.cur_cnt[dc_idx] = 0
                    self.bt_run.setText("RUN")
                    self.QWidgetBtnColor(self.bt_run, "black", "white")
                    self.cal_stop_clicked = False                   
            
                    if not self.acquiring[H] and not self.acquiring[K]:
                        self.func_lamp(self.cal_cur, OFF)
                        self.cal_cur += 1
                        self.cal_run_cycle()
                
            else:
                show_cur_cnt = "%d / %s" % (self.cur_cnt[dc_idx], self.e_repeat[dc_idx].text())
                self.label_cur_num[dc_idx].setText(show_cur_cnt)
                
                if self.stop_clicked:
                    self.cur_cnt[dc_idx] = 0
                    self.protect_btn(True) 
                    self.bt_take_image.setText("Continuous")
                    
                    self.QWidgetBtnColor(self.bt_take_image, "black", "white")
                    self.stop_clicked = False
                    self.enable_dcs(dc_idx, True)

                elif self.cur_cnt[dc_idx] < int(self.e_repeat[dc_idx].text()):
                    self.continuous = True
                    self.bt_take_image.click()
                
                else:
                    self.cur_cnt[dc_idx] = 0
                    self.protect_btn(True) 
                                            
                    if self.mode == CONT_MODE:
                        self.bt_take_image.setText("Continuous")
                    else:
                        self.bt_take_image.setText("Take Image")
                        
                    self.QWidgetBtnColor(self.bt_take_image, "black", "white")
                    self.stop_clicked = False
                    self.enable_dcs(dc_idx, True)

        elif param[0] == CMD_STOPACQUISITION:
            
            end_time = ti.strftime("%Y-%m-%d %H:%M:%S", ti.localtime())
            self.label_prog_time[dc_idx].setText(self.label_prog_time[dc_idx].text() + " / " + end_time)
                        
            self.protect_btn(True)                    
            self.bt_take_image.setText("Take Image")  
            self.QWidgetBtnColor(self.bt_take_image, "black", "white")
            self.stop_clicked = False  
            self.enable_dcs(dc_idx, True)
        
        
    #-------------------------------
    # dcs command
    def initialize2(self, dc_idx):        
        self.dcs_ready[dc_idx] = False
        self.QWidgetBtnColor(self.bt_init[dc_idx], "yellow", "blue")
        msg = "%s %s %d" % (CMD_INITIALIZE2_ICS, self.dcs_list[dc_idx], self.simulation)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)
            
        
    def set_fs_param(self, dc_idx):     
        if not self.dcs_ready[dc_idx]:
            return

        self.enable_dcs(dc_idx, False)
        
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
        self.elapsed_timer[dc_idx].setInterval(0.001)
        self.elapsed_timer[dc_idx].timeout.connect(lambda: self.show_elapsed(dc_idx))

        self.elapsed[dc_idx] = ti.time()
        self.label_prog_elapsed[dc_idx].setText("0.0")    
        self.elapsed_timer[dc_idx].start()

        if self.cur_cnt[dc_idx] == 0:
            msg = "%s %s %d %.3f 1 %d 1 %.3f 1" % (CMD_SETFSPARAM_ICS, self.dcs_list[dc_idx], self.simulation, _exptime, _FS_number, _fowlerTime)
        else:
            msg = "%s %s %d" % (CMD_ACQUIRERAMP_ICS, self.dcs_list[dc_idx], self.simulation)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)


        self.acquiring[dc_idx] = True        

        
    def stop_acquistion(self, dc_idx):        
        if self.cur_prog_step[dc_idx] > 0:
            self.prog_timer[dc_idx].stop()
            self.elapsed_timer[dc_idx].stop()
                
        msg = "%s %s %d" % (CMD_STOPACQUISITION, self.dcs_list[dc_idx], self.simulation)
        self.producer[DCS].send_message(self.dt_dcs_q, msg)
    
        
    
    def load_data(self, dc_idx, folder_name):
        
        self.label_prog_sts[dc_idx].setText("Transfer")
        
        try:
            filepath = ""
            if self.simulation:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/Demo/SDCS_demo.fits" % WORKING_DIR
                elif dc_idx == H:
                    filepath = "%sIGRINS/Demo/SDCH_demo.fits" % WORKING_DIR
                elif dc_idx == K:
                    filepath = "%sIGRINS/Demo/SDCK_demo.fits" % WORKING_DIR
            else:
                if dc_idx == SVC:
                    filepath = "%sIGRINS/dcss/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
                elif dc_idx == H:
                    filepath = "%sIGRINS/dcsh/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
                elif dc_idx == K:
                    filepath = "%sIGRINS/dcsk/Fowler/%s/Result/FowlerResult.fits" % (WORKING_DIR, folder_name)
            
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
                
            if self.chk_autosave[dc_idx].isChecked():
                self.save_fits(dc_idx)
            
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
                        
            
    def enable_dcs(self, dc_idx, enable):
        self.radio_exptime[dc_idx].setEnabled(enable)
        self.e_exptime[dc_idx].setEnabled(enable)

        self.radio_N_fowler[dc_idx].setEnabled(enable)
        self.e_FS_number[dc_idx].setEnabled(enable)

        self.e_repeat[dc_idx].setEnabled(enable)
        
        self.chk_ds9[dc_idx].setEnabled(enable)
        self.chk_autosave[dc_idx].setEnabled(enable)
        
        self.bt_save[dc_idx].setEnabled(enable)
        self.bt_path[dc_idx].setEnabled(enable)
        
        self.e_path[dc_idx].setEnabled(enable)
        self.e_savefilename[dc_idx].setEnabled(enable)        
        
        if self.radio_exptime[dc_idx].isChecked() and enable:
            self.judge_exp_time(dc_idx)
        elif self.radio_N_fowler[dc_idx].isChecked() and enable:
            self.judge_FS_number(dc_idx)
            
            
    def show_elapsed(self, dc_idx):
        cur_elapsed = ti.time() - self.elapsed[dc_idx]
        if self.measure_T[dc_idx] > 0 and cur_elapsed >= self.measure_T[dc_idx] or (self.mode == SINGLE_MODE and self.stop_clicked):
            self.elapsed_timer[dc_idx].stop()
            return
        
        msg = "%.3f sec" % (ti.time() - self.elapsed[dc_idx])
        self.label_prog_elapsed[dc_idx].setText(msg)


    def show_progressbar(self, dc_idx):
        if self.cur_prog_step[dc_idx] >= 100 or (self.mode == SINGLE_MODE and self.stop_clicked):
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
        self.e_utpos.setEnabled(enable)
        self.bt_utpos_next.setEnabled(enable)
                
        self.bt_utpos_set1.setEnabled(enable)
        self.bt_utpos_set2.setEnabled(enable)
        
    
    def protect_btn_lt(self, enable):
        self.bt_ltpos_prev.setEnabled(enable)
        self.e_ltpos.setEnabled(enable)
        self.bt_ltpos_next.setEnabled(enable)
                
        self.bt_ltpos_set1.setEnabled(enable)
        self.bt_ltpos_set2.setEnabled(enable)
        self.bt_ltpos_set3.setEnabled(enable)
        self.bt_ltpos_set4.setEnabled(enable)
        
    
    def cal_exposure(self):
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.set_fs_param(H)            
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.set_fs_param(K)
                            
        
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
            
        
    def last_seq(self, dc_idx):
        fpath = self.e_path[dc_idx].text()
        
        if fpath[-1] != "/":
            fpath += "/"
            
        sfiles = glob.glob(fpath + "%s_????.fits" % self.dcs_list[dc_idx])
        print(sfiles)
        max_seq = 0
        if sfiles:
            max_seq = int(max(sfiles).split("_")[1][:4])
        else:
            max_seq = 0
            
        return max_seq
    
    
    def new_seq(self, dc_idx):
        return self.last_seq(dc_idx) + 1
                                
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
            self.enable_dcs(K, True)
        
        for idx in range(DCS_CNT):
            self.bt_init_status(idx)
        
        self.enable_dcs(SVC, False)
            
    
    def set_whole_sync(self):
        self.sel_mode = MODE_WHOLE
        for idx in range(DCS_CNT):
            if self.dcs_ready[idx]:
                self.bt_init[idx].setEnabled(True)
                self.enable_dcs(idx, True)
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
            self.QWidgetBtnColor(self.bt_init[idx], "black", "gray")
        
        
    def btn_click(self):
        if self.mode == CONT_MODE:
            if self.continuous:
                self.single_exposure()
                self.continuous = False
            else:
                btn_name = self.bt_take_image.text()
                self.stop_clicked = False
                if btn_name == "Stop":
                    self.stop_clicked = True
                else:
                    self.single_exposure()
        else:
            btn_name = self.bt_take_image.text()
            self.stop_clicked = False
            if btn_name == "Stop":
                self.stop_clicked = True
            elif btn_name == "Abort":
                self.abort_acquisition()
            else:
                self.single_exposure()
            
        
    def single_exposure(self):    
        self.QWidgetBtnColor(self.bt_take_image, "yellow", "blue")
        
        if int(self.e_repeat[SVC].text()) > 1 or int(self.e_repeat[H].text()) > 1 or int(self.e_repeat[K].text()) > 1:
            self.bt_take_image.setText("Stop")
        else:
            self.bt_take_image.setText("Abort")
                    
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_H.isChecked():
            self.set_fs_param(H)            
        if self.radio_HK_sync.isChecked() or self.radio_whole_sync.isChecked() or self.radio_K.isChecked():
            self.set_fs_param(K)
        if self.radio_whole_sync.isChecked() or self.radio_SVC.isChecked():
            self.set_fs_param(SVC)
        
        self.protect_btn(False)
                    
    
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
        
        
    def judge_FS_number(self, dc_idx):
        self.e_exptime[dc_idx].setEnabled(False)
        self.e_FS_number[dc_idx].setEnabled(True)
        
        
    def judge_param(self, dc_idx):
        if self.e_exptime[dc_idx].text() == "" or self.e_FS_number[dc_idx].text() == "":
            return
        
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
        self.QWidgetBtnColor(self.bt_take_image, "black", "white")
        self.stop_clicked = False
        
    
    def save_fits(self, dc_idx):
        
        fpath = "%s" % self.e_path[dc_idx].text()
        self.log.createFolder(fpath)
        
        self.cur_frame[dc_idx] = self.new_seq(dc_idx)
        filename = "%s_%04d.fits" % (self.dcs_list[dc_idx], self.cur_frame[dc_idx])
        self.e_savefilename[dc_idx].setText(filename)
        
        fpath += "/%s" % filename
        fits.writeto(fpath, self.img[dc_idx], self.header[dc_idx], overwrite=True, output_verify="ignore")
    
    
    def open_path(self, dc_idx):
        loader = self.e_path[dc_idx].text()
        folder = QFileDialog.getExistingDirectory(self, "Select Directory", loader)
        if folder:
            self.e_path[dc_idx].setText(folder)
    
    
    def open_calilbration(self):
        
        if self.simulation == NONE_MODE:
            return
        
        if self.chk_open_calibration.isChecked():
            self.setFixedSize(1315, 700)
            self.setGeometry(0, 0, 1315, 700)
            self.show_sub_timer.start()
        else:
            self.setFixedSize(1030, 700)
            self.setGeometry(0, 0, 1030, 700)
            self.show_sub_timer.stop()
            
        if self.power_status[MOTOR] == OFF:
            self.power_onoff(MOTOR, ON)
                
        if self.proc_sub[LT] == None:
            port = self.cfg.get(HK, self.com_list[LT] + "-port")
            cmd = "%sworkspace/ics/HKP/motor.py" % WORKING_DIR
            self.proc_sub[LT] = subprocess.Popen(['python', cmd, self.com_list[LT], port, str(int(self.simulation))])          
        if self.proc_sub[UT] == None:
            port = self.cfg.get(HK, self.com_list[UT] + "-port")
            cmd = "%sworkspace/ics/HKP/motor.py" % WORKING_DIR
            self.proc_sub[UT] = subprocess.Popen(['python', cmd, self.com_list[UT], port, str(int(self.simulation))]) 
        


    #-------------------------------------------------
    # calibration
    def cal_whole_check(self):
        check = self.chk_whole.isChecked()
        
        for i in range(CAL_CNT):
            self.cal_chk[i].setChecked(check)
            
            self.cal_use_parsing(self.cal_chk[i], self.cal_e_exptime[i], self.cal_e_repeat[i])


    def cal_use_parsing(self, chkbox, exptime, repeat):
        use = chkbox.isChecked()
        exptime.setEnabled(use)
        repeat.setEnabled(use)
        
        
    def cal_run(self):
        btn_name = self.bt_run.text()
        self.cal_stop_clicked = False
        if btn_name == "STOP":
            self.cal_stop_clicked = True
            self.cal_mode = False
        elif btn_name == "RUN":
            self.cal_mode = True
            self.cal_cur = 0
            self.bt_run.setText("STOP")
            self.QWidgetBtnColor(self.bt_run, "yellow", "blue")
        
            self.cal_run_cycle()   
        
            
    def cal_run_cycle(self):
        
        cal_cnt = 0
        for cal_cnt in range(self.cal_cur, CAL_CNT):
            if self.cal_chk[cal_cnt].isChecked():
                self.cal_cur = cal_cnt
                self.func_motor(cal_cnt)   #need to check
                if cal_cnt > 0 and self.cal_chk[cal_cnt-1].isChecked:
                    self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt-1], "black")                    
                    self.QWidgetEditColor(self.cal_e_exptime[cal_cnt-1], "black")
                    self.QWidgetEditColor(self.cal_e_repeat[cal_cnt-1], "black")
                self.QWidgetCheckBoxColor(self.cal_chk[cal_cnt], "blue") 
                self.QWidgetEditColor(self.cal_e_exptime[cal_cnt], "blue")
                self.QWidgetEditColor(self.cal_e_repeat[cal_cnt], "blue")
                break
        
        if cal_cnt >= CAL_CNT-1 or self.cal_cur >= CAL_CNT:
            self.bt_run.setText("RUN")
            self.QWidgetBtnColor(self.bt_run, "black", "white")
            self.QWidgetCheckBoxColor(self.cal_chk[self.cal_cur-1], "black") 
            self.QWidgetEditColor(self.cal_e_exptime[self.cal_cur-1], "black")
            self.QWidgetEditColor(self.cal_e_repeat[self.cal_cur-1], "black")
            
            self.cal_mode = False
            
                    
    def power_onoff(self, idx, onoff):
        msg = "%s %d %s" % (HK_REQ_PWR_ONOFF_IDX, idx, onoff)
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg) 


    def func_lamp(self, idx, off=False):  
        if off:
            self.power_onoff(FLAT, OFF)
        else:
            self.power_onoff(FLAT, LAMP_FLAT[idx])
        
        if off:
            self.power_onoff(THAR, OFF)
        else:
            self.power_onoff(THAR, LAMP_FLAT[idx])
                        
            
    def func_motor(self, idx):
        self.ut_moved = False
        self.lt_moved = False
        
        msg = "%s %d %d" % (DT_REQ_MOVEMOTOR, MOTOR_LT_POS[idx], MOTOR_UT_POS[idx])
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
                        
        
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
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
            

    def move_motor_delta(self, motor, direction): #motor-UT/LT, direction-prev, next
        if motor == UT:
            if direction == PREV:
                curpos = int(self.e_utpos.text()) - int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORBACK, self.com_list[motor], curpos)
            else:
                curpos = int(self.e_utpos.text()) + int(self.e_movinginterval.text())
                self.e_utpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORGO, self.com_list[motor], curpos)
                
            self.protect_btn_ut(False)
            
        elif motor == LT:
            if direction == PREV:
                curpos = int(self.e_ltpos.text()) - int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORBACK, self.com_list[motor], curpos)
            else:
                curpos = int(self.e_ltpos.text()) + int(self.e_movinginterval.text())
                self.e_ltpos.setText(str(curpos))
                msg = "%s %s %d" % (DT_REQ_MOTORGO, self.com_list[motor], curpos)
                
            self.protect_btn_lt(False)
                
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
                
    
    def motor_pos_set(self, motor, position): #motor-UT/LT, direction-UT(0/1), LT(0-3)
        if motor == UT:
            msg = "%s %d" % (DT_REQ_SETUT, position)
        elif motor == LT:
            msg = "%s %d" % (DT_REQ_SETLT, position)
            
        self.producer[HK_SUB].send_message(self.dt_sub_q, msg)
    
    
    
    #-------------------------------------
    def sub_data_processing(self):        
        # LT---------------------------------------------------------
        if self.param_sub[LT] != "":
            param = self.param_sub[LT].split()
            
            if param[0] == HK_REQ_COM_STS:
                self.bt_lt_motor_init.setEnabled(self.com_status[LT])
                
            elif param[0] == DT_REQ_INITMOTOR:
                if param[1] == "OK":
                    self.protect_btn_lt(True)
                    self.e_ltpos.setText("0")
                    self.QWidgetBtnColor(self.bt_lt_motor_init, "white", "green")
                    
            elif param[0] == DT_REQ_MOVEMOTOR:
                self.lt_moved = True
                self.e_ltpos.setText(param[1])
                
                if self.ut_moved and self.lt_moved:
                    self.func_lamp(self.cal_cur)
                    ti.sleep(1)
                    
                    self.cal_exposure()
                    
            elif param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                self.protect_btn_lt(True)
                self.e_ltpos.setText(param[1])
                
            self.param_sub[LT] = ""
                    
        # UT---------------------------------------------------------  
        if self.param_sub[UT] != "": 
            param = self.param_sub[UT].split()     
            
            if param[0] == HK_REQ_COM_STS:
                self.bt_ut_motor_init.setEnabled(self.com_status[UT])
                            
            if param[0] == DT_REQ_INITMOTOR:
                if param[1] == "OK":
                    self.protect_btn_ut(True)
                    self.e_utpos.setText("0")                
                    self.QWidgetBtnColor(self.bt_ut_motor_init, "white", "green")
                                
            elif param[0] == DT_REQ_MOVEMOTOR:
                self.ut_moved = True
                self.e_utpos.setText(param[1])
                
                if self.ut_moved and self.lt_moved:
                    self.func_lamp(self.cal_cur)
                    ti.sleep(1)
                    
                    self.cal_exposure()
            
            elif param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                self.protect_btn_ut(True)
                self.e_utpos.setText(param[1])
                
            self.param_sub[UT] = ""
            
            
    def dcs_data_processing(self):
        
        for idx in range(DCS_CNT):
            if self.param_dcs[idx] != "":
                self.dcs_status(idx, self.param_dcs[idx])
                self.param_dcs[idx] = ""           
            
    

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    dt = MainWindow()
    dt.show()
        
    app.exec()