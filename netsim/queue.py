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

from GSM_State import *
import threading
import time

class msg:
    def __init__(self):
        self.id = 0          # ID of message
        self.message = ""    # Asynch messages
        self.time = 0.0      # Time for message 

class queue:
    def __init__(self, state):
        global st
        # Lock for asynchmsg access
        self.lock = threading.Lock()
        # List of asynchronous messages
        self.asynchmsg = []
        st = state

    # Check message queue for messages
    def messages(self):
        self.lock.acquire()
        entries = len(self.asynchmsg)
        self.lock.release()
        return entries
    # Append a message to the end of the queue
    def append_message(self, message, parameters, delay=0.0, id=0):
        self.m = msg()
        self.m.id = id
        self.m.message = "*" + message + "(" + parameters + ")"
        self.m.time = time.time() + delay
        self.lock.acquire()
        self.asynchmsg.append(self.m)
        self.lock.release()
    # Remove a expired message from the start of the queue
    def get_expired_message(self):
        global st
        msg = None
        self.lock.acquire()
        st.maxSleep = 0.1
        entry = 0
        entries = len(self.asynchmsg)
        while entry < entries:
            if self.asynchmsg[entry].time <= time.time():
                msg = self.asynchmsg[entry].message
                del self.asynchmsg[entry]
                break
            # Get the maximum time to sleep before we must
            # check the queue again
            nxtSleep = self.asynchmsg[entry].time - time.time()
            if nxtSleep < st.maxSleep:
                st.maxSleep = nxtSleep
            entry += 1
        self.lock.release()
        return msg
    # Remove a message from the start of the queue
    def get_message_by_id(self, id):
        msg = None
        self.lock.acquire()
        entry = 0
        entries = len(self.asynchmsg)
        while entry < entries:
            if self.asynchmsg[entry].id == id:
                msg = self.asynchmsg[entry].message
                del self.asynchmsg[entry]
                break
            entry += 1
        self.lock.release()
        return msg
