"""
Created on Feb 15, 2023

Modified on Dec 7, 2023

@author: hilee
"""

import os, sys
import threading

import time as ti
import datetime
from distutils.util import strtobool


sys.path.append(os.path.dirname(os.path.abspath(os.path.dirname(__file__))))

from InstSeq_def import *

import svc_process
from add_wcs_header import update_header2

import astropy.io.fits as pyfits
import numpy as np

import Libs.SetConfig as sc
from Libs.MsgMiddleware import *
from Libs.logger import *

import FITSHD_v3 as LFHD

import cppyy, time
giapi_root=os.environ.get("GIAPI_ROOT")
#giapi_root="/home/ics/giapi-glue-cc"
cppyy.add_include_path(f"{giapi_root}/install/include")
cppyy.add_library_path(f"{giapi_root}/install/lib")
cppyy.include("giapi/StatusUtil.h")
cppyy.include("giapi/EpicsStatusHandler.h")
cppyy.include("giapi/GeminiUtil.h")
cppyy.include("giapi/GiapiUtil.h")
cppyy.include("giapi/EpicsStatusHandler.h")
cppyy.include("giapi/GiapiUtil.h")
cppyy.load_library("libgiapi-glue-cc")
cppyy.add_include_path(f"{giapi_root}/src/examples/InstrumentDummyPython")
cppyy.include("InstCmdHandler.h")
cppyy.include("InstStatusHandler.h")

from cppyy.gbl import giapi
from cppyy.gbl import instDummy


giapi.StatusUtil.createStatusItem("ig2:is:currentstatus", giapi.type.Type.INT) 
giapi.StatusUtil.createStatusItem("ig2:sts:rackAmbient:temp", giapi.type.Type.FLOAT) 

i=0
z=10.0
while True:
    i=i+1
    z=z+1
    print (f'Sending {i}')
    giapi.StatusUtil.setValueAsInt("ig2:is:currentstatus", i)   
    giapi.StatusUtil.setValueAsFloat("ig2:sts:rackAmbient:temp", z)   
    giapi.StatusUtil.postStatus()                                               
    time.sleep(1)

