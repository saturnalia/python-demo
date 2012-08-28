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

from common import *
from GUI import *

from callctrl import *
from ss_api import *
from pchtypes import *

from common_cc_ds import *
from capi2_ss_ds   import *

persist_PIN_code = ['"1234"','"4321"']             # PIN1 and PIN2 code
persist_PUK_code = ['"12345678"','"87654321"']     # PUK1 and PUK2 code
try:
    from persist import *
except:
    print "Using default GSM State..."

#
# Call Barring
#

class SS_ActivationClassInfo_t:
    def __init__(self, _activated, _ss_class):
        self.activated = _activated     # TRUE if service activated */
        self.ss_class = _ss_class       # SS_SvcCls_t 

class CallBarringStatus_t:
    def __init__(self, _call_barring_type):
        self.netCause = GSMCAUSE_SUCCESS            # NetworkCause_t 
        self.call_barring_type =_call_barring_type  # SS_CallBarType_t
        self.cbPassword = '"0000"'
        self.ss_activation_class_info = []          # SS_ActivationClassInfo_t 
        # All barrings OFF
        self.ss_activation_class_info.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_SPEECH))
        self.ss_activation_class_info.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DATA))
        self.ss_activation_class_info.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_FAX))
        self.ss_activation_class_info.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_SMS))

class CallForwardClassInfo_t:
    def __init__(self, _activated, _ss_class, _number=''):
        self.activated = _activated
        self.ss_class = _ss_class            # SS_SvcCls_t 
        self.forwarded_to_number = _number


class CallForwardStatus_t:
    def __init__(self, _reason):
        self.netCause = GSMCAUSE_SUCCESS    # NetworkCause_t 
        self.reason =_reason                # SS_CallFwdReason_t 
        self.call_forward_class_info_list = []
        self.call_forward_class_info_list.append(CallForwardClassInfo_t(FALSE, SS_SVCCLS_SPEECH))
        self.call_forward_class_info_list.append(CallForwardClassInfo_t(FALSE, SS_SVCCLS_ALT_SPEECH ))
        self.call_forward_class_info_list.append(CallForwardClassInfo_t(FALSE, SS_SVCCLS_DATA))
        self.call_forward_class_info_list.append(CallForwardClassInfo_t(FALSE, SS_SVCCLS_FAX))
        self.call_forward_class_info_list.append(CallForwardClassInfo_t(FALSE, SS_SVCCLS_SMS))

# State of one call
class CCallInfo_t:
    def __init__(self, callType = MOVOICE_CALL, callState = CC_CALL_BEGINNING, clientID=0):
        self.callType  = callType   # CCallType_t
        self.callState = callState  # CCallState_t 
        #self.callExitCause         # Cause_t 
        self.callMpty  = FALSE      # Not multiparty
        self.callConnectedIDPresent = FALSE
        self.callConnectedID = ''   # Other party
        self.callStateTimeStamp = 0.0
        self.callSetupPhase = FALSE
        self.clientID = clientID
        
        ################
        # Set functions
    def setCallType(self, callType):
        self.callType  = callType   # CCallType_t

    def setCallState(self, callState):
        # New state Connected ?
        if callState == CC_CALL_CONNECTED:
            # and was Calling or Waiting?
            if self.callState == CC_CALL_CALLING or self.callState == CC_CALL_WAITING:
                self.callStateTimeStamp = time.time()
        self.callState = callState  # CCallState_t 

    def setCallConnectedID(self, callConnectedID):
        self.callConnectedID = callConnectedID
        self.callConnectedIDPresent = TRUE

        ################
        # Get functions
    def getCallType(self):
        return self.callType        # CCallType_t

    def getCallState(self):
        return self.callState       # CCallState_t 

    def getCallConnectedID(self):
        return self.callConnectedID # Other party

    def ClientID(self, clientID=None):
        # Set ?
        if clientID != None: self.clientID = clientID
        return self.clientID

    def getTimestamp(self):
        return self.callStateTimeStamp

######################
# Simulator state here
class GSM_State:
    def __init__(self):
        # private:
        self.startTime        = time.time()
        self.active           = FALSE       # TRUE if client active
        self.sim_state        = FALSE       # TRUE if GSM Sim thread running
        self.isRegisteredGSM  = FALSE       # TRUE if registered to GSM network
        self.isRegisteredGPRS = FALSE       # TRUE if registered to GPRS network
        # SIM:
        self.needPIN          = FALSE		# **FixMe** setting this to true won't work right now
        self.isPIN_OK         = FALSE       # TRUE if verified against 'PIN1_code'
        self.isSIM_removed    = FALSE       # TRUE if SIM is removed
        self._PIN_code        = persist_PIN_code    # PIN1 and PIN2 code
        self._PUK_code        = persist_PUK_code    # PUK1 and PUK2 code
        self._PIN_attempts    = [3,3]       # Remaining PIN1 and PIN2 attempts
        self._PUK_attempts    = [3,3]       # Remaining PUK1 and PUK2 attempts
        self.haveSVC          = FALSE       # TRUE if there is a service provider name
        self.FDN_enabled      = FALSE       # TRUE if Fixed Dialing Number
        self.ACM_MAX          = 100
        self.ACM              = 0
        self.pbk_ready        = FALSE
        self.display_pref     = [0,0,0,0,0]
        self.pref_storage     = ME_STORAGE
        # Test:
        self.FieldTestEnabled = FALSE

        # Keypad:
        self.isKPD_running    = FALSE       # Keypad run called?
        self.isKPD_registered = FALSE       # Keypad callback is registered?
        # Flags from debug console:
        self.MT_Generate      = 0           # Generate MT Voice calls
        self.MT_Number        = ''          # From number
        self.Release_Call     = FALSE       # MO/MT Release from network
        self.SendRXLEV        = TRUE        # Send RX level messages
        # Call Control, array of 10 calls
        self.ci               = 0           # CI 0 is always first
        self.cc = [None, None, None, None, None, None, None, None, None, None]
        self.timer_process    = 1           # "tag" of last timer process
        self.maxSleep         = 0.1         # Max time to sleep before checking queue
        self.BuzzerActive     = BOOL_FALSE  # No initial buzzer
        self.lastCallDuration = 0.0         # Last active call duration
        self._microphoneOn    = 1           # Microphone on?
        self._microphoneGain  = 8           # Max microphone gain
        self._speakerVol      = 8           # Max speacker volume
        self.Battmgr_Active   = TRUE        # BUG: BATTMGR_RegisterStatus() done
        self.Charger_Inserted = FALSE       # Charger not inserted
        # Default operator AT&T Wireless
        self.operatorShort    = 'ATWS'
        self.operatorLong     = 'AT&T Wireless'
        self.rawmcc           = 0x1300
        self.rawmnc           = 0x83
        self.home_rawmcc      = 0x1300
        self.home_rawmnc      = 0x83
        self.ALS_default_line = 0

        # Call Waiting
        self.callwaiting = []
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_SPEECH))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DATA))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_FAX))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_SMS))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DATA_CIRCUIT_SYNC))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DATA_CIRCUIT_ASYNC))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DEDICATED_PACKET))
        self.callwaiting.append(SS_ActivationClassInfo_t(FALSE, SS_SVCCLS_DEDICATED_PAD))

        # Barring
        self.callbarring = []               # Call barring status
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_OUT_ALL))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_OUT_INTL))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_OUT_INTL_EXCL_HPLMN))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_INC_ALL))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_INC_ROAM_OUTSIDE_HPLMN))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_ALL))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_OUTG))
        self.callbarring.append(CallBarringStatus_t(SS_CALLBAR_TYPE_INC))

        # Call forwarding
        self.callforward = []
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_UNCONDITIONAL))
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_BUSY))
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_NO_REPLY))
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_NOT_REACHABLE))
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_ALL_CF_STR))
        self.callforward.append(CallForwardStatus_t(SS_CALLFWD_REASON_ALL_CONDITIONAL_STR))

        self.GPRSActivate       = PDP_CONTEXT_DEACTIVATED
        self.fp                 = 0          # Logfile for GUI

    # Save the persistent part of the state
    def persistState(self):
        pers = open('persist.py','w+')
        pers.write('# Saved with $Id: GSM_State.py,v 1.46 2004/02/09 10:48:27 arne Exp $\n')
        pers.write('persist_PIN_code = ' + "['%s','%s']\n" % (self._PIN_code[0],
                                                              self._PIN_code[1]))
        pers.write('persist_PUK_code = ' + "['%s','%s']\n" % (self._PUK_code[0],
                                                              self._PUK_code[1]))
        pers.close()

    def setGUI(self, gui):
        self.gui = gui

    # Get / Set registerstatus GSM
    def registeredGSM(self, set=None):
        if set != None:
            self.isRegisteredGSM = set
        return self.isRegisteredGSM

    # Get / Set registerstatus GPRS
    def registeredGPRS(self, set=None):
        if set != None:
            self.isRegisteredGPRS = set
        return self.isRegisteredGPRS

    # Get / Set PIN OK Status
    def PIN_OK(self, set=None):
        if set != None:
            self.isPIN_OK = set
        return self.isPIN_OK

    # Get / Set SIM Removed status
    def SIM_removed(self, set=None):
        if set != None:
            self.isSIM_removed = set
        return self.isSIM_removed

    def KPD_running(self, set=None):
        if set != None:
            self.isKPD_running = set
        return self.isKPD_registered

    def KPD_registered(self, set=None):
        if set != None:
            self.isKPD_registered = set
        return self.isKPD_registered

    def PIN_code(self, no=1, code=None):
        if no == 1 or no == 2:
            # to index
            no -= 1
            if code != None:
                self._PIN_code[no] = code
                self.gui.update_sim()
                self.persistState()
        return self._PIN_code[no]

    def PUK_code(self, no=1,  code=None):
        if no == 1 or no == 2:
            # to index
            no -= 1
            if code != None:
                self._PUK_code[no] = code
                self.gui.update_sim()
                self.persistState()
        return self._PUK_code[no]

    def PIN_attempts(self, no=1, attempts=None):
        if no == 1 or no == 2:
            # to index
            no -= 1
            if attempts != None:
                self._PIN_attempts[no] = attempts
                self.gui.update_sim()
        return self._PIN_attempts[no]

    def PUK_attempts(self, no=1, attempts=None):
        if no == 1 or no == 2:
            # to index
            no -= 1
            if attempts != None:
                self._PUK_attempts[no] = attempts
                self.gui.update_sim()
        return self._PUK_attempts[no]

    # Get number of supported callindexes
    def callIndexes(self):
        return len(self.cc)

    # Get next active callindex
    def GetNextActiveCallIndex(self):
        length = len(self.cc)
        ci = 0
        while ci < length:
            # Free CI ?
            if self.cc[ci] == None:
                return ci
            ci += 1
        return -1

    def GetNextHeldCallIndex(self):
        length = len(self.cc)
        ci = 0
        while ci < length:
            # Held CI ?
            if self.cc[ci] != None and self.cc[ci].getCallState() == CC_CALL_HOLD:
                return ci
            ci += 1
        return -1

    # Check if a callindex is active
    def activeCallIndex(self, ci=None):
        # Current callindex ?
        if ci == None: ci = self.ci
        return self.cc[ci] != None

    # Release a call
    def releaseCall(self, ci=None):
        # Current callindex ?
        if ci == None: ci = self.ci
        self.cc[ci] = None
        self.gui.update_cc(ci)

    def newCall(self, type, state, number, client):
        ci = self.GetNextActiveCallIndex()
        self.cc[ci] = CCallInfo_t(type, state, client)
        self.cc[ci].setCallConnectedID(number)
        self.gui.update_cc(ci)
        return ci

    # Set a new call active
    def setActiveCallIndex(self, ci):
        self.ci = ci
        return self.ci

    # Get / Set call type
    def callType(self, ci=None, type=None):
        # Current callindex ?
        if ci == None: ci = self.ci
        # Set calltype ?
        if type != None: 
            self.cc[ci].setCallType(type)
            self.gui.update_cc(ci)
        return self.cc[ci].getCallType()

    # Get / Set call state
    def callState(self, ci=None, state=None):
        # Current callindex ?
        if ci == None: ci = self.ci
        # Illegal CI ?
        if ci > len(self.cc):
            return UNKNOWN_ST
        # Inactive call ?
        if self.cc[ci] == None:
            return UNKNOWN_ST
        # Set state ?
        if state != None:
            # All calls in a Multi-Party call should
            # be set to the same state
            if self.cc[ci].callMpty :
                for ix in range( len(self.cc) ):
                    if self.cc[ix] != None:
                        if self.cc[ix].callMpty :
                            self.cc[ix].setCallState(state)
                            self.gui.update_cc(ix)
            else:
                self.cc[ci].setCallState(state)
                self.gui.update_cc(ci)
        return self.cc[ci].getCallState()

    def MultiPartyCall(self, ci=None, set=None):
        # Current callindex ?
        if ci == None:  ci = self.ci
        if set != None: self.cc[ci].callMpty = set
        if self.cc[ci] == None: return FALSE
        return self.cc[ci].callMpty

    # Get ID of other party
    def callConnectedID(self, ci=None):
        # Current callindex ?
        if ci == None: ci = self.ci
        if self.cc[ci] != None:
            return self.cc[ci].getCallConnectedID()
        return "Invalid call"

    def ClientID(self, ci, clientID=None):
        return self.cc[ci].ClientID(clientID)

    # Return Call duration in seconds
    def callDuration(self, ci=None):
        if ci == None: ci = self.ci
        if self.cc[ci] != None:
            return time.time() - self.cc[ci].getTimestamp()
        # Call is not active
        return 0.0

    # Set/Get microphone on status
    def microphoneOn(self, on=None):
        if on != None: self._microphoneOn = on
        return self._microphoneOn

    # Set/Get microphone gain
    def microphoneGain(self, gain=None):
        if gain != None: self._microphoneGain = gain
        return self._microphoneGain

    # Set/Get speaker volume
    def speakerVol(self, vol=None):
        if vol != None: self._speakerVol = vol
        return self._speakerVol

    def operator(self, short, long, _mcc, _mnc):
        self.operatorShort  = short
        self.operatorLong   = long
        self.rawmcc         = _mcc
        self.rawmnc         = _mnc

    def homeoperator(self, _mcc, _mnc):
        self.home_rawmcc    = _mcc
        self.home_rawmnc    = _mnc

    def getCallbarring(self, callBarType):
        # Check all
        for ix in range(len(self.callbarring)):
            # Match ?
            if self.callbarring[ix].call_barring_type == callBarType:
                return self.callbarring[ix]
        return None

    def getCallforward(self, callForwReason):
        # Check all
        for ix in range(len(self.callforward)):
            # Match ?
            if self.callforward[ix].reason == callForwReason:
                return self.callforward[ix]
        return None

    def getCallwaiting(self, ss_class):
        for ix in range(len(self.callwaiting)):
            if self.callwaiting[ix].ss_class == ss_class:
               return self.callwaiting[ix]
        return None

    def getAllCallwaiting(self):
        return self.callwaiting

	def getACMMax( self ):
		return self.ACM_MAX

	def getACM( self ):
		return self.ACM

	def setACMMax( self, acm_max ):
		self.ACM_MAX = acm_max

	def setACM( self, acm ):
		self.ACM = acm

    def setPBKReady( self, ready ):
        self.pbk_ready = ready

    def getPBKReady( self ):
        return self.pbk_ready

    def setFieldTest( self, enabled ):
	   self.FieldTestEnabled = enabled

    def getFieldTest( self ):
	   return self.FieldTestEnabled
