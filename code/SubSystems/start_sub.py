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

import Libs.SetConfig as sc

import subprocess

com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "lt", "ut", "uploader"]
proc_sub = [None for _ in range(len(com_list))]

def start_sub_system():          
    ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
    cfg = sc.LoadConfig(ini_file)
    
    simul = bool(cfg.get(MAIN, "simulation"))
    
    path = WORKING_DIR + "ics_pack/code/SubSystems"
    comport = []
    
    for name in com_list:                
        if name != "uploader":
            comport.append(cfg.get(HK, name + "-port"))
    
    for i in range(len(com_list)-4):                        
        if 0 <= i <= TMC3:
            cmd = "%s/temp_ctrl.py" % path
            proc_sub[i] = subprocess.Popen(['python', cmd, comport[i]])
        elif i == TM or i == VM:
            cmd = "%s/monitor.py" % path
            proc_sub[i] = subprocess.Popen(['python', cmd, comport[i]])

    cmd = "%s/pdu.py" % path
    proc_sub[i] = subprocess.Popen(['python', cmd])               

    cmd = "%s/DB_uploader.py" % path
    proc_sub[i] = subprocess.Popen(['python', cmd]) 
    
    if simul:
        cmd = "%s/motor.py" % path
        proc_sub[i] = subprocess.Popen(['python', cmd, com_list[LT], comport[LT]]) 
    
        cmd = "%s/motor.py" % path
        proc_sub[i] = subprocess.Popen(['python', cmd, com_list[UT], comport[UT]]) 
                
                
def exit_sub_system():
    for i in range(len(com_list)):
        if proc_sub[i] != None:
            if proc_sub[i].poll() == None:
                proc_sub[i].kill()
                proc_sub[i] = None                
                

print( '================================================\n'+
        '                type: "q" to exit  \n'+
        '================================================\n')
    
start_sub_system()

while True:
    if input() == 'q':
        exit_sub_system()
        break