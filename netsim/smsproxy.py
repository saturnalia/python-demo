#/****************************************************************************
#*
#*     Copyright (c) 2004-2006 Broadcom Corporation
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
import threading

from socketServer import *
from smsutil  import *
from sim_brcm import *
from sms_storage import *
from taskmsgs import *
from string import *
from common import *

# Socket error code for 'Resource temporarily unavailable'
EAGAIN = 11

# Set to 1 if you want debug messages from the socketServer
SOCKETDEBUG = 0
# You can set this to 0 if you like
BLOCKING = 1

class SmsProxy( threading.Thread ):
    def __init__(self, queue, state, sms, port):
        global q, st, smsdb, proxy_port
        q = queue
        st = state
        smsdb = sms
        proxy_port = port
        threading.Thread.__init__(self, name="SmsServer")

    def run( self ):
        print tod(), "SMS Proxy Started...."

        # Need a delay event
        ev = threading.Event()

        # create a socket server

        srv = SocketServer('', proxy_port, SOCKETDEBUG, BLOCKING)

        while 1:

            print tod(), "SMS Proxy listening on port %d" % proxy_port
            srv.Listen()
            print tod(), "SMS Proxy Connected....."

            while 1:
                pdu = srv.Receive()
                if srv.ConnectionResetByPeer():
                   print "SMS Client Disconnected...."
                   break

                if pdu is not None:
                    # Got a PDU (as opposed to a socket error)
                    if len(pdu) > 0:
                        print tod(), "SMS Proxy received PDU, length %d" % len(pdu)
                        # extract PDU, TON, SMSC from the message
                        # assumes the following format:
                        # "xxxxxxxxxx",yyy,"zzzzzzzzzz"
                        # where xxxx is the raw PDU in hex
                        #       yyy  is the Type of number in decimal
                        #       zzzz is the Service Center Number in ASCII
                        c=string.find(pdu,',')
                        msg = pdu[0:c]
                        c=string.rfind(pdu,',')
                        smsc = pdu[c+1:]
                        # compose a SMS DELIVER message and send it
                        result = '%s,%s,%s,%s' % (SMS_DELIVER, SIMACCESS_SUCCESS, msg, smsc)
                        q.append_message(MSG_SMSPP_DELIVER_IND, result)
                    else:
                        # zero length PDU, so we are done
                        print tod(), "SMS Proxy disconnecting..."
                        break
                else:
                    # Receive() returned None, so check the error
                    errorCode = srv.GetLastError()
                    if not BLOCKING:
                        if errorCode is not EAGAIN:
                            # not EAGAIN, so assume an error
                            print tod(), "SMS Proxy got socket errorCode %d, disconnecting..." % errorCode
                            break
                    else:
                        # assume we are done
                        print tod(), "SMS Proxy got socket errorCode %d, disconnecting..." % errorCode
                        break
