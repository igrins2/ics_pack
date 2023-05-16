# -*- coding: utf-8 -*-

"""
Created on Feb 10, 2023

Modified on Apr 18, 2023

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant

#import os
#dir = os.getcwd().split("/")
#WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
WORKING_DIR = "/home/ics/"

MAIN = "MAIN"

DCS_CNT = 3

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

SINGLE_MODE = 0
CONT_MODE = 1
GUIDE_MODE = 2

SVC = 0
H_K = 1
ALL = 2

H = 1
K = 2

IMG_SVC = 0
IMG_EXPAND = 1
IMG_FITTING = 2
IMG_PROFILE = 3

T_frame = 1.45479
T_br = 2


HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu

HK_REQ_COM_STS = "ComPortStatus"
HK_REQ_GETVALUE = "GetValue"  #temp_ctrl, tm, vm

CMD_REQ_TEMP = "ReqTempInfo"    #from DCS
CMD_SIMULATION = "Simulation"
SUB_STATUS = "SubStatus"
EXIT = "Exit"

CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics"
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"
CMD_STOPACQUISITION = "STOPACQUISITION"

SHOW_TCS_INFO = "ShowTCSInfo"

#CMD_COMPLETED = "Completed"
