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


def callbackStatus(t, statusItem):
    #print (f'Recieved the message type is: {t}')
    #if  giapi.type.BOOLEAN == t:
    #    print (f'{statusItem.getDataAsInt(0)}')
    #elif giapi.type.INT == t:
    #    print (f'{statusItem.getDataAsInt(0)}')
    
    if giapi.type.DOUBLE == t:
        pass
        #print (f'{statusItem.getDataAsDouble(0)}')
    elif giapi.type.STRING == t:
        pass
        #print (f'{statusItem.getDataAsString(0)}')
    #elif giapi.type.BYTE == t:
    #    print (f'{statusItem.getDataAsByte(0)}')
    else:
        print (f'Not defined, it is an error')
    

channel = ["ag:port:igrins2", \
        "tcs:sad:instrPA", "tcs:sad:currentRma", \
        "tcs:sad:currentRA", "tcs:sad:currentDec", \
        "tcs:sad:airMass", "tcs:sad:airMassNow", \
        "tcs:sad:currentZd", "tcs:sad:LST", \
        "tcs:sad:currentHAString"]
handler = instDummy.InstStatusHandler.create(callbackStatus)

for i in range(10):
    giapi.GeminiUtil.subscribeEpicsStatus(channel[i], handler)
#giapi.GeminiUtil.subscribeEpicsStatus(channel[0], handler)
#giapi.GeminiUtil.subscribeEpicsStatus(channel[2], handler)
#giapi.GeminiUtil.subscribeEpicsStatus(channel[7], handler)

w_t = 5
pStatus = giapi.GeminiUtil.getChannel("tcs:sad:instrPA", 20)
cur_pa = pStatus.getDataAsDouble(0)
print (f'************* The tcs:sad:instrPA is: {cur_pa}')

while True:
    #print(f'Father sleeping')
    '''
    for i in range(10):
        pStatus =  giapi.GeminiUtil.getChannel(channel[i], 20);
        if i == 0 or i == 3 or i == 4 or i == 8 or i == 9:
            print(f"The {channel[i]} is: {pStatus.getDataAsString(0)}")
        else:
            print (f'The {channel[i]} is: {pStatus.getDataAsDouble(0)}')
    '''
    '''    
    try:
        pStatus =  giapi.GeminiUtil.getChannel(channel[0], 20)
        print(f"The {channel[0]} is: {pStatus.getDataAsString(0)}")
    except:
        print("reading error")
    '''
    

    pStatus =  giapi.GeminiUtil.getChannel(channel[3], 20)
    print (f'The {channel[3]} is: {pStatus.getDataAsString(0)}')
    pStatus2 =  giapi.GeminiUtil.getChannel(channel[4], 20)
    print (f'The {channel[4]} is: {pStatus2.getDataAsString(0)}')
    pStatus =  giapi.GeminiUtil.getChannel(channel[5], 20)
    print (f'The {channel[5]} is: {pStatus.getDataAsDouble(0)}')
    
    time.sleep(w_t)

