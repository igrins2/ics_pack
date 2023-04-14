# -*- coding: utf-8 -*-
"""
Created on Mar 3, 2023

Modified on Mar 6, 2023

@author: hilee

"""

#import os, sys          
#sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HKP.HK_def import *
from HKP.temp_ctrl import *
from HKP.monitor import *
from HKP.pdu import *

import Libs.SetConfig as sc

import subprocess

class Start_Sub(threading.Thread):
    def __init__(self):
        
        self.proc_sub = [None for _ in range(SUB_CNT+2)]
        self.proc_simul = None
                
        self.start()
        
        
    def __del__(self):
        self.exit_sub_system(True)
        
        
    def show_func(self, show):
        if show:
            print("------------------------------------------\n"
                "Command:\n"
                "  show\n"
                "  real\n" 
                "  simul\n"
                "  exit\n"
                "------------------------------------------")
        print("(If you want to show commands, type 'show'!!!)\n")
        print(">>", end=" ")
        return input()


    def show_noargs(self, cmd):
        msg = "'%s' has no arguments. Please use just command." % cmd
        print(msg)
        
        
    def start_sub_system(self, simul='0'):       
        ti.sleep(3)
          
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
            
        comport = []
        com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "lt", "ut", "uploader"]
        for name in com_list:                
            if name != com_list[UPLOADER]:
                comport.append(cfg.get(HK, name + "-port"))
        
        for i in range(len(com_list)):
            if self.proc_sub[i] != None:
                continue
                            
            if 0 <= i <= TMC3:
                cmd = "%sworkspace/ics/HKP/temp_ctrl.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul])
            elif i == TM or i == VM:
                cmd = "%sworkspace/ics/HKP/monitor.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, comport[i], simul])
            elif i == PDU:
                cmd = "%sworkspace/ics/HKP/pdu.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, simul])               
            elif i == LT or i == UT:    
                if bool(int(simul)):
                    cmd = "%sworkspace/ics/HKP/motor.py" % WORKING_DIR
                    self.proc_sub[i] = subprocess.Popen(['python', cmd, com_list[i], comport[i], simul]) 
            elif i == UPLOADER:
                cmd = "%sworkspace/ics/HKP/uploader.py" % WORKING_DIR
                self.proc_sub[i] = subprocess.Popen(['python', cmd, simul]) 

    def exit_sub_system(self, simul=False):
        for i in range(SUB_CNT):
            if self.proc_sub[i] != None:
                if self.proc_sub[i].poll() == None:
                    self.proc_sub[i].kill()
                    self.proc_sub[i] = None
                    
        if simul:
            if self.proc_simul != None:
                    if self.proc_simul.poll() == None:
                        self.proc_simul.kill()
                        self.proc_simul = None


    def start(self):
                    
        print( '================================================\n'+
            '                Ctrl + C to exit or type: exit  \n'+
            '================================================\n')

        args = ""
        args = self.show_func(True)
        
        show = True
        while(show):
            if len(args) < 1:
                args = self.show_func(False)
            
            if len(args.split()) > 1:
                self.show_noargs(args)
            
            if args == "show":
                args = self.show_func(True)
                
            elif args == "real":
                
                self.exit_sub_system(True)                    
                self.start_sub_system()
                
            elif args == "simul":
                
                print("For starting 'simul', com port of current subsystems should be exit.\r\nDo you really want to start 'simul'? (Y/n)")
                if input() == 'n':
                    args = ""
                    continue
                
                self.exit_sub_system()
                            
                if self.proc_simul == None:
                    cmd = "%sworkspace/ics/igos2_simul/run_hk_simulator.py" % WORKING_DIR
                    self.proc_simul = subprocess.Popen(["python", cmd])                                   
                
                self.start_sub_system('1')
                    
            elif args == "exit": 
                show = False    
                
            else:
                print("Please confirm command.")
            
            args = ""
            ti.sleep(1)
  
  
if __name__ == "__main__":
    
    Start_Sub()
