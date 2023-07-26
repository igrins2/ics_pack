# -*- coding: utf-8 -*-
"""
Created on Sep 17, 2021

Modified on Apr 18, 2023

@author: hilee

1. cli - ok
2. unit test - ok
3. communicate with components: multi thread, Async, non-blocking
4. communicate with other packages: DTP, GMP, ICS
5. GUI - ok
6. firebase

"""

import os, sys          
sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from HK_def import *

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *

import threading
import subprocess
class HK_cli(threading.Thread):
    def __init__(self):
        
        # load ini file
        ini_file = WORKING_DIR + "IGRINS/Config/IGRINS.ini"
        cfg = sc.LoadConfig(ini_file)
            
        self.ics_ip_addr = cfg.get(MAIN, "ip_addr")
        self.ics_id = cfg.get(MAIN, "id")
        self.ics_pwd = cfg.get(MAIN, "pwd")
        
        self.hk_ex = cfg.get(MAIN, "hk_exchange")     
        self.hk_q = cfg.get(MAIN, "hk_routing_key")
        
        self.com_list = ["tmc1", "tmc2", "tmc3", "tm", "vm", "pdu", "lt", 'ut']
        
        self.producer = None
        self.consumer = [None for _ in range(COM_CNT+2)]
        
        self.proc_motor = [None, None]  
        cmd = "%sics_pack/code/SubSystems/motor.py" % WORKING_DIR
        if self.proc_motor[LT-6] == None:
            self.proc_motor[LT-6] = subprocess.Popen(['python', cmd, self.com_list[LT]])          
        if self.proc_motor[UT-6] == None:
            self.proc_motor[UT-6] = subprocess.Popen(['python', cmd, self.com_list[UT]])
        
        
    def __del__(self):
        
        for i in range(2):
            if self.proc_motor[i] != None:
                self.proc_motor[i].terminate()
                print(self.proc_motor[i].pid, "exit")
        
        for th in threading.enumerate():
            print(th.name + " exit.")     
            
        
        if self.producer != None:
            self.producer.__del__()    
            self.producer = None
        
        for idx in range(COM_CNT+2):
            self.consumer[idx] = None
        

    #-------------------------------
    # hk cli publisher
    def connect_to_server_ex(self):
            
        # RabbitMQ connect  
        self.producer = MsgMiddleware(HK, self.ics_ip_addr, self.ics_id, self.ics_pwd, self.hk_ex)      
        self.producer.connect_to_server()
        self.producer.define_producer()
        


    #-------------------------------
    # sub queue
    def connect_to_server_sub_q(self):
        # RabbitMQ connect
        sub_hk_ex = [self.com_list[i]+'.ex' for i in range(COM_CNT+2)]
        for idx in range(COM_CNT+2):
            self.consumer[idx] = MsgMiddleware(HK, self.ics_ip_addr, self.ics_id, self.ics_pwd, sub_hk_ex[idx])      
            self.consumer[idx].connect_to_server()
            
        self.consumer[TMC1].define_consumer(self.com_list[TMC1]+'.q', self.callback_tmc1)       
        self.consumer[TMC2].define_consumer(self.com_list[TMC2]+'.q', self.callback_tmc2)
        self.consumer[TMC3].define_consumer(self.com_list[TMC3]+'.q', self.callback_tmc3)
        self.consumer[TM].define_consumer(self.com_list[TM]+'.q', self.callback_tm)
        self.consumer[VM].define_consumer(self.com_list[VM]+'.q', self.callback_vm)
        self.consumer[PDU].define_consumer(self.com_list[PDU]+'.q', self.callback_pdu)
        self.consumer[LT].define_consumer(self.com_list[LT-1]+'.q', self.callback_lt)
        self.consumer[UT].define_consumer(self.com_list[UT-1]+'.q', self.callback_ut)
        
        for idx in range(COM_CNT+2):
            th = threading.Thread(target=self.consumer[idx].start_consumer)
            th.daemon = True
            th.start()
                
                 
    def callback_tmc1(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_MANUAL_CMD:
            print('[TC1]', param[1])      
            
            
    def callback_tmc2(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_MANUAL_CMD:
            print('[TC2]', param[1])
            
        
    def callback_tmc3(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_MANUAL_CMD:
            print('[TC3]', param[1])
                    

    def callback_tm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_MANUAL_CMD:
            print('[TM]', param[1])
                

    def callback_vm(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        if param[0] == HK_REQ_MANUAL_CMD:
            print('[VM]', param[1])
            
            
    def callback_pdu(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        try:
            if param[0] == HK_REQ_PWR_STS:
                pwr_sts = ""
                if param[1] == None:    return
                    
                for i in range(PDU_IDX):
                    pwr_sts += param[i+1] + " "
                print('[PDU]', pwr_sts)
        
        except:
            self.log.send(self.iam, WARNING, "parsing error")
            
                
    def callback_lt(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        try:
            if param[0] == DT_REQ_INITMOTOR:
                print('[lt]', "init OK")           
                
            elif param[0] == DT_REQ_MOVEMOTOR or param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                print('[lt]', "moved:", param[1])    
                
            elif param[0] == DT_REQ_SETLT:
                print('[lt]', "save OK")
                
        except:
            self.log.send(self.iam, WARNING, "parsing error")
                
                
    def callback_ut(self, ch, method, properties, body):
        cmd = body.decode()
        param = cmd.split()
        
        try:
            if param[0] == DT_REQ_INITMOTOR:
                print('[ut]', "init OK")             
                
            elif param[0] == DT_REQ_MOVEMOTOR or param[0] == DT_REQ_MOTORGO or param[0] == DT_REQ_MOTORBACK:
                print('[ut]', "moved:", param[1])
            
            elif param[0] == DT_REQ_SETUT:
                print('[ut]', "save OK")
        
        except:
            self.log.send(self.iam, WARNING, "parsing error")
               

    def show_func(self, show):
        if show:
            print("------------------------------------------\n"
                "Usage: Command [Options] [Args]...\n\n"
                "Options:\n"
                "  -h, --help  Show this message and exit.\n\n"
                "Command:\n"
                "  show\n"  
                "  getsetpoint index port\n" 
                "  getheatvalue index port\n"
                "  gettempvalue index port\n"
                "  getvacuumvalue\n"
                "  poweronoff index onoff\n"
                "  initmotor motor\n"
                "  motormove motor posnum\n"
                "  motorgo motor delta\n"   
                "  motorback motor delta\n"    
                "  setlt posnum\n"   
                "  setut posnum\n" 
                "  exit\n"
                "------------------------------------------")
        print("(If you want to show commands, type 'show'!!!)\n")
        print(">>", end=" ")
        args = list(input().split())
        return args


    def show_subfunc(self, cmd, *args):
        msg = "Usage: %s [Options] %s\n\n  %s\n\n" % (cmd, args[0], args[1])
        print(msg+"Options:\n" 
                "  -h, --help  Show this message and exit")

    def show_errmsg(self, args):
        print("Please input '%s' or '-h'/'--help'." % args)


    def show_noargs(self, cmd):
        msg = "'%s' has no arguments. Please use just command." % cmd
        print(msg)
     

    def start(self):
        print( '================================================\n'+
            '                Ctrl + C to exit or type: exit  \n'+
            '================================================\n')
                    
        args = self.show_func(True)     
        show = True   
        while(show):
            while len(args) < 1:
                args = self.show_func(False)
            
            #print(args)
            if args[0] == "show":
                args = self.show_func(True)
                    
            if args[0] == "getsetpoint" or args[0] == "getheatvalue":
                _args = "index, port"
                
                try:
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "index:1~3, port:1~2")   
                    elif len(args) != 3:
                        self.show_errmsg(_args)         
                    elif (1 <= int(args[1]) <= 3) is not True:    
                        print("Please input 1~3 for index.")
                    elif (1 <= int(args[2]) <= 2) is not True:
                        print("Please input 1~2 for port.")
                    else:                        
                        if args[0] == "getsetpoint":
                            cmd = "SETP? %s" % args[2]
                            msg = "%s tmc%s %s" % (HK_REQ_MANUAL_CMD, args[1], cmd)
                            self.producer.send_message(self.hk_q, msg)

                        elif args[0] == "getheatvalue":  
                            cmd = "HTR? %s" % args[2]
                            msg = "%s tmc%s %s" % (HK_REQ_MANUAL_CMD, args[1], cmd)
                            self.producer.send_message(self.hk_q, msg)
                except:
                    print("Please input 1~3 for index and 1~2 for port.")
                                        
            elif args[0] == "gettempvalue":
                _args = "index, port"
                
                try:
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "index:1~4, port:A or B(index:1~3)/0~8(index:4)")
                    elif len(args) != 3:
                        self.show_errmsg(_args)  
                    elif (1 <= int(args[1]) <= 4) is not True:    
                        print("Please input 1~4 for index.")
                    else:
                        if 1 <= int(args[1]) <= 3:
                            if (args[2] == "A" or args[2] == "B") is not True:
                                print("Please input 'A' or 'B' for port on index 1~3.")
                            else:                                
                                cmd = "KRDG? %s" % args[2]
                                msg = "%s tmc%s %s" % (HK_REQ_MANUAL_CMD, args[1], cmd)
                                self.producer.send_message(self.hk_q, msg)                              
                        elif args[1] == "4":
                            if (0 <= int(args[2]) <= 8) is not True:
                                print("Please input 0~8 for port on index 4.")
                            else:
                                cmd = "KRDG? %s" % args[2]
                                msg = "%s tm %s" % (HK_REQ_MANUAL_CMD, cmd)
                                self.producer.send_message(self.hk_q, msg)  
                except:
                    print("Please input 'A' or 'B' port for index 1~3 and 0~8 port for index 4.")                                                
                            
            elif args[0] == "getvacuumvalue":
                if len(args) > 1:
                    self.show_noargs(args[0])
                else:
                    msg = "%s vm @253PR3?;FF" % HK_REQ_MANUAL_CMD
                    self.producer.send_message(self.hk_q, msg)
                    
            elif args[0] == "poweronoff":
                _args = "index, onoff"
                
                try:
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "index:0(all)/1(MACIE 5V)/2(VM 24V)/3(Motor 24V)/4(TH lamp 24V)/5(HC lamp 24V), onoff:on/off")
                    elif len(args) != 3:
                        self.show_errmsg(_args)
                    elif (0 <= int(args[1]) <= 8) is not True:
                        print("Please input a number 1~8 or 0(all).")
                    elif (args[2] == "on" or args[2] == "off") is not True:
                        print("Please input 'on' or 'off'.")
                    else:
                        if args[1] == "0":
                            if args[2] == "on":
                                onoff = "on on on on on on on on"
                            else:
                                onoff = "off off off off off off off off"                         
                            msg = "%s %s" % (HK_REQ_PWR_ONOFF, onoff)
                            #print('CLI >> PDU', msg)
                            self.producer.send_message(self.hk_q, msg)
                            ti.sleep(10)
                        else:
                            msg = "%s %s %s" % (HK_REQ_PWR_ONOFF_IDX, args[1], args[2])
                            self.producer.send_message(self.hk_q, msg)
                            ti.sleep(2)
                except:
                    print("Please input a number 1~8 or 0(all) and 'on' or 'off'")
            
            elif args[0] == "initmotor":
                _args = "motor"
                
                try:
                    if len(args) < 1:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "motor:ut/lt")
                    elif len(args) != 2:
                        self.show_errmsg(_args)
                    elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                        self.show_errmsg(_args)
                    else:
                        msg = "%s %s" % (DT_REQ_INITMOTOR, args[1])
                        self.producer.send_message(self.hk_q, msg)
                except:
                    print("Please input 'ut' or 'lt'.")                   
                        
            elif args[0] == "motormove":
                _args = "motor, posnum"
                
                try:
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "motor:ut/lt, posnum:0 or 1(motor:ut)/0-3(motor:lt)")
                    elif len(args) != 3:
                        self.show_errmsg(_args)
                    elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                        self.show_errmsg(_args)
                    elif args[1] == MOTOR_UT and (0 <= int(args[2]) <= 1) is not True:
                        print("Please input a number 0 or 1 for ut.")
                    elif args[1] == MOTOR_LT and (0 <= int(args[2]) <= 3) is not True:
                        print("Please input a number 0~3 for lt.")
                    else:         
                        msg = "%s %s %s" % (DT_REQ_MOVEMOTOR, args[1], args[2])
                        self.producer.send_message(self.hk_q, msg)   
                except:
                    print("Please input a number 0 or 1 for ut and 0~3 for lt.")
            
            elif args[0] == "motorgo" or args[0] == "motorback":
                _args = "motor, delta"   
                
                try:
                    if len(args) < 2:
                        self.show_errmsg(_args) 
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "motor:ut/lt, delta:int")   
                    elif len(args) != 3:
                        self.show_errmsg(_args)     
                    elif (args[1] == MOTOR_UT or args[1] == MOTOR_LT) is not True:
                        self.show_errmsg(_args)
                    elif int(args[2]) < 1:
                        print("Please input a number over the 0 for delta.")
                    else:
                        if args[0] == "motorgo":
                            msg = "%s %s %s" % (DT_REQ_MOTORGO, args[1], args[2])
                            self.producer.send_message(self.hk_q, msg)  
                        elif args[0] == "motorback":
                            msg = "%s %s %s" % (DT_REQ_MOTORBACK, args[1], args[2])
                            self.producer.send_message(self.hk_q, msg)  
                except:
                    print("Please input a number over the 0 for delta.")
            
            elif args[0] == "setut":
                _args = "posnum"    
                
                try:  
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "posnum:0/1")          
                    elif (0 <= int(args[1]) <= 1) is not True:  
                        print("Please input a number 0 or 1 for ut.")
                    else:
                        msg = "%s %s" % (DT_REQ_SETUT, args[1])
                        self.producer.send_message(self.hk_q, msg)
                except:
                    print("Please input a number 0 or 1 for ut.")
            
            elif args[0] == "setlt":
                _args = "posnum" 
            
                try:    
                    if len(args) < 2:
                        self.show_errmsg(_args)
                    elif args[1] == "-h" or args[1] == "--help":
                        self.show_subfunc(args[0], _args, "posnum:0-3")             
                    elif (0 <= int(args[1]) <= 3) is not True:  
                        print("Please input a number 0-3 for lt.")
                    else:
                        msg = "%s %s" % (DT_REQ_SETLT, args[1])
                        self.producer.send_message(self.hk_q, msg)  
                except:
                    print("Please input a number 0-3 for lt.")
                        
                    
            elif args[0] == "exit":
                if len(args) > 1:
                    self.show_noargs(args[0])
                else:        
                    show = False                               
                    break
                
            else:
                print("Please confirm command.")
            
            args = ""
            ti.sleep(0.5)


if __name__ == "__main__":
    
    hk = HK_cli()
    hk.connect_to_server_ex()
    hk.connect_to_server_sub_q()
   
    hk.start()
    
    hk.__del__()
    
