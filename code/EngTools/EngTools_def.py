# -*- coding: utf-8 -*-

"""
Created on Sep 17, 2021

Modified on March 9, 2023

@author: hilee
"""

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


HKP = 0
DTP = 1

MODE_SIMUL = 0
MODE_REAL = 1


HK_STATUS = "HKStatus"
EXIT = "Exit"
ALIVE = "Alive"

