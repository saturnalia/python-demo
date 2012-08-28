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


import sys
import getopt
import string
import asynchEvents

from socketServer import *
from broadcomapi  import *
from sim_def   import *
from sim_api   import *
from capi2_ss_ds   import *
from GSM_Thread   import *
from queue import *
from smsproxy import *
from mmsproxy import *
from WapPushUDP import *

def green():
    return "\x1B[1;32m"

def yellow():
    return "\x1B[1;33m"

def bright():
    return "\x1B[1;1m"

def normal():
    return "\x1B[0;0m"

def usage():
    print 'phoneserver '
    print ' -h | --help  # Disable GUI window'
    print ' -n | --nogui # Disable GUI window'

#########################
# Phoneserver entry
try:                                
    opts, args = getopt.getopt(sys.argv, "hn", ["help", "nogui"] ) 
except getopt.GetoptError:           
    usage()                          
    sys.exit(2)    

nogui = FALSE

for opt, arg in opts: 
    if opt in ("-h", "--help"):
        usage()                     
        sys.exit()       
    elif opt in ("-n", "--nogui"):
        print 'Disabling GUI'
        nogui = TRUE

# BUG: should obtain this from port.h (or something)
SMSPROXY_PORT       = 1665
WAP_PUSH_PROXY_PORT = 2948
MMSPROXY_PORT       = 1664
PHONESERVER_PORT    = 1666
DEBUG_PORT          = 1667

# Want messages from the SocketServer ?
SOCKETDEBUG = 0

BLOCKING = 1
NONBLOCKING = 0

# Create SMS storage
smsdb = SmsStorage()

# Global Broadcom API state
st = GSM_State()

# Make the asynch event queue
q = queue(st)

# Create SMS Proxy
sproxy = SmsProxy(q, st, smsdb, SMSPROXY_PORT)

# Create WAP Push Proxy (UDP)
wapPushProxy = WapPushUDP(q, WAP_PUSH_PROXY_PORT)

# The Graphic User Interface
gui = GUI(st, q, smsdb, Revision)
# Connect the GUI to the state
st.setGUI(gui)

# Create SMS Proxy
mmsproxy = MmsProxy(q, MMSPROXY_PORT, gui)

# Let the API have the state, GUI and queue
broadcomApiInit(st, gui, q, smsdb )

# Create GSM Activity thread
thr = GsmThread(st, q, gui)
# Need a delay event
ev = threading.Event()
# Create TCP server
srv = SocketServer('', PHONESERVER_PORT, SOCKETDEBUG, NONBLOCKING) 

print "+---------------------------------------------------------------"
print "| Broadcom GSM/GPRS/WEDGE API Simulator "
print "| API = TCP/IP port %d" % PHONESERVER_PORT
print "+---------------------------------------------------------------"

# Start the TCP servers
thr.start()
# and the GUI
gui.start()
# and SMS Proxy
sproxy.start()
# and MMS Proxy
mmsproxy.start()
# and WAP Push Proxy
wapPushProxy.start()

while 1:
    # Reset to initial state, run constructor again
    st.__init__()
    # Flush queue
    q.__init__(st)
    # Update GUI
    gui.update_sim()
    for ci in range(len(st.cc)):
        gui.update_cc(ci)

    # Wait for connect...
    srv.Listen()
    # Connected

    # Note system start time:
    system_start()

    st.active = TRUE

    while 1:
        # Any Asynch messages in queue ?
        while 1:
            message = q.get_expired_message()
            if message == None:
                break
            print tod(), "=>Event :%s" % bright(), message, normal()
            asynchEvents.handleEvent(st, message)
            srv.Send(message + "\n")

        # Get command from client
        command = srv.Receive()
        # Have been disconnected ?
        if srv.ConnectionResetByPeer() or command == "":
            print "API Client disconnected..."
            # Wait for new connect
            break
        if command != None:
            # Not 'Echo' comand ?
            if command[:1] != '>':
                # Split command into function and parameters
                open  = string.find(command, "(")
                close = string.find(command, ")")
                func = command[:open]
                para = string.split(command[open+1:close], ',')
                print tod(), "Command :%s" % green(), command[:close+1] , normal()
                srv.Send(callApiFunc(func, para))
            else:
                message = "*%s" % command[1:]
                print tod(), "=>Event :%s" % bright(), message, normal()
                srv.Send(message)
        else:
            ev.wait(st.maxSleep) # Max 100 ms

sys.exit()

