# -*- coding: utf-8 -*-
"""
Created on Mar 3, 2023

Modified on Apr 17, 2023

@author: hilee

"""

#import os, sys          
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from SubSystems_def import *
from temp_ctrl import *
from monitor import *
from pdu import *

import subprocess

class SubSystems():
    
    def __init__(self):
        self.com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "uploader"]
        self.proc_sub = [None for _ in range(len(self.com_list))]
        
        self.start_sub_system()
        
        
    def __del__(self):
        self.exit_sub_system()
    
    
    def start_sub_system(self):                  
        path = WORKING_DIR + "ics_pack/code/SubSystems"
        
        for i in range(len(self.com_list)-2):                        
            if 0 <= i <= TMC3:
                cmd = "%s/temp_ctrl.py" % path
                self.proc_sub[i] = subprocess.Popen(['python', cmd, str(i+1)])
            elif i == TM or i == VM:
                cmd = "%s/monitor.py" % path
                self.proc_sub[i] = subprocess.Popen(['python', cmd, str(i+1)])

        cmd = "%s/pdu.py" % path
        self.proc_sub[PDU] = subprocess.Popen(['python', cmd])               

        cmd = "%s/DB_uploader.py" % path
        self.proc_sub[UPLOADER] = subprocess.Popen(['python', cmd]) 
        
    
    def exit_sub_system(self):
        for i in range(len(self.com_list)):
            if self.proc_sub[i] != None:
                if self.proc_sub[i].poll() == None:
                    self.proc_sub[i].kill()
                    self.proc_sub[i] = None   


if __name__ == "__main__":
    
    ss = SubSystems()
    
    #print( '================================================\n'+
    #    '                type: "q" to exit  \n'+
    #    '================================================\n')
    
    while True:
        if ss.proc_sub[TMC1] == None and ss.proc_sub[TMC2] == None and \
            ss.proc_sub[TMC3] == None and ss.proc_sub[TM] == None and \
            ss.proc_sub[VM] == None and ss.proc_sub[PDU] == None and \
            ss.proc_sub[UPLOADER] == None:
            break
        
        
        