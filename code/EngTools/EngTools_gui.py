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


class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.setFixedSize(281, 184)
                    
        self.iam = "EngTools"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, INFO, "start")
        
        self.setupUi(self)
        self.setWindowTitle("EngTools 1.0")
                
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
        
        # 0 - HKP, 1 - DTP
        self.proc = [None, None]
        
        self.producer = None
        self.consumer_hk = None
        self.consumer_dt = None
        
        self.param = ""
                
        self.label_stsHKP.setText("---")
        self.label_stsDTP.setText("---")
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
                    
        self.producer.channel.close()
        self.consumer_hk.channel.close()
        self.consumer_dt.channel.close()
                                                                
        return super().closeEvent(event)
        
        
    def init_events(self):
        self.radio_inst_simul.clicked.connect(self.set_mode)
        self.radio_real.clicked.connect(self.set_mode)
        
        self.bt_runHKP.clicked.connect(self.run_HKP)
        self.bt_runDTP.clicked.connect(self.run_DTP)
        
        
    #-------------------------------
    # publish EngTools
    def connect_to_server_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.EngTools_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
    
         
    #-------------------------------
    # consumer from hk
    def connect_to_server_hk_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.hk_q, self.callback_hk)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
        

    def callback_hk(self, ch, method, properties, body):
        
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_STATUS:
            self.label_stsHKP.setText(param[1])
            self.bt_runHKP.setEnabled(False)
            self.label_stsHKP.setText("STARTED")
            
        elif param[0] == EXIT:                     
            self.proc[HKP] = None
            self.bt_runHKP.setEnabled(True)
            self.label_stsHKP.setText("CLOSED")
                
            if self.bt_runHKP.isEnabled() and self.bt_runDTP.isEnabled():
                self.radio_inst_simul.setEnabled(True)
                self.radio_real.setEnabled(True)  
    
    
    #-------------------------------
    # consumer from dt
    def connect_to_server_dt_q(self):
        # RabbitMQ connect
        consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.dt_ex)      
        consumer.connect_to_server()
        consumer.define_consumer(self.dt_q, self.callback_dt)       
        
        th = threading.Thread(target=consumer.start_consumer)
        th.daemon = True
        th.start()
        

    def callback_dt(self, ch, method, properties, body):
        
        cmd = body.decode()
        msg = "receive: %s" % cmd
        self.log.send(self.iam, INFO, msg)
        param = cmd.split()
        
        if param[0] == HK_STATUS:
            self.label_stsDTP.setText(param[1])                
            self.bt_runDTP.setEnabled(False)
            self.label_stsDTP.setText("STARTED")

        elif param[0] == EXIT:                     
            self.proc[DTP] = None   
            self.bt_runDTP.setEnabled(True)   
            self.label_stsDTP.setText("CLOSED")  
                
            if self.bt_runHKP.isEnabled() and self.bt_runDTP.isEnabled():
                self.radio_inst_simul.setEnabled(True)
                self.radio_real.setEnabled(True)
            
    
    def set_mode(self):                    
        if self.radio_inst_simul.isChecked():
            self.simulation = True
                        
        elif self.radio_real.isChecked():
            self.simulation = False
        
        if self.producer:                               
            msg = "%s %s %d" % (ALIVE, DT, self.simulation)
            self.producer.send_message(self.EngTools_q, msg)  
        
        
    def run_HKP(self):
            
        if self.proc[HKP] == None:
            self.proc[HKP] = subprocess.Popen(['python', WORKING_DIR + 'ics_pack/code/HKP/HK_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)
        
           
    def run_DTP(self):
        
        if self.proc[DTP] == None:
            self.proc[DTP] = subprocess.Popen(['python', WORKING_DIR + 'ics_pack/code/DTP/DT_gui.py'])
        
        self.radio_inst_simul.setEnabled(False)
        self.radio_real.setEnabled(False)
        
        msg = "%s %s %d" % (ALIVE, DT, self.simulation)
        self.producer.send_message(self.EngTools_q, msg)     
        
    

if __name__ == "__main__":
    
    app = QApplication(sys.argv)
        
    ETs = MainWindow()
    ETs.show()
        
    app.exec()
    