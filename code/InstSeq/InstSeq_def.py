# -*- coding: utf-8 -*-

"""
Created on Feb 10, 2023

Modified on Sep 29, 2023

@author: hilee
"""

# -----------------------------------------------------------
# definition: constant

import os
dir = os.getcwd().split("/")
WORKING_DIR = "/" + dir[1] + "/" + dir[2] + "/"

MAIN = "MAIN"
INST_SEQ = "InstSeq"

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

TEST_MODE = "test"
ACQ_MODE = "acq"
SCI_MODE = "sci"

ACT_TEST = 0
ACT_REBOOT = 1
ACT_INIT = 2
ACT_APPLY = 3
ACT_OBSERVE = 4
ACT_ABORT = 5

T_minFowler = 0.168
T_frame = 1.45479
N_fowler_max = 16

'''
OBS_PREP = "OBS_PREP"
OBS_STARTED_ACQ = "OBS_STARTED_ACQ"
OBS_END_ACQ = "OBS_END_ACQ"
OBS_START_DSET_WRITE = "OBS_START_DSET_WRITE"
OBS_END_DSET_WRITE = "OBS_END_DSET_WRITE"
'''

#EXIT = "Exit"

CMD_INITIALIZE1 = "Initialize1" 
CMD_INIT2_DONE = "Initialize2_Done" # to DCS
CMD_INITIALIZE2_ICS = "Initialize2_ics"
CMD_SETFSPARAM_ICS = "SetFSParam_ics"
CMD_ACQUIRERAMP_ICS = "ACQUIRERAMP_ics"
CMD_STOPACQUISITION = "STOPACQUISITION"
CMD_RESTART = "Restart"

CMD_BUSY = "Busy"

INSTSEQ_SHOW_TCS_INFO = "ShowTCSInfo"

OBSAPP_CAL_OFFSET = "CalOffset"
#OBSAPP_SAVE_SVC = "SaveSVC"

CUR_P_Q_POS = "Current_p_and_q_Position"

#OBSAPP_BUSY = "ObsAppBusy"

#CMD_COMPLETED = "Completed"
