# -*- coding: utf-8 -*-

"""
Created on Feb 10, 2023

Modified on Jan 4, 2024

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

MAIN = "MAIN"
INST_SEQ = "InstSeq"
SC = "SC"

DCS_CNT = 3

# LOG option
DEBUG = "DEBUG"
INFO = "INFO"
WARNING = "WARNING"
ERROR = "ERROR"

SVC = 0
H = 1
K = 2

START = 0
END = 1

IS_STS_OBSTIME = "ig2:is:obstime"
IS_STS_CURRENT = "ig2:is:currentstatus"
IS_STS_TIMEPROG = "ig2:is:timeprogress"

IDLE = "IDLE"
EXPOSING = "EXPOSING"
FOWLER_BACK = "FOWLER_BACK"
CREATE_MEF = "CREATING MEF"

TEST_MODE = "test"
ACQ_MODE = "acq"
SCI_MODE = "sci"

ACT_TEST = 0
ACT_REBOOT = 1
ACT_INIT = 2
ACT_APPLY = 3
ACT_OBSERVE = 4
ACT_ABORT = 5

T_br = 2
T_minFowler = 0.168
T_frame = 1.45479
N_fowler_max = 16
#T_readout = {1:0.5, 2:2, 4:3.5, 8:4.5, 16:6.5}
T_readout = {1:0.5, 2:1.5, 4:2.5, 8:3, 16:4}
T_fowler_cal = {1:0.586, 2:0.939, 4:1.595, 8:3.1364, 16:6.2142}

#EXIT = "Exit"
HK_REQ_PWR_ONOFF = "PowerOnOff" #pdu

CMD_INITIALIZE1 = "Initialize1" 
CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics"
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"
CMD_STOPACQUISITION = "STOPACQUISITION"
CMD_RESTART = "Restart"

INSTSEQ_TCS_INFO_PA = "TCSInfoPA"
INSTSEQ_PQ = "OffsetPQ"
DAYCAL_MODE = "dayCal"

OBSAPP_CAL_OFFSET = "CalOffset"
OBSAPP_OUTOF_NUMBER_SVC = "Out_of_Number_SVC"
OBSAPP_TAKING_IMG = "StartTakingImage"

MOVEPOS_P_Q = "Current_p_and_q_Position"

#OBSAPP_BUSY = "ObsAppBusy"

#CMD_COMPLETED = "Completed"
