# -*- coding: utf-8 -*-

"""
Created on Aug 21, 2022

Modified on , 2023

@author: hilee
"""

import sys, os

sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from ui_gmp import *

from PySide6.QtCore import *
from PySide6.QtGui import *
from PySide6.QtWidgets import *

from Libs.MsgMiddleware import *

import Libs.SetConfig as sc
from  Libs.logger import *

dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

class MainWindow(Ui_Dialog, QMainWindow):
    
    def __init__(self):
        super().__init__()
        
        self.iam = "GMP"
        
        self.log = LOG(WORKING_DIR + "IGRINS", self.iam)  
        self.log.send(self.iam, "INFO", "start")
        
        self.setupUi(self)
        self.setWindowTitle("Virtual GMP")
        
        self.init_events()
        
        # ---------------------------------------------------------------
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
        
        self.ics_ip_addr = cfg.get("MAIN", 'ip_addr')
        self.ics_id = cfg.get("MAIN", 'id')
        self.ics_pwd = cfg.get("MAIN", 'pwd')
        
        self.InstSeq_ex = cfg.get('MAIN', 'instseq_exchange')
        self.InstSeq_q = cfg.get('MAIN', 'instseq_routing_key')
        
        self.action_id = 0
        
        self.e_ActionID.setText(str(self.action_id))
        self.e_expTime.setText("1.63")
        self.radio_acq.setChecked(True)
        self.radio_sci.setChecked(False)     
        
        self.e_port.setText("3")
        self.e_currentRMA.setText("45")
        self.e_positionAngle.setText("90")
        self.e_currentRA.setText("02:13:43.363")
        self.e_currentDec.setText("-29:52:19.16")
        self.e_airMass.setText("1.44")
        self.e_HourAngle.setText("+03:34:16")
        self.e_localSiderealTime.setText("05:48:00")
        self.e_zenithDistance.setText("45.9")
        
        self.producer = None 
        self.consumer = None  
        
        self.connect_to_server_ex()
        self.connect_to_server_InstSeq_q()
        
               
    def closeEvent(self, event: QCloseEvent) -> None:

        for th in threading.enumerate():
            self.log.send(self.iam, "INFO", th.name + " exit.")

        if self.producer != None:
            self.producer.__del__()
            self.producer = None
        
        self.consumer = None
                                                                
        return super().closeEvent(event)
        
        
    def init_events(self):
        self.bt_test.clicked.connect(self.test)
        self.bt_reboot.clicked.connect(self.reboot)
        self.bt_init.clicked.connect(self.init)
        self.bt_apply.clicked.connect(self.apply)
        self.bt_observe.clicked.connect(self.observe)
        self.bt_abort.clicked.connect(self.abort)
        self.bt_send_fromGemini.clicked.connect(self.send)
        
        
    def connect_to_server_ex(self):
        # RabbitMQ connect  
        self.producer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.iam + '.ex')      
        self.producer.connect_to_server()
        self.producer.define_producer()
        
        
    def publish_to_queue(self, msg):
        if self.producer == None:   return
        
        self.producer.send_message(self.iam + '.q', msg)
        
        self.e_send.setText(msg)
        
        msg = "%s ->" % msg
        self.log.send(self.iam, "INFO", msg)
        
        
    def connect_to_server_InstSeq_q(self):
        # RabbitMQ connect
        self.consumer = MsgMiddleware(self.iam, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.InstSeq_ex+'.test')      
        self.consumer.connect_to_server()
        self.consumer.define_consumer(self.InstSeq_q+'.test', self.callback_InstSeq)       
        
        th = threading.Thread(target=self.consumer.start_consumer)
        th.daemon = True
        th.start()
        
        
    def callback_InstSeq(self, ch, method, properties, body):
        cmd = body.decode()

        self.e_recv.setText(cmd)
                
        msg = "<- [InstSeq] %s" % cmd
        self.log.send(self.iam, "INFO", msg)     
        
    
    def seq_cmd(self, seq):
        self.e_recv.setText("")
        
        self.action_id = int(self.e_ActionID.text()) + 1
        msg = "%d %d" % (self.action_id, seq)
        self.publish_to_queue(msg)
        self.e_ActionID.setText(str(self.action_id))
                
    
    def test(self):
        self.seq_cmd(0)
        
    
    def reboot(self):
        self.seq_cmd(1)
    
    
    def init(self):
        self.seq_cmd(2)
    
    
    def apply(self):
        self.e_recv.setText("")
        
        self.action_id = int(self.e_ActionID.text()) + 1
        _expTime = float(self.e_expTime.text())
        if self.radio_acq.isChecked() and not self.radio_sci.isChecked():
            _mode = "acq"
        elif not self.radio_acq.isChecked() and self.radio_sci.isChecked():
            _mode = "sci"
            
        msg = "%d 9 ig2:dcs:expTime=%.2f ig2:seq:state=%s" % (self.action_id, _expTime, _mode)
        self.publish_to_queue(msg)
        self.e_ActionID.setText(str(self.action_id))        
        
    
    def observe(self):
        self.seq_cmd(10)
    
    
    def abort(self):
        self.seq_cmd(16)
        
    
    def send(self):
        port = "ag:port:igrins2=%s" % self.e_port.text()
        rma = "tcs:currentRMA=%s" % self.e_currentRMA.text()
        PA = "tcs:instrPA=%s" % self.e_positionAngle.text()
        RA = "tcs:sad:currentRA=%s" % self.e_currentRA.text()
        Dec = "tcs:sad:currentDec=%s" % self.e_currentDec.text()
        AM = "tcs:sad:airMass=%s" % self.e_airMass.text()
        HA = "tcs:sad:HA=%s" % self.e_HourAngle.text()
        LST = "tcs:sad:LST=%s" % self.e_localSiderealTime.text()
        ZD = "tcs:sad:ZD=%s" % self.e_zenithDistance.text()
        
        msg = "%s %s %s %s %s %s %s %s %s" % (port, rma, PA, RA, Dec, AM, HA, LST, ZD)
        self.publish_to_queue(msg)
    
    
if __name__ == "__main__":

    app = QApplication(sys.argv)
        
    gmp = MainWindow()
    gmp.show()
        
    app.exec()
        
        
    
        
        
    
        