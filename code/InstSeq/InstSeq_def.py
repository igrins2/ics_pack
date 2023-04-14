# -*- coding: utf-8 -*-

"""
Created on Feb 10, 2023

Modified on 

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant

import os

dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

MAIN = "MAIN"
HK = "HK"
DT = "DT"

PDU_IDX = 8
TM_CNT = 8
SUB_CNT = 7
COM_CNT = 6
DCS_CNT = 3

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

SERV_CONNECT_CNT = 3 #Inst.sequencer / SVC / SUB
INST_SEQ = 0
DCSS = 1
HK_SUB = 2

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

OBS_APP = 0 # for InstSeq
DCS = 1 # for InstSeq

T_frame = 1.45479
T_br = 2

# components
TMC1 = 0
TMC2 = 1
TMC3 = 2
TM = 3
VM = 4
PDU = 5
UPLOADER = 6

DEFAULT_VALUE = "-999"

ALM_ERR = "ERROR"
ALM_OK = "GOOD"
ALM_WARN = "WARN"
ALM_FAT = "FATAL"

TMC1_A = 0
TMC1_B = 1
TMC2_A = 2
TMC2_B = 3
TMC3_A = 4
TMC3_B = 5
TM_1 = 6

ON = "on"
OFF = "off"

LOGGING_INTERVAL = 60

HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu

HK_REQ_COM_STS = "ComPortStatus"
HK_REQ_GETVALUE = "GetValue"  #temp_ctrl, tm, vm
HK_REQ_UPLOAD_DB = "UploadDB"   #uploader
HK_REQ_UPLOAD_STS = "UploadDBStatus"    #uploader

CMD_REQ_TEMP = "ReqTempInfo"    #from DCS
CMD_SIMULATION = "Simulation"
SUB_STATUS = "SubStatus"
EXIT = "Exit"
ALIVE = "Alive"
READY = "Ready"
SHOW_TCS_INFO = "ShowTCSInfo"

CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics"
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"
CMD_STOPACQUISITION = "STOPACQUISITION"

CMD_COMPLETED = "Completed"
