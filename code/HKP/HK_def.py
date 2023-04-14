# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on Dec 15, 2022

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant
SUB_CNT = 9 #whole subsystems

COM_CNT = 6 #hardware without motors
PDU_IDX = 8
TM_CNT = 8
CONTEXT_SETTINGS = dict(help_option_names=["-h", "--help"])

import os

dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
HK = "HK"
DT = "DT"

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

ENG_TOOLS = 0
HK_SUB = 1

#RETRY_CNT = 5
# ---------------------------
# components
TMC1 = 0
TMC2 = 1
TMC3 = 2
TM = 3
VM = 4
PDU = 5
LT = 6
UT = 7
UPLOADER = 8



# ---------------------------
ON = "on"
OFF = "off"

MOTOR_LT = "lt"
MOTOR_UT = "ut"

# ---------------------------
# temperature
TMC1_A = 0
TMC1_B = 1
TMC2_A = 2
TMC2_B = 3
TMC3_A = 4
TMC3_B = 5
TM_1 = 6

DEFAULT_VALUE = "-999"

ALM_ERR = "ERROR"
ALM_OK = "GOOD"
ALM_WARN = "WARN"
ALM_FAT = "FATAL"

LOGGING_INTERVAL = 60

# ---------------------------
# motor
RELATIVE_DELTA_L = 100000
RELATIVE_DETLA_S = 10
VELOCITY_200 = "VT=109226"
VELOCITY_1 = "VT=546"
MOTOR_ERR = 100

HK_REQ_COM_STS = "ComPortStatus"

HK_REQ_GETSETPOINT = "GetSetPoint"  #temp_ctrl

HK_REQ_GETVALUE = "GetValue"  #temp_ctrl, tm, vm

HK_REQ_MANUAL_CMD = "SendManualCommand" #temp_ctrl, tm
HK_REQ_CLI_CMD = "SendCLICommand"   #temp_ctrl, tm, vm, pdu, motor

HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu
HK_REQ_PWR_ONOFF_IDX = "PowerOnOffIndex" #pdu

HK_REQ_UPLOAD_DB = "UploadDB"   #uploader
HK_REQ_UPLOAD_STS = "UploadDBStatus"    #uploader

DT_REQ_INITMOTOR = "InitMotor"  #motor  
DT_REQ_MOVEMOTOR = "MoveMotor"  #motor
DT_REQ_MOTORGO = "MotorGo"      #motor
DT_REQ_MOTORBACK = "MotorBack"  #motor

DT_REQ_SETUT = "SetUT"          #motor
DT_REQ_SETLT = "SetLT"          #motor

CMD_REQ_TEMP = "ReqTempInfo"    #from DCS

HK_STATUS = "HKStatus"
EXIT = "Exit"
ALIVE = "Alive"

