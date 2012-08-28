#****************************************************************************
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
#****************************************************************************
#*
#*     Name:              mmsproxy.py
#*
#*     Description:       This file contains the implementation for an MMS
#*                        proxy server.
#*
#*     PDUs implemented:  1. send-req (HTTP header must contain content-length,
#*                           or messages must be chunked).
#*                        2. send-conf (always confirm, no error checking).
#*                        3. m-notification-ind (canned).
#*                        4. notifyresp-ind (only handles "retreived" or
#*                           "deferred"), also assumes a certain pdu format
#*                           from the client.
#*                        5. m-retrieve-conf
#*
#*     Intermediates:     - sendConf.bin
#*                        - temp.bin
#*
#*     Outputs:           - StoredMMS.bin
#*
#*     Limitations:       - Can only 1 handle request at a time
#*                        - not all MMS PDUs/scenarios supported
#*                        - Does not expect user to cancel a transaction
#*                        - Always sends 200 OK
#*
#*     References:        Multimedia Messaging Service: Encapsulation Protocol
#*                        (OMA-MMS-ENC-v1_2-20040323-C.doc)
#*
#*     Author:            calebho
#*
#*
#*     Usage:             Configure the WAP profile to: use HTTP; Use Proxy to Yes
#*                        and change the Proxy IP as well as the MMS Message server 
#*                        to <Your IP>:<MmscPort=1664> (eg http://127.0.0.1:1664)
#*
#*****************************************************************************

import shutil
import os
import time
import binascii

from threading import Thread
from taskmsgs import *
from smsutil  import *
from sim_brcm import *
from string import *
from common import *
from GUI import *
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

MSG_TYPE_INDICATOR 	=	'\x8c'
M_SEND_REQ 		=	'\x80'
M_SEND_CONF 		=	'\x81'
M_RETREIVE_CONF 	=	'\x84'
M_NOTIFYRESP_IND	=	'\x83'
X_MMS_RESPONSE_STATUS	=	'\x92'
X_MMS_RESPONSE_TEXT 	=	'\x93'
RESP_STATUS_VALUE_OK 	=	'\x80'
MESSAGE_ID 		=	'\x8b'


# The MmsProxy class implements an http server thread, http events are handled 
# by the MmscHandler class

class MmsProxy(Thread):
    def __init__(self, queue, port, ui):
        global mmsc_proxy_port, q, gui
        gui = ui
        q = queue
        mmsc_proxy_port = port
        Thread.__init__(self, name="MmscServer")

    def run( self ):
        print tod(), "MMS Proxy Started...."

        #### Need a delay event ####
        print tod(), "MMS Proxy listening on port %d" % mmsc_proxy_port
        server = HTTPServer(('', int(mmsc_proxy_port)), MmscHandler)
        server.serve_forever()

# The MmmscHandler class implements the response events for http GET/POST requests
class MmscHandler(BaseHTTPRequestHandler):

    def do_GET(self):
            print tod(), "MMS Proxy: Get request received: sending stored MMS"
            print self.headers,"----------------"

            #### send the stored MMS file ####
            MMS = open("StoredMMS.bin", 'rb')
            self.wfile.write(MMS.read())
            print tod(), "MMS Proxy: MMS sent complete"
            gui.info.set("MMS message in 'StoredMMS.bin' sent to client ")
            return
  

    def do_POST(self):
            print tod(), "MMS Proxy: Post request received:"
            print self.headers,"----------------"

            #### myfile is for storing MMS messages / POST requests
            #### if it's a send-req, this file would be copied into StoredMMS.bin
            myfile = open("temp.bin", 'wb')

            #### receivedData is for any data POSTed by PhoneSim ####
            rxData = open("MMS_POSTReceivedData.bin", 'wb')

            #### replyFile is for send-conf ####
            replyFile = open("sendConf.bin", 'wb')

            contentLen = int(self.headers.getheader("content-length", 0))
            chunked = self.headers.getheader("Transfer-Encoding", "")

            myfile.write("HTTP/1.1 200 OK\r\n")
            myfile.write("Content-type: application/vnd.wap.mms-message\r\n")

            replyFile.write("HTTP/1.1 200 OK\r\n")
            replyFile.write("Content-type: application/vnd.wap.mms-message\r\n")

            isChunked = FALSE
            if chunked == "chunked":
               isChunked = TRUE
               myfile.write("Transfer-Encoding: chunked\r\n")

            #### end HTTP header ####
            myfile.write("\r\n")
            replyFile.write("\r\n")


            #### initialize buffer to store past data ####
            passThruBuffer = ['\xFF', '\xFF', '\xFF', '\xFF']

            #### initialize state variables ####
            done           = FALSE
            readPduHdr     = FALSE
            sendReq        = FALSE
            readCount      = 0
            writtenConfPdu = FALSE

            while done == FALSE:

                if (isChunked == FALSE) and (contentLen == 0):
                    print tod(), "MMS Proxy: does not contain content-length and it's not chunked either, cannot process"
                    break

                #### read a byte and shift the buffer ####
                passThruBuffer = [self.wfile.read(1), passThruBuffer[0], passThruBuffer[1], passThruBuffer[2]]
                readCount = readCount + 1

                if passThruBuffer[0] == "":
                   done = TRUE

                rxData.write(passThruBuffer[0])

                #### read Pdu header ####
                if readPduHdr == FALSE:
                    if passThruBuffer[1] == MSG_TYPE_INDICATOR:

                         #### send-req
                         if passThruBuffer[0] == M_SEND_REQ:
                              #### change it to m-retrieve-conf x84 for storage
                              passThruBuffer[0] = M_RETREIVE_CONF
                              sendReq = TRUE
                              readPduHdr = TRUE
                              replyFile.write(MSG_TYPE_INDICATOR)
                              replyFile.write(M_SEND_CONF)

                         #### notifyresp-ind
                         elif passThruBuffer[0] == M_NOTIFYRESP_IND:
                              sendReq = FALSE
                              readPduHdr = TRUE

                #### store the byte to MMS message storage ####
                myfile.write(passThruBuffer[0])

                if isChunked:
                    #### check for end of chunked message
                    if (passThruBuffer[3] == '\n') and (passThruBuffer[2] == '0') and (passThruBuffer[1] == '\r') and (passThruBuffer[0] == '\n'):
                         done = TRUE
                         print tod(), "MMS Proxy: Chunked request processed"

                elif contentLen > 0:
                    #### read up to content-length
                    if readCount >= contentLen:
                         done = TRUE
                         print tod(), "MMS Proxy: " + str(contentLen) + " bytes of data processed"

                #### Constructing the send-conf pdu start ####
                if (readPduHdr == TRUE) and (writtenConfPdu == FALSE):

                    #### skip the M-retr-conf byte because we already wrote m-send-conf for the header #### 
                    if passThruBuffer[0] != M_RETREIVE_CONF:

                         ####   Get the Transaction ID and MMS version   ####
                         #### (TransID ends with x00 and ver is 2 bytes) ####
                         #### then finish constructing the send-conf pdu ####

                         if passThruBuffer[3] != '\x00':
                             replyFile.write(passThruBuffer[0])
                         else:
                             writtenConfPdu = TRUE
                             #### set status flag to Ok
                             replyFile.write(X_MMS_RESPONSE_STATUS)
                             replyFile.write(RESP_STATUS_VALUE_OK)

                             #### set text response to "Ok" (Optional)
                             replyFile.write(X_MMS_RESPONSE_TEXT)
                             replyFile.write("Ok")
                             replyFile.write('\x00')

                             #### set message ID to "01" (arbitary and optional)
                             replyFile.write(MESSAGE_ID )
                             replyFile.write("01")
                             replyFile.write('\x00')
                             replyFile.close()

                #### Constructing the send-conf pdu end ####

            #### end while done == FALSE ####


            #### close the MMS message file ####
            myfile.close()
            rxData.close()

            #### send response back to client: ####
            if sendReq == TRUE:
                 #### send send-conf pdu ####
                 replyFile = open("sendConf.bin", 'rb')
                 self.wfile.write(replyFile.read())
                 self.wfile.flush()
                 print tod(), "MMS Proxy: Send-conf sent"                 
                 #### clean up ####
                 shutil.copyfile("temp.bin", "StoredMMS.bin")
                 print tod(), "MMS Proxy: MMS stored successfully"
                 gui.info.set("A new MMS message has been saved to StoredMMS.bin")

                 #### automatic loop back: ####
                 #### send m-notification-ind (arbitary pdu) ####
                 notificationPdu = "\"40069111111100F506062209370800730605040B8400010006266170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500AF84B4818DCA8C8298246D32008D908A808E02052088068104449D6A3496546573740083687474703A2F2F3132372E302E30302E313A313636342F6D6D73632F54483F7469643D3100\""
                 smscPdu = "\"[]\""

                 gui.wap_push_content.set(notificationPdu)
                 gui.sms_smsc.set(smscPdu)
                 gui.blink_field(gui.wap_push_msg)

                 if gui.varloopbackMMS.get() == TRUE:
                     gui.send_wap_push_pdu()

            else:
                 self.wfile.write("HTTP/1.1 200 OK\r\n\r\n")


            #### clean up ####
            replyFile.close()
            os.remove("temp.bin")
            os.remove("sendConf.bin")
            return

