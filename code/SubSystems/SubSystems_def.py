# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Jan 4, 2024

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant
COM_CNT = 6 
PDU_IDX = 8
TM_CNT = 8
DCS_CNT = 3
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os, sys
##dir = os.getcwd().split("/")
#WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
try:
    dir = sys.argv[0].split('/')
    WORKING_DIR = "/home/%s/" % dir[2]
except:
    WORKING_DIR = "/home/ics/"
    
MAIN = "MAIN"
HK = "HK"
SC = "SC"

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

#RETRY_CNT = 5
# ---------------------------
# components
TMC1 = 0
TMC2 = 1
TMC3 = 2
TM = 3
VM = 4
PDU = 5
UPLOADER = 6
# ---------------------------
ON = "on"
OFF = "off"

MOTOR_LT = "lt"
MOTOR_UT = "ut"

DEFAULT_VALUE = "-999"

SVC = 0
H = 1
K = 2

# ---------------------------
# motor
RELATIVE_DELTA_L = 100000
RELATIVE_DETLA_S = 10
VELOCITY_200 = "VT=109226"
VELOCITY_1 = "VT=546"
MOTOR_ERR = 100

# ---------------------------
# health
HEALTH_IG2 = 0
HEALTH_ICS = 1
HEALTH_DCSH = 2
HEALTH_DCSK = 3
HEALTH_DCSS = 4

# ---------------------------
# state
GOOD = 0
STOPPED = 1
DISCON = 2
PWR_OFF = 3
TMP_ERR = 4
TMP_WARN = 5

HK_REQ_COM_STS = "ComPortStatus"

HK_REQ_GETVALUE = "GetValue"  #temp_ctrl, tm, vm

HK_REQ_MANUAL_CMD = "SendManualCommand" #temp_ctrl, tm
HK_REQ_CLI_CMD = "SendCLICommand"   #temp_ctrl, tm, vm, pdu, motor

HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu
HK_REQ_PWR_ONOFF_IDX = "PowerOnOffIndex" #pdu

HK_REQ_UPLOAD_DB = "UploadDB"   #uploader
#HK_REQ_UPLOAD_STS = "UploadDBStatus"    #uploader

DT_REQ_INITMOTOR = "InitMotor"  #motor  
DT_REQ_MOVEMOTOR = "MoveMotor"  #motor
DT_REQ_MOTORGO = "MotorGo"      #motor
DT_REQ_MOTORBACK = "MotorBack"  #motor
DT_REQ_STOP = "StopMotor"       #motor

DT_REQ_SETUT = "SetUT"          #motor
DT_REQ_SETLT = "SetLT"          #motor

UPLOAD_Q = "UploadDBQ"    #uploader
IG2_HEALTH = "IGRINS2Health"    #0-GOOD, 1-WARNING, 2-BAD

INSTSEQ_TCS_INFO_PA = "TCSInfoPA"   #add 20240104
CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics"
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"

HEART_BEAT = "HeartBeat"