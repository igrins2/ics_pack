# -*- coding: utf-8 -*-

"""
Created on Jun 28, 2022

Modified on Dec 15, 2022

@author: hilee
"""


# -----------------------------------------------------------
# definition: constant

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"
        
MAIN = "MAIN"
DT = "DT"
HK = "HK"

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

ALM_ERR = "ALARM ERROR"
ALM_OK = "ALARM GOOD"
ALM_WARN = "ALARM WARN"
ALM_FAT = "ALARM FATAL"

PDU_IDX = 8

FOWLER_MODE = 3

DCS_CNT = 3
SVC = 0
H = 1
K = 2

SINGLE_MODE = 0
CONT_MODE = 1

MODE_HK = 0
MODE_WHOLE = 1
MODE_SVC = 2
MODE_H = 3
MODE_K = 4

T_frame = 1.45479
T_exp = 1.63
T_minFowler = 0.168
T_br = 2

# for cal motor moving position
COM_CNT = 3
PDU = 0
LT = 1
UT = 2

PREV = 0
NEXT = 1

CAL_CNT = 9

EMPTY = 0
FOLD_MIRROR = 1
MOTOR_UT_POS = [EMPTY, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, FOLD_MIRROR, EMPTY]

EMPTY = 0
DARK_MIRROR = 1
PINHOLE = 2
USAF = 3
MOTOR_LT_POS = [DARK_MIRROR, EMPTY, EMPTY, EMPTY, PINHOLE, PINHOLE, USAF, USAF, EMPTY]

MACIE = 1
MOTOR = 3
FLAT = 4
THAR = 5
ON = "on"
OFF = "off"
LAMP_FLAT = [OFF, ON, OFF, OFF, ON, OFF, ON, OFF, OFF]
LAMP_THAR = [OFF, OFF, OFF, ON, OFF, ON, OFF, OFF, OFF]

MUX_TYPE = 2

FRAME_X = 2048
FRAME_Y = 2048

HK_REQ_COM_STS = "ComPortStatus"

HK_REQ_PWR_STS = "PowerStatus"  #pdu
HK_REQ_PWR_ONOFF_IDX = "PowerOnOffIndex" #pdu

DT_REQ_INITMOTOR = "InitMotor"  #motor  
DT_REQ_MOVEMOTOR = "MoveMotor"  #motor
DT_REQ_MOTORGO = "MotorGo"      #motor
DT_REQ_MOTORBACK = "MotorBack"  #motor

DT_REQ_SETUT = "SetUT"          #motor
DT_REQ_SETLT = "SetLT"          #motor

EXIT = "Exit"
ALIVE = "Alive" # from EngTools

DT_STATUS = "DTStatus"

CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics" 
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"
CMD_STOPACQUISITION = "STOPACQUISITION"


