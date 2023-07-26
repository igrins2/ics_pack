# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Apr 17, 2023

@author: hilee
"""

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ui_EngTools import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

import subprocess

from Libs.MsgMiddleware import *
from EngTools_def import *

import Libs.SetConfig as sc
from  Libs.logger import *

from distutils.util import strtobool

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(268, 165)
                    
        self.iam = "EngTools"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("EngTools 2.0")
                
        self.init_events()
                    
        # ---------------------------------------------------------------
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        self.cfg = sc.LoadConfig(ini_file)
        
        self.ics_ip_addr = self.cfg.get(MAIN, 'ip_addr')
        self.ics_id = self.cfg.get(MAIN, 'id')
        self.ics_pwd = self.cfg.get(MAIN, 'pwd')
        
        self.EngTools_ex = self.cfg.get(MAIN, 'engtools_exchange')
        self.EngTools_q = self.cfg.get(MAIN, 'engtools_routing_key')
        
        self.hk_ex = self.cfg.get(MAIN, 'hk_exchange')
        self.hk_q = self.cfg.get(MAIN, 'hk_routing_key')
        
        self.dt_ex = self.cfg.get(MAIN, 'dt_exchange')
        self.dt_q = self.cfg.get(MAIN, 'dt_routing_key')
        
        self.simulation = strtobool(self.cfg.get(MAIN, "simulation"))
        
        # 0 - HKP, 1 - DTP
        self.proc = [None, None]
        
        self.producer = None
        self.consumer_hk = None
        self.consumer_dt = None
        
        self.param = ""
                
        self.label_stsHKP.setText("---")
        self.label_stsDTP.setText("---")
        self.radio_real.setChecked(True)
        
        if self.simulation:
            self.radio_inst_simul.setChecked(True)
            self.radio_real.setChecked(False)
        else:
            self.radio_inst_simul.setChecked(False)
            self.radio_real.setChecked(True)
        
        self.connect_to_server_ex()
        self.connect_to_server_hk_q()
        self.connect_to_server_dt_q()
                    
        
    def closeEvent(self, event: QCloseEvent) -> None:
                
        for i in range(2):
            if self.proc[i] != None:
                self.proc[i].terminate()
                self.log.send(self.iam, INFO, str(self.proc[i].pid) + " exit")
                
        for th in threading.enumerate():
            self.log.send(self.iam, INFO, th.name + " exit.")


        if self.producer != None:
            self.producer.__del__()
            self.producer = None
        
        self.consumer_hk = None
        self.consumer_dt = None
                                                                
        return super().closeEvent(event)
        
        
    def init_events(self):
        self.radio_inst_simul.clicked.connect(self.set_mode)
        self.radio_real.clicked.connect(self.set_mode)
        
        self.bt_runHKP.clicked.connect(self.run_HKP)
        self.bt_runDTP.clicked.connect(self.run_DTP)
        
        
    #-------------------------------
    # EngTools publisher
    def connect_to_server_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.EngTools_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.EngTools_q, msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, INFO, msg)
    
         
    #-------------------------------
    # hk queue
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        self.consumer_hk = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_ex)      
        self.consumer_hk.connect_to_server()
        self.consumer_hk.define_consumer(self.hk_q, self.callback_hk)       
        
        th = threading.Thread(target=self.consumer_hk.start_consumer)
        th.daemon = True
        th.start()
        

    def callback_hk(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == HK_STATUS or param[0] == EXIT): return
        
        msg = "<- [HKP] %s" % cmd
        self.log.send(self.iam, INFO, msg)

        try:
            if param[0] == HK_STATUS:
                self.label_stsHKP.setText(param[2])
                self.bt_runHKP.setEnabled(False)
                
            elif param[0] == EXIT:                     
                self.proc[HKP] = None
                self.bt_runHKP.setEnabled(True)
                self.label_stsHKP.setText("CLOSED")
                    
                if self.bt_runHKP.isEnabled() and self.bt_runDTP.isEnabled():
                    self.radio_inst_simul.setEnabled(True)
                    self.radio_real.setEnabled(True)  
        except:
            self.log.send(self.iam, WARNING, "parsing error")


    #-------------------------------
    # dt queue
    def connect_to_server_dt_q(self):
        # RabbitMQ connect
        self.consumer_dt = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_ex)      
        self.consumer_dt.connect_to_server()
        self.consumer_dt.define_consumer(self.dt_q, self.callback_dt)       
        
        th = threading.Thread(target=self.consumer_dt.start_consumer)
        th.daemon = True
        th.start()
        

    def callback_dt(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()

        if not (param[0] == DT_STATUS or param[0] == EXIT): return

        msg = "<- [DTP] %s" % cmd
        self.log.send(self.iam, INFO, msg)
        
        try:
            if param[0] == DT_STATUS:
                self.label_stsDTP.setText(param[2])                
                self.bt_runDTP.setEnabled(False)
                
                msg = "%s %d" % (ALIVE, self.simulation)
                self.publish_to_queue(msg)

            elif param[0] == EXIT:                     
                self.proc[DTP] = None   
                self.bt_runDTP.setEnabled(True)   
                self.label_stsDTP.setText("CLOSED")  
                    
                if self.bt_runHKP.isEnabled() and self.bt_runDTP.isEnabled():
                    self.radio_inst_simul.setEnabled(True)
                    self.radio_real.setEnabled(True)   
        except:
            self.log.send(self.iam, WARNING, "parsing error")    
            
    
    def set_mode(self):                    
        if self.radio_inst_simul.isChecked():
            self.simulation = True
                        
        elif self.radio_real.isChecked():
            self.simulation = False
                
        
    def run_HKP(self):
            
        if self.proc[HKP] == None:
            self.proc[HKP] = subprocess.Popen(['python', WORKING_DIR + 'ics_pack/code/HKP/HK_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)
        self.label_stsHKP.setText("STARTED")
        
           
    def run_DTP(self):
        
        if self.proc[DTP] == None:
            self.proc[DTP] = subprocess.Popen(['python', WORKING_DIR + 'ics_pack/code/DTP/DT_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)  
        self.label_stsDTP.setText("STARTED")      
    

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    ETs = MainWindow()
    ETs.show()
        
    app.exec()
    