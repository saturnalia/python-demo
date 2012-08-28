#/****************************************************************************
#*
#*     Copyright (c) 2004 Broadcom Corporation
#*           All Rights Reserved
#*
#*     No portions of this material may be reproduced in any form without the
#*     written permission of:
#*
#*           Broadcom Corporation
#*           16215 Alton Parkway
#*           P.O. Box 57013
#*           Irvine, California 92619-7013
#*
#*     All information contained in this document is Broadcom Corporation
#*     company private, proprietary, and trade secret.
#*
#****************************************************************************/


import time 
import string

from ss_api import *

FALSE = 0
TRUE  = 1

BOOL_TRUE =  "1=TRUE"
BOOL_FALSE = "0=FALSE"

VOID = "void"

CAM_SUCCESS = "87=CAM_SUCCESS"

INVALID_CALL ="101=INVALID_CALL" 

# NOTE: We only support one client
CLIENT_ID = 64

# Time Of Day
def tod():
    return time.strftime("%H:%M:%S", time.localtime())

# Show logical value
def showBoolean(value):
    if value == FALSE:
        return 'FALSE'
    return 'TRUE'

# Convert a atring with a optional '=' character to
# integer
def intUntilEqu(str):
    equ = string.find(str,'=')
    if equ == -1:
        value = int(str)
    else:
        value = int(str[:equ])
    return value

# Reset time when system starts
def system_start():
    global time_time_startup 
    time_time_startup = time.time()

def system_start_time():
    global time_time_startup 
    return time_time_startup 

def get_gsm_gmt():
    # timezone not implemented, using gmt
    timeStamp = time.strftime("%Y%m%d%H%M%S", time.gmtime())[2:] + "00"
    return timeStamp