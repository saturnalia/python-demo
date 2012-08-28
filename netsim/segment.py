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
#*****************************************************************************/

from math import ceil
from common import *
from binascii import hexlify

refNum = 0
MAX_CHAR_PER_SEGMENT = 140


# The following function takes in the raw data for an SMS or a WAP Push pdu
# and creates a list of segments if necessary. In case the data does not need
# to be segmented, the segment list has only one element.
#
# [in] data         - the raw pdu data
# [in] isWapPush    - set to TRUE for Wap Push pdu, otherwise the pdu is treated
#                     as a normal SMS
# [out] segmentList - the list of segmented pdus
#

def createSMSSegments(data, isWapPush = FALSE):
    global refNum
    # adds SMS header to the WAP push message!
    # hardcoded data encoding, 8-bit ascii only!

    # SMS-Deliver Pdu format:
    # ----------------------------------
    # [1] Type (SMS-Deliver, 0x40 is UDHI=1, 0x44 is UDHI=1/MoreMsgToSend=1)
    # [1] Sender's Number Length (06)
    # [n] Sender address (SMSC: +111111)
    # [1] PID (00)
    # [2] Data coding scheme is F5 (8 bit ASCII, Class 1)
    # [7] Time stamp (dynamic)
    # [1] User Data Length (dynamic)
    # [1] User Data Header Length (10 for segmented, 06 for unsegmented)
        # [1] Information Element Identifier (00==Concatenated 8-bit ref number)
        # [1] Information Element Identifier Data Length (03)
        # [1] Reference number (generated variable)
        # [1] Number of message segments (variable)
        # [1] Sequence Number (increase by 1 for each segment, starting with 1)
        # the following IEI is for WAP push via UDP
        # [1] Information Element Identifier (05==Application Port Address Scheme 16 bit)
        # [1] Information Element Identifier Data Length (04)
        # [n] Information Element Data (Dst=0b84, Src=0001 [WAP push, UDP])
    # [n] User Data

    segmentList = []

    # update refNum
    refNum = refNum + 1
    if refNum > 255:
        refNum = 0

    timeStamp = get_gsm_gmt()

    seqNum = 1
    WAPIEI = ""
    UDHL = 0
    if isWapPush:
        WAPIEI = "05040B840001" #send to WAP push port via UDP


    totalSegNum = int(ceil(len(data) / float(MAX_CHAR_PER_SEGMENT)))

    # for debugging:
    # print "Total seg num ", totalSegNum

    if (totalSegNum > 1):

        while(len(data) > 0):
            UDH = WAPIEI + "0003" + ("%02X" % refNum) + ("%02X" % totalSegNum) + ("%02X" % seqNum)
            UDHL = len(UDH) / 2

            if (len(data) > MAX_CHAR_PER_SEGMENT):
                curData = data[0 : MAX_CHAR_PER_SEGMENT]
                # take out the processed data
                data = data[MAX_CHAR_PER_SEGMENT : ]
                pdu = hexlify(curData)
                seqNum = seqNum + 1
            else:
                pdu = hexlify(data)
                curData = data
                # set the data to an empty string because we're done
                data = ""

            msgLen = len(curData) + UDHL + 1
            msg = "44069111111100F5" + timeStamp + ("%02X" % msgLen) + ("%02X" % UDHL) + UDH + pdu
            segmentList.append(msg)

    else:

        pdu = hexlify(data)
        UDH = WAPIEI
        UDHL = len(UDH) / 2
        msgLen = len(data) + UDHL + 1

        msg = "40069111111100F5" + timeStamp + ("%02X" % msgLen) + ("%02X" % UDHL) + UDH + pdu
        segmentList.append(msg)
    return segmentList
