#/****************************************************************************
#*
#*     Copyright (c) 2006 Broadcom Corporation
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
#*
#*   The following module is created for receiving WAP pushed through UDP.
#*   For example: UDP pushes can come from NowSMS or Proteller for MMS.
#*
#*****************************************************************************/


import time
import threading
import socket

from taskmsgs import *
from smsutil  import *
from sim_brcm import *
from common import *
from segment import createSMSSegments

class WapPushUDP( threading.Thread ):
    def __init__(self, queue, port):
        global udp_q, udp_proxy_port
        udp_q = queue
        udp_proxy_port = port
        threading.Thread.__init__(self, name="WapPushUDP")

    def run( self ):
        print tod(), "WAP Push Proxy Started...."

        # Need a delay event
        ev = threading.Event()

        # create a socket server
        # Set the socket parameters
        host = ""
        buf = 1024
        addr = (host,udp_proxy_port)
        # Create socket and bind to address
        UDPSock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        UDPSock.setsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR, UDPSock.getsockopt (socket.SOL_SOCKET, socket.SO_REUSEADDR)|1)
        UDPSock.bind(addr)

        while 1:

            print tod(), "WAP Push listening on UDP port %d" % udp_proxy_port

            while 1:
                data,addr = UDPSock.recvfrom(buf)
                if not data:
                   print "Client has exited!"
                   break
                smsc = 111111
                for segment in createSMSSegments(data, TRUE):
                    # compose a SMS DELIVER Pdu message and send it
                    result = '%s,%s,"%s","%s"' % (SMS_DELIVER, SIMACCESS_SUCCESS, segment, smsc)
                    udp_q.append_message(MSG_SMSPP_DELIVER_IND, result)

