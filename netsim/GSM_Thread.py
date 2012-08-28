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


# System modules
import threading
import string
import time
import random
import sys
import os

# Extracted Broadcom enums
from mstypes    import *
from taskmsgs   import *

# Spark extra 

from common    import *

# 
# GSM Activity simulator
# 
class GsmThread(threading.Thread):
        
    def __init__(self, state, queue, g):
        global st, q, gui
        st = state    # State
        q = queue
        gui = g
        self._stopevent = threading.Event()
        # Run each second
        self._sleepperiod = 1.0
        self.startSec = int(time.time())
        threading.Thread.__init__(self, name="GsmThread")

    def handle_periodic_events(self):
        global gui
        # Send only if enabled in GUI
        sec = int(time.time()) - self.startSec

        ############################################################
        # Every 30 seconds, send RX Level messages
        if gui.varSendRSSI.get() and (sec % 10) == 0:
             # Signal quality monitoring and BERT
             result = "%d=L,%d=SQ" % (gui.varSignallevel.get(), random.randint(1, 7))
             q.append_message(MSG_RSSI_IND, result)

        #######################################################
        # Every 45 seconds send battery level
#        if st.Battmgr_Active and gui.varSendBATTLEV.get() and (sec % 45) == 0:
#            result = "%d=L,%d=ADC_AVG,5=LVLS" % (gui.varBattlevel.get(), random.randint(0, 0xFFFF))
#            q.append_message(MSG_BATTMGR_LEVEL, result)

        #####################################
        # Every 2 seconds send MSG_MEASURE_REPORT_PARAM_IND
        # The values sent are mostly guesses
        if st.getFieldTest():
            if (sec % 2) == 0:
                result = "%d=band,%d=arcfn,%d=ms_txpwr,%d=rx_acc_min,%d=cbq,%d=cba,%d=c2_valid,%d=cr_offset" % (
                    0,                    # 0: GSM, 1:DCS, 2:PCS, 3:850, 255:INVALID_BAND
                    random.randint(1,10), # arcfn
                    random.randint(1,10), # ms_txpwr
                    random.randint(1,10), #
                    random.randint(1,10), #
                    random.randint(1,10), #
                    random.randint(1,10), #
                    random.randint(1,10)
                    )
                q.append_message(MSG_MEASURE_REPORT_PARAM_IND, result)

        #####################################
        # Update charger status
#        if st.Charger_Inserted != gui.varChargerInserted.get():
#            result = ""
#            if gui.varChargerInserted.get():
#                q.append_message(MSG_BATTMGR_CHARGING, result)
#            else:
#                q.append_message(MSG_BATTMGR_NOT_CHARGING, result)
#            st.Charger_Inserted = gui.varChargerInserted.get()

    def run(self):
        global st, gui
        print "%s starts" % (self.getName(),)

        while 1:
            # Wait until PIN OK
            while not st.PIN_OK():
               self._stopevent.wait(self._sleepperiod)

            st.startTime = time.time()

            # SIM Application Toolkit
            if gui.varSatkEnabled.get():
                # Telenor ?
                if gui.varOperator.get() == 1:
                    result = "%s,%d,%d,[%s,%s]" % (
                        '"Telenor"',        # Title
                        0,                  # Title icon
                        2,                  # Number of entries
                        '"MobilHandel"',    # First menu item
                        '"Flere tjenester"')
                # Netcom ?
                elif gui.varOperator.get() == 2:
                    result = "%s,%d,%d,[%s,%s,%s,%s,%s]" % (
                        '"NetCom Extra"',   # Title
                        0,                  # Title icon
                        5,                  # Number of entries
                        '"SMSinfo"',        # First menu item
                        '"Friends SMS"',    # ...                 
                        '"NetRefill"',
                        '"Favoritter"',
                        '"Prisinfo"')
                else:
                    #                   1  2  3  4  5  6  7  8  9  10 11
                    result = "%s,%d,%d,[%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s]" % (
                        '"SATK Test"',      # Title
                        0,                  # Title icon
                        11,                 # Number of entries
                        '"SELECT\x11ITEM"',
                        '"DISPLAY\x11TEXT"',
                        '"GET\x11INKEY"',
                        '"GET\x11INPUT"',
                        '"PLAY\x11TONE"',
                        '"SEND\x11SS"',
                        '"SEND\x11USSD"',
                        '"SETUP\x11CALL"',
                        '"REFRESH"',
                        '"SEND\x11SHORT\x11MSG"',
                        '"SESSION_END"')
                q.append_message(MSG_SATK_EVENT_SETUP_MENU, result, 2.0)
            #
            # Replay keypad ?
#            if gui.varReplayKeypad.get() and os.access("kp.log", os.R_OK):
#                    fp = open("kp.log","r")
#                    while 1:
#                        s = fp.readline()
#                        # EOF ?
#                        if s == '':
#                            break
#                        w = string.split(s)
#                        q.append_message(w[0], w[1], float(w[2]))
            # Until API client terminates
            st.sim_state = TRUE
            while st.sim_state:
                # Queue empty ?
                if q.messages() == 0:
                    self.handle_periodic_events()
                    #***************######################
                    # Network release of current call ?
                    if st.Release_Call == TRUE and st.activeCallIndex():
                        st.Release_Call = FALSE
                        result = "%d,%s" % (st.ci, MNCAUSE_TEMPORARY_FAILURE)
                        q.append_message(MSG_VOICECALL_RELEASE_IND, result)
                # Wait
                self._stopevent.wait(self._sleepperiod)
            print "%s restarts" % (self.getName(),)

    def join(self,timeout=None):
        sys.exit()

