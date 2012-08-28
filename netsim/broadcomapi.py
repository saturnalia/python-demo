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
import pickle

# Extracted Broadcom enums
from mstypes    import *
from common_defs    import *
from mstypes_enum    import *
from taskmsgs   import *
from callctrl   import *
from sim_brcm   import *
from smsutil    import *
from resultcode import *
from smsapi     import *
from sms_storage import *
from common_sms		import *
from stk_api     import *
from ss_api     import *
from msnu       import *
from serialapi  import *
from dataComm import *
from phonebk_api import *
from dataacct_api   import *
from pchtypes   import *
from pch_def   import *
from dataacct_def   import *

from common    import *
from enums     import *
from GSM_State import *
from GUI       import *
from queue     import *

Revision = "$Revision: 1.437 $"[11:]
Revision = Revision[:string.find(Revision,'$')]

# Abbreviated Dialing Number Phonebook
adn_pbk = [['arne', '41461735'], ['bjornaa','92400644'],
           ['egil', '92022780'], ['morten', '95143336'],
           ['ove',  '99999999'], ['pkg',    '92086292'],
           ['rune', '91713960'], ['seime',  '99574896'],
           ['tommy','97508097']] + (20-9)*[['','']]

# Fixed Dialing Number Phonebook
fdn_pbk = [[ 'FDN1','11111111'], [ 'FDN2','22222222'],
           [ 'FDN3','33333333']] + (5-3)*[['','']]

# Service Dialing Number Phonebook
sdn_pbk = [[ 'SDN1','11111111'], [ 'SDN2','22222222'],
           [ 'SDN3','33333333']] + (3-3)*[['','']]
# Last Number Dialed Phonebook
lnd_pbk = [['LND1','1111111']] + (10-1)*[['','']]
# MS ISDN Dialing Number Phonebook
msisdn_pbk = [[ 'MSISDN1','17778880001'], ['MSISDN2','87654321']] + (2-2)*[['','']]

# MS BDN Barred Dialing Number Phonebook
msbdn_pbk = [[ 'BDN1','11111111'], [ 'BDN2','22222222'],
           [ 'BDN3','33333333']] + (3-3)*[['','']]

#
# Set the State, GUI and Queue references
def broadcomApiInit(state, userinterface, queue, sms):
    global st, gui, q, smsdb, rtc
    st = state
    gui = userinterface
    q = queue
    smsdb = sms
    rtc = RTCSimulator()
    MSDATA_InitMsData()
    return
#
# Broadcom API functions:
#

# void CC_InitCallCfg(CallConfig_t* curCallCfg)

# void CC_InitFaxConfig( Fax_Param_t* faxCfg )

# Result_t CC_MakeVoiceCall(UInt8 clientID,UInt8* callNum, VoiceCallParam_t voiceCallParam);
def CC_MakeVoiceCall(args):
    # Check that all parameters are present
    if len(args) < 7:
        return CC_FAIL_MAKE_CALL
    # Assign the parameters
    clientID = args[0]
    callNum  = args[1]
    voiceCallParam_clir                         = args[2]   # Bug: Ignored
    voiceCallParam_cug_info_cug_index           = args[3]   # Bug: Ignored
    voiceCallParam_cug_info_suppress_pref_cug   = args[4]   # Bug: Ignored
    voiceCallParam_cug_info_suppress_oa         = args[5]   # Bug: Ignored
    voiceCallParam_isEmergency                  = args[6]   # Bug: Ignored

    # If there is an active call already, it must be on hold
    if st.activeCallIndex() and st.callState() != CC_CALL_HOLD:
        return CC_FAIL_CALL_SESSION

    # Initiate a new call
    ci = st.newCall(MOVOICE_CALL, CC_CALL_CALLING, callNum, clientID)
    # Make the call current
    st.setActiveCallIndex(ci)
    # Report back the call index
    result = "%d=CI" % ci

    result = "%d=CI,%s,%s" % (ci, MOVOICE_CALL, CC_CALL_BEGINNING )
    q.append_message(MSG_CALL_STATUS_IND, result )

    result = "%d=CI,%s,%s" % (ci, MOVOICE_CALL, CC_CALL_CALLING )
    q.append_message(MSG_CALL_STATUS_IND, result, 0.5 )

    # Accept MO ?
    if gui.varMoAction.get() == 0:
        # Schedule a MSG_VOICECALL_CONNECTED_IND after 2.5 seconds
        result += ",%s" % MNCAUSE_VOID_CAUSE
        q.append_message(MSG_VOICECALL_PRECONNECT_IND, result, 1.5)
        q.append_message(MSG_VOICECALL_CONNECTED_IND, result, 2.5)
        # and ALERTING after 1 second
        result = "%d=CI,%s,%s" % (ci, MOVOICE_CALL, CC_CALL_ALERTING)
        q.append_message(MSG_CALL_STATUS_IND, result, 1.)

    # Reject MO ?
    elif gui.varMoAction.get() == 1:
        result += ",%s" % MNCAUSE_MN_CALL_REJECTED
        q.append_message(MSG_VOICECALL_RELEASE_IND, result, 2.0)

    # Busy MO ?
    elif gui.varMoAction.get() == 2:
        result += ",%s" % MNCAUSE_USER_BUSY
        q.append_message(MSG_VOICECALL_RELEASE_IND, result, 2.0)

    return CC_MAKE_CALL_SUCCESS

# Result_t CC_MakeDataCall(UInt8 clientID,UInt8* callNum);
def CC_MakeDataCall(args):
    if len(args) < 2:
        return CC_FAIL_MAKE_CALL
    return CC_MAKE_CALL_SUCCESS

# Result_t CC_MakeFaxCall(UInt8 clientID,UInt8* callNum);
def CC_MakeFaxCall(args):
    if len(args) < 2:
        return CC_FAIL_MAKE_CALL
    return CC_MAKE_CALL_SUCCESS

# Result_t CC_EndCall(UInt8 callIdx)
def CC_EndCall(args):
    if len(args) < 1:
        return CC_WRONG_CALL_INDEX
    ci = int(args[0])
    # Is this an active call ?
    if not st.activeCallIndex(ci):
        return CC_WRONG_CALL_INDEX

    result = "%d,%s" % (ci, MNCAUSE_NORMAL_CALL_CLEARING)
    q.append_message(MSG_VOICECALL_RELEASE_IND, result)
    return CC_END_CALL_SUCCESS

# Result_t CC_EndAllCalls(void)
def CC_EndAllCalls(args):
    len = st.callIndexes()
    ci = 0
    res = CC_END_CALL_FAIL
    while ci < len:
        # Active call ?
        if st.activeCallIndex(ci):
            res = CC_END_CALL_SUCCESS
            result = "%d,%s" % (ci, MNCAUSE_NORMAL_CALL_CLEARING)
            q.append_message(MSG_VOICECALL_RELEASE_IND, result, 1.5)
        ci += 1
    return res

# Result_t CC_EndMPTYCalls(void)
def CC_EndMPTYCalls(args):
    len = st.callIndexes()
    ci = 0
    res = CC_END_CALL_FAIL
    while ci < len:
        # Active multiparty call ?
        if st.activeCallIndex(ci) and st.MultiPartyCall(ci) == TRUE:
            res = CC_END_CALL_SUCCESS
            result = "%d,%s" % (ci, MNCAUSE_NORMAL_CALL_CLEARING)
            q.append_message(MSG_VOICECALL_RELEASE_IND, result, 1.5)
        ci += 1
    return res

# Result_t CC_EndHeldCall(void)
def CC_EndHeldCall(args):
    len = st.callIndexes()
    ci = 0
    res = CC_WRONG_CALL_INDEX
    while ci < len:
        # Call on hold ?
        if st.callState(ci) == CC_CALL_HOLD:
            res = CC_END_CALL_SUCCESS
            result = "%d,%s" % (ci, MNCAUSE_NORMAL_CALL_CLEARING)
            q.append_message(MSG_VOICECALL_RELEASE_IND, result, 1.5)
        ci += 1
    return res

# Result_t CC_AcceptVoiceCall(UInt8 clientID,UInt8 callIndex)
def CC_AcceptVoiceCall(args):
    if len(args) < 2:
        return CC_ACCEPT_CALL_FAIL
    clientID = args[0]
    ci = int(args[1])
    if st.callState(ci) == CC_CALL_CALLING:
        # Make the call current
        st.setActiveCallIndex(ci)
        st.ClientID(ci, clientID)
        result = "%d=CI,%s,%s" % (ci, CC_ACCEPT_CALL_SUCCESS, GSMCAUSE_SUCCESS)
        q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
        result = "%d=CI,%s,%s" % (ci, MTVOICE_CALL, CC_CALL_CALLING)
        q.append_message(MSG_CALL_STATUS_IND, result)
        result = "%d=CI" % (ci)
        q.append_message(MSG_VOICECALL_CONNECTED_IND, result, 2.0)
        return CC_ACCEPT_CALL_SUCCESS
    return CC_ACCEPT_CALL_FAIL

# Result_t CC_AcceptDataCall(UInt8 clientID,UInt8 callIndex)
def CC_AcceptDataCall(args):
    if len(args) < 2:
        return RESULT_ERROR
    clientID  = args[0]
    callIndex = args[1]
    return CC_ACCEPT_CALL_SUCCESS

# Result_t CC_AcceptWaitingCall(UInt8 clientID)
def CC_AcceptWaitingCall(args):
    clientID  = args[0]

    active = 0
    for ci in range(st.callIndexes()):
        # Count number of active or held calls
        if st.callState(ci) == CC_CALL_ACTIVE:
            # Put current call on hold
            st.callState(ci, CC_CALL_HOLD)

    for ci in range(st.callIndexes()):
        # Is Waiting ?
        if st.callState(ci) == CC_CALL_WAITING:
            if active >= 2:
                result = "%d=CI,%s,%s" % (ci, CC_ACCEPT_CALL_SUCCESS, GSMCAUSE_SUCCESS)
                q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
            else:
                # Make the new call current
                st.setActiveCallIndex(ci)
                st.ClientID(ci, clientID)
                result = "%d=CI,%s,%s" % (ci, CC_ACCEPT_CALL_SUCCESS, GSMCAUSE_SUCCESS)
                q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
                result = "%d=CI" % (ci)
                q.append_message(MSG_VOICECALL_CONNECTED_IND, result)
            return CC_ACCEPT_CALL_SUCCESS
    # No Waiting...
    return CC_ACCEPT_CALL_FAIL

# Result_t CC_HoldCurrentCall();
def CC_HoldCurrentCall(args):
    args[0] = ("%d" % st.ci)
    return CC_HoldCall(args)

# Result_t CC_HoldCall(UInt8 callIndex);
def CC_HoldCall(args):
    ci = int(args[0])
    # If call is active 
    if st.activeCallIndex(ci):        # BUG: Limit to resonable states...
        result = "%d=CI,%s,%s" % (ci, CC_HOLD_CALL_SUCCESS, GSMCAUSE_SUCCESS)
        q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
        return CC_HOLD_CALL_SUCCESS
    return CC_HOLD_CALL_FAIL

# Result_t CC_RetrieveNextHeldCall();
def CC_RetrieveNextHeldCall(args):
    ci = st.GetNextHeldCallIndex()
    args[0] = ("%d" % ci)
    return CC_RetrieveCall(args)

# Result_t CC_RetrieveCall(UInt8 callIndex);
def CC_RetrieveCall(args):
    ci = int(args[0])
    # Call on hold ?
    if st.callState(ci) == CC_CALL_HOLD:
        # Yes, set as active call
        st.setActiveCallIndex(ci)
        # and activated
        #st.callState(ci, CC_CALL_ACTIVE)
        result = "%d=CI" % (ci)
        q.append_message(MSG_VOICECALL_CONNECTED_IND, result)
        #
        result = "%d=CI,%s,%s" % (ci, CC_RESUME_CALL_SUCCESS, GSMCAUSE_SUCCESS)
        q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
        return CC_RESUME_CALL_SUCCESS
    return CC_RESUME_CALL_FAIL

# Result_t CC_SwapCall(UInt8 callIndex); //Swap a held call to active with active calls
def CC_SwapCall(args):
    ci = int(args[0])
    # Call on hold ?
    if st.callState(ci) == CC_CALL_HOLD:
        # Hold active call
        st.callState(None, CC_CALL_HOLD)
        # Activate held call
        st.setActiveCallIndex(ci)
        #st.callState(ci, CC_CALL_ACTIVE)
        result = "%d=CI" % (ci)
        q.append_message(MSG_VOICECALL_CONNECTED_IND, result)
        # Action
        result = "%d=CI,%s,%s" % (ci, CC_SWAP_CALL_SUCCESS, GSMCAUSE_SUCCESS)
        q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
        return CC_SWAP_CALL_SUCCESS
    return CC_SWAP_CALL_FAIL

# Result_t CC_SplitCall(UInt8 callIndex); //hold the all active calls except the call with the callIndex
def CC_SplitCall(args):
    ci = int(args[0])
    # Other call must be active
    if st.callState(ci) == CC_CALL_ACTIVE:
        # It must already be a Multiparty call
        if st.MultiPartyCall(ci) == TRUE:
            # Not multiparty anymore
            st.MultiPartyCall(ci, FALSE)
            st.setActiveCallIndex(ci)
            result = "%d=ci,%s,%s" % (ci, CC_SPLIT_CALL_SUCCESS, GSMCAUSE_SUCCESS)
            q.append_message(MSG_VOICECALL_ACTION_RSP, result, 1.0)
            for active_ci in range(st.callIndexes()):
                # Not the requested ci ?
                if ci != active_ci:
                    # Other multiparty call ?
                    if st.MultiPartyCall(active_ci) == TRUE:
                        st.MultiPartyCall(active_ci, FALSE)
                        st.callState( active_ci, CC_CALL_HOLD )
                        result = "%d=CI,%s,%s" % (active_ci, MTVOICE_CALL, CC_CALL_HOLD)
                        q.append_message(MSG_CALL_STATUS_IND, result, 1.5)
            # All other put on hold
            return CC_SPLIT_CALL_SUCCESS;
    return CC_SPLIT_CALL_FAIL

# Result_t CC_JoinCall(UInt8 callIndex);
# Join an active call to the conversation
def CC_JoinCall(args):
    ci = int(args[0])
    # Other call must be active
    if st.callState(ci) == CC_CALL_ACTIVE:
        for held_ci in range(st.callIndexes()):
            if st.callState(held_ci) == CC_CALL_HOLD and not st.MultiPartyCall(held_ci):
                st.MultiPartyCall(held_ci, TRUE)
                result = "%d=CI" % (held_ci)
                q.append_message(MSG_VOICECALL_CONNECTED_IND, result, 1.5)
        result = "%d=ci,%s,%s" % (ci, CC_JOIN_CALL_SUCCESS, GSMCAUSE_SUCCESS)
        q.append_message(MSG_VOICECALL_ACTION_RSP, result, 1.5 )
        # Set joined call to Multiparty also
        st.MultiPartyCall(ci, TRUE)
        result = "%d=CI" % (ci)
        st.callState( ci, CC_CALL_ACTIVE )
        q.append_message(MSG_VOICECALL_CONNECTED_IND, result, 1.0)
        return CC_JOIN_CALL_SUCCESS
    else:
       print "Call state not active ", ci
    return CC_JOIN_CALL_FAIL;

# Result_t CC_TransferCall(UInt8 callIndex);
def CC_TransferCall(args):
    ci = int(args[0])
    # BUG:
    result = "%d=CI,%s,%s" % (ci, CC_TRANS_CALL_SUCCESS, GSMCAUSE_SUCCESS)
    q.append_message(MSG_VOICECALL_ACTION_RSP, result, 0.1)
    return CC_TRANS_CALL_SUCCESS

# Boolean CC_IsSimOriginatedCall(void); // TRUE, if SIM is inserted but FDN active
def CC_IsSimOriginatedCall(args): 
    return BOOL_FALSE

# Result_t CC_SendDTMF(UInt8 dtmfDigit,UInt8 callIndex);
def CC_SendDTMF(args):
    dtmfDigit = args[0]
    ci = int(args[1])
    return CC_SEND_DTMF_SUCCESS

# Result_t CC_StopDTMF(UInt8 callIndex){
def CC_StopDTMF(args):
    ci = int(args[0])
    return CC_STOP_DTMF_SUCCESS

# Result_t CC_MuteDTMFTone(Boolean flag);
def CC_MuteDTMFTone(args):
    return RESULT_OK

# UInt8 CC_GetCurrentCallIndex();
def CC_GetCurrentCallIndex(args):
    callState = st.callState(st.ci)
    if callState == CC_CALL_ACTIVE or callState == CC_CALL_CALLING:
        return "%d=CI" % st.ci
    return INVALID_CALL

# UInt8 CC_GetNextActiveCallIndex();
def CC_GetNextActiveCallIndex(args):
    for ci in range(st.callIndexes()):
        callState = st.callState(ci)
        if callState == CC_CALL_ACTIVE or callState == CC_CALL_CALLING:
            return "%d=CI" % ci
    return INVALID_CALL

# UInt8 CC_GetNextHeldCallIndex();
def CC_GetNextHeldCallIndex(args):
    for ci in range(st.callIndexes()):
        callState = st.callState(ci)
        if callState == CC_CALL_HOLD:
            return "%d=CI" % ci
    return INVALID_CALL

# UInt8 CC_GetNextWaitCallIndex(void);
def CC_GetNextWaitCallIndex(args):
    for ci in range(st.callIndexes()):
        callState = st.callState(ci)
        if callState == CC_CALL_WAITING:
            return "%d=CI" % ci
    return INVALID_CALL

# UInt8 CC_GetMPTYCallIndex();
def CC_GetMPTYCallIndex(args):
    return INVALID_CALL

# CCallState_t CC_GetCallState(UInt8 callIndex);
def CC_GetCallState(args):
    ci = int(args[0])
    if ci < st.callIndexes() and st.cc[ci] != None:
        return st.callState(ci)
    return UNKNOWN_ST

# CCallType_t CC_GetCallType(UInt8 callIndex);
def CC_GetCallType(args):
    ci = int(args[0])
    if ci < st.callIndexes() and st.cc[ci] != None:
        return st.cc[ci].getCallType()
    return UNKNOWN_TY

# Cause_t CC_GetLastCallExitCause(void);
def CC_GetLastCallExitCause(args):
    return MNCAUSE_VOID_CAUSE

# Boolean CC_GetCallNumber(UInt8 callIndex,UInt8* phNum);
def CC_GetCallNumber(args):
    ci      = int(args[0])
    if ci < st.callIndexes() and st.cc[ci] != None:
        return "%s,%s" % (BOOL_TRUE, st.cc[ci].getCallConnectedID())
    # Invalid callindex
    return BOOL_FALSE

# Boolean CC_SetCallNumber(UInt8 callIndex,UInt8* phNum);
def CC_SetCallNumber(args):
    ci      = int(args[0])
    phNum   = args[1]
    if ci < st.callIndexes() and st.cc[ci] != None:
        st.cc[ci].setCallConnectedID(phNum)
        return BOOL_TRUE
    # Invalid callindex
    return BOOL_FALSE

# Result_t CC_GetAllCallStates(CCallStateList_t *stateList, UInt8 *listSz)
def CC_GetAllCallStates(args):
    # assume one active call with state 2
    result = CC_OPERATION_SUCCESS
    length = st.callIndexes()
    ci = 0
    while ci < length:
        if st.cc[ci] != None:
            result = "%s,[%s]" % ( result , st.cc[ci].getCallState())
        ci += 1
    return result

# Result_t CC_GetAllActiveCallIndex(CCallIndexListt_t *indexList,UInt8 *listSz)
def CC_GetAllActiveCallIndex(args):
    # assume one active call with index 1
    result = CC_OPERATION_SUCCESS
    length = st.callIndexes()
    ci = 0
    while ci < length:
        if st.cc[ci] != None:
            result += ",[%d]" % ci
        ci += 1
    return result

# Result_t CC_GetAllCallIndex(CCallIndexListt_t *indexList,UInt8 *listSz)
def CC_GetAllCallIndex(args):
    result = "%s,[" % CC_OPERATION_SUCCESS
    for ci in range(st.callIndexes()):
        if st.activeCallIndex(ci):
            result += "%d," % ci
    result += ']'
    return result

# Result_t CC_GetAllHeldCallIndex(CCallIndexListt_t *indexList,UInt8 *listSz)
def CC_GetAllHeldCallIndex(args):
    # BUG: assume no held calls
    return CC_OPERATION_SUCCESS

# Result_t CC_GetAllMPTYCallIndex(CCallIndexListt_t *indexList,UInt8 *listSz)
def CC_GetAllMPTYCallIndex(args):
    # BUG: assume no MPTY calls
    return CC_OPERATION_SUCCESS

#
#  phone simuator for phonebook
#

def PBK_IsReady(args):
    return st.getPBKReady()

# void PBK_RebuildADNPhonebk(void)
    
# void PBK_GetAlpha(char* number, PBK_API_Name_t* alpha)

# Boolean PBK_IsEmergencyCallNumber(char *phone_number)

# Boolean PBK_IsEmergencyCallNumber(char *phone_number)
def PBK_IsEmergencyCallNumber(args):
    phone_number = args[0]
    if phone_number == '"112"' or phone_number == '"911"':
        result = BOOL_TRUE
    else: 
        result = BOOL_FALSE
    return result

# Result_t PBK_SendInfoReq( UInt8 clientID, PBK_Id_t pbk_id, CallbackFunc_t* pbk_access_cb )

# Result_t PBK_SendFindAlphaMatchMultipleReq( UInt8 clientID, PBK_Id_t pbk_id,
#                                             ALPHA_CODING_t alpha_coding, UInt8 alpha_size,
#                                             UInt8 *alpha, CallbackFunc_t* pbk_access_cb )

# Result_t PBK_SendFindAlphaMatchOneReq( UInt8 clientID, UInt8 numOfPbk, PBK_Id_t *pbkId,
#                                             ALPHA_CODING_t alpha_coding, UInt8 alpha_size,
#                                             UInt8 *alpha, CallbackFunc_t* pbkAccessCb )

# Boolean PBK_IsReady(void)

# Result_t PBK_SendReadEntryReq( UInt8 clientID, PBK_Id_t pbk_id,
#                                UInt16 start_index, UInt16 end_index,
#                                CallbackFunc_t* pbk_access_cb )

# Result_t 
# PBK_SendWriteEntryReq( UInt8 clientID, PBK_Id_t pbk_id, Boolean special_fax_num, UInt16 index, UInt8 type_of_number,
#                        char *number, ALPHA_CODING_t alpha_coding, UInt8 alpha_size, UInt8 *alpha, CallbackFunc_t* pbk_access_cb )

# Result_t PBK_SendIsNumDiallableReq(UInt8 clientID, char *number, CallbackFunc_t* pbk_access_cb)

# sim.c
#
# Phone simulator for SIM access
#
# API functions

# Boolean SIM_IsPINRequired((void)); // TRUE, if PIN is required for operations
def SIM_IsPINRequired(args):
    global gui
    # Any PIN code set ?
    if gui.varPinEnabled.get() == TRUE and st.PIN_code(1) != '':
        return BOOL_TRUE
    st.PIN_OK(TRUE)
    return BOOL_FALSE

# Boolean SIM_IsPINVerified((void)); // TRUE, if PIN is verified for operations
def SIM_IsPINVerified(args):
    if st.PIN_OK() == TRUE:
        return BOOL_TRUE
    else:
        return BOOL_FALSE

# FIXME comes from sima_api.c
# void SIM_GetEonsPlmnName( UInt16 mcc, UInt8 mnc, UInt16 lac,
#			  PLMN_NAME_t *long_name, PLMN_NAME_t *short_name )
def SIM_GetEonsPlmnName(args):
    result = "%s,%s" % ("foo", "bar") 
    return result

# SIMType_t SIM_GetSIMType(void); // Get SIM type
def SIM_GetSIMType(args):
    result = SIMTYPE_NORMAL_SIM
    if st.SIM_removed() == TRUE:
        result = SIMTYPE_NO_CARD
    return result

# SIMPresent_t SIM_GetPresentStatus((void));  // SIM present status
def SIM_GetPresentStatus(args):
    if st.SIM_removed() == FALSE:
        return SIMPRESENT_INSERTED
    return SIMPRESENT_REMOVED


# Boolean SIM_IsPIN2Verified(void); // Check if correct PIN2 has ever been entered
def SIM_IsPIN2Verified(args):
    return BOOL_FALSE

# Boolean SIM_IsOperationRestricted(void); // TRUE, if SIM is inserted but FDN active
def SIM_IsOperationRestricted(args): 
    if st.FDN_enabled:
        return BOOL_TRUE
    return BOOL_FALSE

# Boolean SIM_IsPINBlocked(CHV_t chv); // check if CHV's PIN blocked
def SIM_IsPINBlocked(args):
    chv = int(args[0])               # Attempted CHV (0 or 1)
    if st.PIN_attempts(chv+1) == 0:
        return BOOL_TRUE
    return BOOL_FALSE

# Boolean SIM_IsInvalidSIM(void); // check if SIM is Invalid
def SIM_IsInvalidSIM(args):
    return BOOL_FALSE

# Boolean SIM_IsPUKBlocked(CHV_t chv); // check if CHV's PIN blocked
def SIM_IsPUKBlocked(args):
    chv = int(args[0])               # Attempted CHV (0 or 1)
    if st.PUK_attempts(chv+1) == 0:
        return BOOL_TRUE
    return BOOL_FALSE

# SIMPhase_t SIM_GetCardPhase(void); // Return the SIM card phase
def SIM_GetCardPhase(args):
    return SIMPHASE_2PLUS

# SIM_PIN_Status_t SIM_GetPinStatus(void)
def SIM_GetPinStatus(args):
    return VOID # FixMe

# Boolean SIM_IsPinOK(void)
def SIM_IsPinOK(args):
    return BOOL_TRUE # BUG

# IMSI_t* SIM_GetIMSI(void)
def SIM_GetIMSI(args):
    return '"1234567890"';

# PLMNId_t SIM_GetHomePlmn(void)
def SIM_GetHomePlmn(args):
    return "0x%x=rawmcc,0x%x=rawmnc,0=is_forbidden" % (st.home_rawmcc, st.home_rawmnc)

def SIM_IsCachedDataReady(args):
    return BOOL_TRUE

def SIM_GetSmsTotalNumber(args):
    return smsdb.getSize(SM_STORAGE[0])

# Result_t SIM_GetSmsSca(SIM_SCA_DATA_t sca_data, UInt8 rec_no)
def SIM_GetSmsSca(args):
    rec_no = int(args[0])
    # refer to MS_GetDefaultSMSParamRecNum()
    if rec_no == 0:
        # return Service Center Address: +4791002100
        return '0=RESULT_OK,6=Len,0x91=Toa,"\x74\x09\x00\x12\x00"'
    else:
        return SMS_INVALID_INDEX

def SIM_GetSmsSatus(args):
   return smsdb.getStatus( SM_STORAGE[0], args[1])
    
# Result_t SIM_SendVerifyChvReq(UInt8 clientID, CHV_t chv_select, CHVString_t chv, CallbackFunc_t* sim_access_cb);
def SIM_SendVerifyChvReq(args):
    # Has at least 3 parameters ?
    if len(args) < 3:
        return RESULT_ERROR
    # Get parameters
    clientID   = args[0]
    chv_select = int(args[1])   # CHV selected (0,1)
    chv        = args[2]        # Attempted CHV
    # Already blocked PIN ?
    if st.PIN_attempts(chv_select+1) == 0:
        result = SIMACCESS_BLOCKED_CHV
    # Check PIN code
    elif chv == st.PIN_code(chv_select+1):
        st.PIN_OK(TRUE)
        st.PIN_attempts(chv_select+1,3)
        if chv_select == 0:

            service = gui.varRegisterGSM.get()
            if (service == REG_STATE_NORMAL_SERVICE) or (service == REG_STATE_ROAMING_SERVICE) or (service == REG_STATE_LIMITED_SERVICE):

                # send the Network Name as well if enabled
                if st.gui.varNetworkNameInd.get():
                    result = "\"%s\",\"%s\"" % (st.operatorLong, st.operatorShort)
                    q.append_message(MSG_NETWORK_NAME_IND, result, 15.0)

                # send GPRS state
                GPRS_service = gui.varRegisterGPRS.get()
                result = "%s,%s" % (GPRS_service,"0,0,0")
                q.append_message(MSG_REG_GPRS_IND, result, 10.0)

            # send the GSM state
            result = "%s,%s,%d,%d,%d,%d" % (service, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
            q.append_message(MSG_REG_GSM_IND, result, 8.0)

            result = "%s,%s" % ( SMS_SIM_SMS_READY, SMS_ME_SMS_READY )
            q.append_message(MSG_SMS_READY_IND, result,10.0)
        result = SIMACCESS_SUCCESS
    else: 
        st.PIN_OK(FALSE)
        if st.PIN_attempts(chv_select+1) > 0:
            st.PIN_attempts(chv_select+1,st.PIN_attempts(chv_select+1) - 1)
            result = SIMACCESS_INCORRECT_CHV
        else:
            result = SIMACCESS_BLOCKED_CHV
    # Add to asynch queue
    q.append_message(args[3], result)
    return RESULT_OK

def SIM_SendChangeChvReq(args):
    clientID    = args[0]
    chv_select  = int(args[1])
    old_chv     = args[2]
    new_chv     = args[3]
    # Already blocked PIN ?
    if st.PIN_attempts(chv_select+1) == 0:
        result = SIMACCESS_BLOCKED_CHV
    # Check old PIN code
    elif old_chv == st.PIN_code(chv_select+1):
        st.PIN_attempts(chv_select+1,3)
        # Save new PIN code
        st.PIN_code(chv_select+1, new_chv)
        result = RESULT_OK
    else: 
        if st.PIN_attempts(chv_select+1) > 0:
            st.PIN_attempts(chv_select+1,st.PIN_attempts(chv_select+1) - 1)
            result = SIMACCESS_INCORRECT_CHV
        else:
            result = SIMACCESS_BLOCKED_CHV
    # Add to asynch queue
    q.append_message(args[4], result)
    return RESULT_OK

def SIM_SendSetChv1OnOffReq(args):
    clientID    = args[0]
    chv         = args[1]
    enable_flag = int(args[2])

    if chv == st.PIN_code(1):
        # Correct PIN1, update flag
        gui.varPinEnabled.set(enable_flag)
        result = SIMACCESS_SUCCESS
    else:
        result = SIMACCESS_INCORRECT_CHV
    q.append_message(args[3] , result, 0.5);
    return RESULT_OK

def SIM_SendUnblockChvReq(args):
    # Get parameters
    clientID   = args[0]        # MPX channel number
    chv_select = int(args[1])   # CHV selected
    puk        = args[2]        # Attemted PUK
    new_chv    = args[3]        # Attempted new CHV
    # Check PUK attempts
    if st.PUK_attempts(chv_select+1) == 0:
        result = SIMACCESS_BLOCKED_PUK
    elif puk == st.PUK_code(chv_select+1):
        st.PIN_code(chv_select+1,new_chv)
        st.PIN_attempts(chv_select+1,3)
        st.PUK_attempts(chv_select+1,3)
        result = SIMACCESS_SUCCESS
    else: 
        st.PUK_attempts(chv_select+1, st.PUK_attempts(chv_select+1) - 1)
        result = SIMACCESS_INCORRECT_PUK
    # Add to asynch queue
    q.append_message(args[4], result, 2.0)
    return RESULT_OK


def SIM_SendSetOperStateReq(args):
    clientID    = args[0]
    oper_state  = int(args[1])
    chv2        = args[2]
    # Correct PIN2 ?
    if chv2 == st.PIN_code(2) or chv2 == '""':
        if oper_state == intUntilEqu(SIMOPERSTATE_RESTRICTED_OPERATION):
            st.FDN_enabled = TRUE
        elif oper_state == intUntilEqu(SIMOPERSTATE_UNRESTRICTED_OPERATION):
            st.FDN_enabled = FALSE
        result = SIMACCESS_SUCCESS
    else:
        result = SIMACCESS_INCORRECT_CHV
    q.append_message(args[3], result, 0.3)
    return RESULT_OK											 

# Result_t SIM_SendRemainingPinAttemptReq(UInt8 clientID, CallbackFunc_t* sim_access_cb);
def SIM_SendRemainingPinAttemptReq(args):
    if len(args) < 1:
        return RESULT_ERROR
    clientID = args[0]
    result = "%s,%d=PIN1,%d=PIN2,%d=PUK1,%d=PUK2" % (SIMACCESS_SUCCESS,
            st.PIN_attempts(1), st.PIN_attempts(2),
            st.PUK_attempts(1), st.PUK_attempts(2))
    q.append_message(args[1], result)
    return RESULT_OK

def SIM_SendPbkInfoReq(args):
    clientID = args[0]
    id       = SIMPBK_ID_t(args[1])
    callback = args[2]
    # Check which phonebook
    if id == SIMPBK_ADN:       # Abbreviated Dialing Number Phonebook
        total    = len(adn_pbk)
        alpha_sz = 14
    elif id == SIMPBK_FDN:     # Fixed Dialing Number Phonebook
        total = len(fdn_pbk)
        alpha_sz = 14
    elif id == SIMPBK_SDN:     # Service Dialing Number Phonebook
        total = len(sdn_pbk)
        alpha_sz = 14
    elif id == SIMPBK_LND:     # Last Number Dialed Phonebook
        total = len(lnd_pbk)
        alpha_sz = 14
    elif id == SIMPBK_MSISDN:  # MS ISDN Dialing Number Phonebook
        total = len(msisdn_pbk)
        alpha_sz = 14
    elif id == SIMPBK_BDN:	 # MS BDN Barred Dialing Number Phonebook
        total = len(msbdn_pbk)
        alpha_sz = 14    
    # SIM_PBK_INFO_t
    result = "%s,%s,%d=total,%d=alpha_sz" % (
            SIMACCESS_SUCCESS, id, total, alpha_sz)
    if callback != "":
        q.append_message(callback, result) 
    return RESULT_OK

def SIM_SendReadPbkReq(args):
    clientID  = args[0]
    id        = SIMPBK_ID_t(args[1])
    index     = int(args[2])
    end_index = int(args[3])
    callback1 = args[4]
    callback2 = args[5]
    # Check which phonebook
    if id == SIMPBK_ADN:        # ADN - Abbreviated Dialing Number
        pbk = adn_pbk
    elif id == SIMPBK_FDN:      # FDN - Fixed Dialing Number
        pbk = fdn_pbk
    elif id == SIMPBK_SDN:      # SDN - Service Dialing Number
        pbk = sdn_pbk
    elif id == SIMPBK_LND:      # LDN - Last Number Dialed
        pbk = lnd_pbk
    elif id == SIMPBK_MSISDN:   # MS ISDN Dialing Number
        pbk = msisdn_pbk
    elif id == SIMPBK_BDN:			# MS BDN Barred Dialing Number
    		pbk = msbdn_pbk
    else:
        return RESULT_ERROR
    # SIM_PBK_WRITE_RESULT_t
    for ix in range(index, end_index+1):
        name   = pbk[ix][0]
        number = pbk[ix][1]
        result = '%s,%s,%d,%d,%s,%s,"%s","%s",%d' % (
            SIMACCESS_SUCCESS, id, ix, end_index, NationalTON, UnknownNP,
            name, number, 0xFF)
        if callback1 != "":
            q.append_message(callback1, result)
        if callback2 != "":
            q.append_message(callback2, result)
    return RESULT_OK

def SIM_SendWritePbkReq(args):
    clientID = args[0]
    id       = SIMPBK_ID_t(args[1])
    index    = int(args[2])
    buffer_ton    = args[3]
    buffer_npi    = args[4]
    buffer_name   = args[5][1:-1]       # Remove ""
    buffer_digits = args[6][1:-1]       # Remove ""
    callback1 = args[7]
    # Check which phonebook
    if id == SIMPBK_ADN:        # ADN - Abbreviated Dialing Number
        pbk = adn_pbk
    elif id == SIMPBK_FDN:      # FDN - Fixed Dialing Number
        pbk = fdn_pbk
    elif id == SIMPBK_SDN:      # SDN - Service Dialing Number
        pbk = sdn_pbk
    elif id == SIMPBK_LND:      # LDN - Last Number Dialed
        pbk = lnd_pbk
    elif id == SIMPBK_MSISDN:   # MS ISDN Dialing Number
        pbk = msisdn_pbk
    elif id == SIMPBK_BDN:	    # MS BDN Barred Dialing Number
        pbk = msbdn_pbk    
    else:
        return RESULT_ERROR
    # Check index
    if index >= len(pbk):
        return RESULT_ERROR
    # insert the entry
    pbk[index] = [buffer_name, buffer_digits]
    # SIM_PBK_WRITE_RESULT_t
    result = '%s,%s,%d=ix,%s,%s,"%s","%s",%d' % (
            SIMACCESS_SUCCESS, id, index, buffer_ton, buffer_npi,
            buffer_name, buffer_digits, 0)
    if callback1 != "":
        q.append_message(callback1, result)
    return RESULT_OK


def SIM_SendUpdatePrefListReq(args):
    return RESULT_OK

def SIM_SendReadAcmMaxReq(args):
	result = '%s %d' % ( SIMACCESS_SUCCESS, st.getACMMAX )
	q.append_message( MSG_SIM_MAX_ACM_RSP, result ) 
	return RESULT_OK

def SIM_SendWriteAcmMaxReq(args):
	st.setACMMax( int(args[1]) )		  
	q.append_message( MSG_SIM_MAX_UPDATE_RSP, SIMACCESS_SUCCESS )
	return RESULT_OK

def SIM_SendReadAcmReq( args ):
	result = '%s %d' % (SIMACCESS_SUCCESS, st.getACM)
	q.append_message( MSG_SIM_ACM_VALUE_RSP, result )
	return RESULT_OK

def SIM_SendWriteAcmReq( args ):
	st.setACM( int(args[1]) )
	q.append_message( MSG_SIM_ACM_UPDATE_RSP, SIMACCESS_SUCCESS )
	return RESULT_OK
	
def SIM_SendIncreaseAcmReq( args ):
	st.setACM( st.getACM() + int(args[1]) )
	q.append_message( MSG_SIM_ACM_INCREASE_RSP, SIMACCESS_SUCCESS )
	return RESULT_OK

def SIM_SendReadSvcProvNameReq(args):
    clientID = int(args[0])
    # Have SVC and not on AT&T ?
    if gui.varHaveSVC.get() == TRUE and gui.varHomeOperator.get() != 0:
        result = 'SIMACCESS_SUCCESS,1=display,"Chess"'
    else:
        if gui.varHomeOperator.get() == 0:
            result = '0=SIMACCESS_SUCCESS,1=display,"AT&T Wireless"'
        elif gui.varHomeOperator.get() == 1:
            result = 'SIMACCESS_SUCCESS,1=display,"Netcom"'
        elif gui.varHomeOperator.get() == 2:
            result = 'SIMACCESS_SUCCESS,1=display,"Telenor"'
        else:
            result = 'SIMACCESS_SUCCESS,0=display,""'
    # SIM_SVC_PROV_NAME_t
    q.append_message(MSG_SIM_SVC_PROV_NAME_RSP, result)
    return RESULT_OK

# char* MS_ConvertPLMNNameStr(PLMN_NAME_t *plmn_name)
def MS_ConvertPLMNNameStr(args):
    return args[2]

# 
def MS_GetRegisteredLAC(args):
    return "1"


# int MS_GetDefaultSMSParamRecNum()
def MS_GetDefaultSMSParamRecNum(args):
    return '0=rec_no'




# Enable the testing for SIM Presence Test
# Result_t SIM_EnableSIMPresenceTest( void)
def SIM_EnableSIMPresenceTest(args):
    return RESULT_OK

# Disable the testing for SIM Presence Test
# Result_t SIM_DisableSIMPresenceTest(void)
def SIM_DisableSIMPresenceTest(args):
    return RESULT_OK

# Result_t SIM_SendRestrictedAccessReq(                
#     UInt8 clientID,                        // MPX channel number
#     APDUCmd_t command,                    // SIM command
#     APDUFileID_t file_id,                // SIM file id
#     UInt8 p1,                            // instruction param 1
#     UInt8 p2,                            // instruction param 2
#     UInt8 p3,                            // instruction param 3
#     UInt8 *data,                        // data
#     CallbackFunc_t* sim_access_cb        // Call back function
#     )

# void SIM_UpdatePinStatus(Boolean set_pin2, Boolean power_up)
def SIM_UpdatePinStatus(args):
    return VOID

# void SIM_SetDedicatedPinStatus(SIM_PIN_Status_t pin_status)
def SIM_SetDedicatedPinStatus(args):
    return VOID


# GID_DIGIT_t* SIM_GetGID1(void)
def SIM_GetGID1(args):
    return VOID # BUG

# GID_DIGIT_t* SIM_GetGID2(void)
def SIM_GetGID2(args):
    return VOID # BUG


# void SIM_PostStatusInd(Boolean chv1_verified, Boolean first_time_powerup)
def SIM_PostStatusInd(args):
    return VOID

# void SIM_PostInitSmsInd(void)
def SIM_PostInitSmsInd(args):
    return VOID

# void SIM_PostGeneralServiceInd(Boolean sim_general_service_ready, Boolean first_time_powerup)
def SIM_PostGeneralServiceInd(args):
    return VOID

# void SIM_PostAcmUpdateInd(void)
def SIM_PostAcmUpdateInd(args):
    return VOID

# void SIM_PostSmsMemAvailInd(Boolean avail)
def SIM_PostSmsMemAvailInd(args):
    return VOID

# void SIM_PostCachedDataReadyInd(void)
def SIM_PostCachedDataReadyInd(args):
    return VOID

def SIM_SendWholeBinaryEFileReadReq(args):
    q.append_message(args[3], SIMACCESS_SUCCESS, 3.0)
    return RESULT_OK

def SIM_SendLinearEFileUpdateReq(args):
		return RESULT_OK

def SIM_SendRecordEFileReadReq(args):
    q.append_message(args[3], SIMACCESS_SUCCESS, 3.0)
    return RESULT_OK

def SIM_SendEFileInfoReq(args):
    q.append_message( args[3], SIMACCESS_SUCCESS, 3.0)
    return RESULT_OK

def SIM_SendRecordEFileReadReq(args):
#	q.append_message(???
	return RESULT_OK

# UInt8 CC_GetCallClientID(UInt8 callIndex);
def CC_GetCallClientID(args):
    ci = int(args[0])
    return "%s=clientID" % st.ClientID(ci)

# UInt8* CC_GetConnectedLineID(UInt8 callIndex);
def CC_GetConnectedLineID(args):
    ci = int(args[0])
    #return "+4733331252=NUMBER"
    return '"%s"' % (st.callConnectedID(ci))

# UInt32 CC_GetLastCallCCM(void);
def CC_GetLastCallCCM(args):
    return "12345=CCM"

# UInt32 CC_GetLastCallDuration(void);
def CC_GetLastCallDuration(args):
    return "%.0f" % (st.lastCallDuration * 1000.0)

# UInt32 CC_GetCurrentCallDurationInMilliSeconds(UInt8 callIndex);
def CC_GetCurrentCallDurationInMilliSeconds(args):
    ci = int(args[0])
    return "%.0f" % (st.callDuration(ci) * 1000.0)

# UInt32 CC_GetLastDataCallRxBytes(void);
def CC_GetLastDataCallRxBytes(args):
    return "12345=RXBYTES"

# UInt32 CC_GetLastDataCallTxBytes(void);
def CC_GetLastDataCallTxBytes(args):
    return "12345=TXBYTES"

# UInt8 CC_GetNumofActiveCalls();
def CC_GetNumofActiveCalls(args):
    active = 0
    for ci in range(st.callIndexes()):
        # Is Active call ?
        if st.callState(ci) == CC_CALL_ACTIVE:
            active += 1
    return "%d=active" % active

# UInt8 CC_GetNumofHeldCalls();
def CC_GetNumofHeldCalls(args):
    held = 0
    for ci in range(st.callIndexes()):
        # Is Held call ?
        if st.callState(ci) == CC_CALL_HOLD:
            held += 1
    return "%d=held" % held

# UInt8 CC_GetNumOfMPTYCalls();
def CC_GetNumOfMPTYCalls(args):
    mpty = 0
    for ci in range(st.callIndexes()):
        if st.MultiPartyCall(ci):
            mpty += 1
    return "%d=mpty" % mpty

# Boolean CC_IsConnectedLineIDPresentAllowed(UInt8 callIndex);
def CC_IsConnectedLineIDPresentAllowed(args):
    return BOOL_FALSE

# Boolean CC_IsMultiPartyCall(UInt8 callIndex);
def CC_IsMultiPartyCall(args):
    ci = int(args[0])
    # Is this a multiparty call ?
    if st.MultiPartyCall(ci):
        return BOOL_TRUE
    return BOOL_FALSE

# Boolean CC_IsThereAlertingCall(void);
def CC_IsThereAlertingCall(args):
    for ci in range(st.callIndexes()):
        if st.activeCallIndex(ci):
            if st.callState(ci) == CC_CALL_ALERTING:
                # There is a alerting call
                return BOOL_TRUE
    # No alerting call
    return BOOL_FALSE

# Boolean CC_IsThereVoiceCall();
def CC_IsThereVoiceCall(args):
    for ci in range(st.callIndexes()):
        if st.activeCallIndex(ci):
            if st.callType(ci) == MOVOICE_CALL:
                # There is (at least) a voice call
                return BOOL_TRUE
    # No call waiting
    return BOOL_FALSE

# Boolean CC_IsThereWaitingCall();
def CC_IsThereWaitingCall(args):
    for ci in range(st.callIndexes()):
        if st.activeCallIndex(ci):
            if st.callState(ci) == CC_CALL_WAITING:
                # There is a call waiting
                return BOOL_TRUE
    # No call waiting
    return BOOL_FALSE

# Boolean CC_IsValidDTMF(UInt8 dtmfDigit),
def CC_IsValidDTMF(args):
    return BOOL_TRUE # BUG:

# void CC_ReportCallMeterVal( UInt8 callIndex, UInt32 callCCMUnit, UInt32 callDuration);
def CC_ReportCallMeterVal(args):
    return VOID

# void CC_ReportDataCallConnect(UInt8 callIndex);
def CC_ReportDataCallConnect(args):
    return VOID

# void CC_ReportMakeLinkRst(UInt8 ec_est_mode,UInt8 dc_mode);
def CC_ReportMakeLinkRst(args):
    return VOID


def GetGPRSMTPDPAutoRsp(args):
    return RESULT_OK

def GetNumofAlertingCalls(args):
    return RESULT_OK

# AttachState_t MS_GetGPRSAttachStatus(void)
def MS_GetGPRSAttachStatus(args):
    return RESULT_OK

# Boolean MS_IsDeRegisterInProgress(void)
def MS_IsDeRegisterInProgress(args):
    return RESULT_OK

# Boolean MS_IsRegisterInProgress(void)
def MS_IsRegisterInProgress(args):
    return RESULT_OK

# MSClass_t PDP_GetMSClass(void)
def PDP_GetMSClass(args):
    return RESULT_OK

# Result_t PDP_SetGPRSMinQoS(UInt8 cid,UInt8 numPara,UInt8 precedence,UInt8 delay,UInt8 reliability,UInt8 peak,UInt8 mean);
def PDP_SetGPRSMinQoS(args):
    return RESULT_OK

# Result_t PDP_SetGPRSQoS(UInt8 cid,UInt8 numPara,UInt8 precedence,UInt8 delay,UInt8 reliability,UInt8 peak,UInt8 mean);
def PDP_SetGPRSQoS(args):
    return RESULT_OK

# PCHQosProfile_t PDP_GetDefaultQos()
def PDP_GetDefaultQos(args):
    return VOID;

#Result_t PDP_SetPDPContext(UInt8 cid,UInt8 numParms,UInt8 *pdpType,UInt8 *apn,UInt8 *pdpAddr,UInt8 dComp,UInt8 hComp)
def PDP_SetPDPContext(args):
    return RESULT_OK

# Result_t PDP_SetMSClass(MSClass_t msClass);
def PDP_SetMSClass(args):
    return RESULT_OK

# Result_t PDP_GetGPRSActivateStatus(UInt8 *numActiveCid, GPRSActivate_t *outCidActivate)
def PDP_GetGPRSActivateStatus(args):
    return "0=RESULT_OK,%d=numActiveCid,%d=cid,%s" % (1,1, st.GPRSActivate)

def SetGPRSMTPDPAutoRsp(args):
    return RESULT_OK

# void SYS_DeRegisterForMSEvent(UInt8 clientID);
def SYS_DeRegisterForMSEvent(args):
    clientID = args[0]
    # NOTE: should be same as CLIENT_ID
    return RESULT_OK

# UInt8 SYS_RegisterForMSEvent(CallbackFunc_t* callback, UInt32 eventMask);
def SYS_RegisterForMSEvent(args):
    return "%d" % CLIENT_ID

# void SYS_ProcessPowerDowneq(args):
def SYS_ProcessPowerDownReq(args):
    # Add to asynch queue
    result = "2"
    q.append_message(MSG_POWER_DOWN_CNF, result, 2.0)
    # Bug POWER DOWN simulator
    return RESULT_OK


class RTCSimulator(threading.Thread):
    def __init__(self):
        self.lastFired = time.time()
        self.enabled = False
        self.alarm = self.lastFired
        threading.Thread.__init__(self, name="RTCSimulatorThread")
        self.start()

    def run(self):
        while True:
            self.checkAlarm()
            time.sleep(1)

    def checkAlarm(self):
        if self.enabled:
            t = time.time()
            if t >= self.alarm and self.alarm > self.lastFired:
                q.append_message(MSG_SIMULATOR_RTC_FIREALARM,"")
                self.lastFired = self.alarm


# UInt32 RTC_GetSeconds(void) // return RTC in seconds, from random point
def RTC_GetSeconds(args):
    SEC_HOUR = 60*60
    SEC_DAY = 24*SEC_HOUR
    SEC_YEAR = 365*SEC_DAY
    # BUG: 2*SEC_HOUR is UTC compensation?
    return "%.0f" % (time.time() - (30*SEC_YEAR + 7*SEC_DAY + 2*SEC_HOUR))

# UInt32 RTC_GetCount(void) // return RTC in seconds, from year 2000
def RTC_GetCount(args):
    SEC_HOUR = 60*60
    SEC_DAY = 24*SEC_HOUR
    SEC_YEAR = 365*SEC_DAY
    # BUG: 2*SEC_HOUR is UTC compensation?
    return "%.0f" % (time.time() - (30*SEC_YEAR + 7*SEC_DAY + 2*SEC_HOUR))

# UInt32 OSTIMER_RetrieveClock(void)
def OSTIMER_RetrieveClock(args):
    # return milliseconds since system start, not used
    return "%.0f=ms" % (1000.0 * (time.time() - system_start_time()))

# Ticks_t TIMER_GetValue(void)
def TIMER_GetValue(args):
    # return milliseconds since system start
    return "%.0f=ms" % (1000.0 * (time.time() - system_start_time()))

def RTC_DisableAlarm(args):
    rtc.enabled = False
    return VOID

def RTC_EnableAlarm(args):
    rtc.enabled = True
    return VOID

def RTC_SetAlarmTime(args):
    rtc.alarm = float(args[0])
    print "Alarm will expire in %.0f seconds." % (rtc.alarm - time.time())
    return VOID

def RTC_GetAlarmTime(args):
    return "%.0f" % rtc.alarm

def KPD_DRV_Init(args):
    return VOID

def KPD_DRV_Run(args):
    st.KPD_running(TRUE)
    return VOID

# void KPD_DRV_Register(KeypadCb_t KeyCb);
def KPD_DRV_Register(args):
    # BUG: should check running flag
    # perform callbacks when keys are pressed
    st.KPD_registered(TRUE)
    return VOID

# UInt32 KPD_DRV_GetLastKeyPressTime( void )
def KPD_DRV_GetLastKeyPressTime(args):
    # return time in milliseconds
    return "1"

def KPD_DRV_N_key_enable(args):
    return VOID

# void SYS_ProcessPowerUpReq( void )
def SYS_ProcessPowerUpReq(args):

    # If no SIM is inserted send a NO SIM indication and send a limited service
    # message 10 seconds after power-up.

    if st.SIM_removed() == TRUE:
        result = "%s,%s,%d,%d,%d,%d" % (REG_STATE_LIMITED_SERVICE, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
        q.append_message(MSG_REG_GSM_IND, result, 10.0)
        result = "%d" % ( 0 )

    # If the PIN is required send a limited service indication
    # after 10 seconds.

    else:
        if gui.varPinEnabled.get() == FALSE:
            service = gui.varRegisterGSM.get()
            if (service == REG_STATE_NORMAL_SERVICE) or (service == REG_STATE_ROAMING_SERVICE) or (service == REG_STATE_LIMITED_SERVICE):

            # send the Network Name as well if enabled
                if st.gui.varNetworkNameInd.get():
                    result = "\"%s\",\"%s\"" % (st.operatorLong, st.operatorShort)
                    q.append_message(MSG_NETWORK_NAME_IND, result, 15.0)

                    # send GPRS state
                    GPRS_service = gui.varRegisterGPRS.get()
                    result = "%s,%s" % (GPRS_service,"0,0,0")
                    q.append_message(MSG_REG_GPRS_IND, result, 10.0)

                    # send the GSM state
                    result = "%s,%s,%d,%d,%d,%d" % (service, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
                    q.append_message(MSG_REG_GSM_IND, result, 8.0)
            result = "%s,%s" % ( SMS_SIM_SMS_READY, SMS_ME_SMS_READY )
            q.append_message(MSG_SMS_READY_IND, result,20.0)
        else:
            result = "%s,%s,%d,%d,%d,%d" % (REG_STATE_LIMITED_SERVICE, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
            q.append_message(MSG_REG_GSM_IND, result, 10.0)
        result = "%d" % ( 1 )

    q.append_message(MSG_SIM_DETECTION_IND,result) 

    # Send a searching event as soon as the system
    # power's up

    result = "%s,%s" % (REG_STATE_SEARCHING,"0,0,0")
    q.append_message(MSG_REG_GSM_IND, result, 1.0)

    return VOID

# void SYS_ProcessNoRfReq( void )
def SYS_ProcessNoRfReq(args):

    # If no SIM is inserted send a NO SIM indication and send a limited service
    # message 10 seconds after power-up.

    if st.SIM_removed() == TRUE:
        result = "%s,%s,%d,%d,%d,%d" % (REG_STATE_LIMITED_SERVICE, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
        q.append_message(MSG_REG_GSM_IND, result, 5.0)
        result = "%d" % ( 0 )

    # If the PIN is required send a limited service indication
    # after 10 seconds.

    else:
        if gui.varPinEnabled.get() == FALSE:
		    result = "%s,%s" % ( SMS_SIM_SMS_READY, SMS_ME_SMS_READY )
		    q.append_message(MSG_SMS_READY_IND, result,10.0)
        else:
            result = "%s,%s,%d,%d,%d,%d" % (REG_STATE_LIMITED_SERVICE, GSMCAUSE_SUCCESS, 0, 0, 0, 0 )
            q.append_message(MSG_REG_GSM_IND, result, 10.0)
            
        result = "%d" % ( 1 )

    q.append_message(MSG_SIM_DETECTION_IND,result) 

    # Send a searching event as soon as the system
    # power's up

    result = "%s,%s" % (REG_STATE_NO_SERVICE,"0,0,0")
    q.append_message(MSG_REG_GSM_IND, result, 1.0)

    return VOID


# void AUDIO_SetSpeakerOn(void)
def AUDIO_SetSpeakerOn(args):
    return VOID

# void AUDIO_SetSpeakerOff(void)
def AUDIO_SetSpeakerOff(args):
    return VOID

# void AUDIO_SetMicrophoneOn(void)
def AUDIO_SetMicrophoneOn(args):
    return VOID

# void AUDIO_SetMicrophoneOff(void)
def AUDIO_SetMicrophoneOff(args):
    return VOID

# UInt8 AUDIO_GetMicrophoneGainSetting(void)
def AUDIO_GetMicrophoneGainSetting(args):
    return VOID

# Result_t AUDIO_SetMicrophoneGain(UInt8 gain)
# Description:  Set the micorphone gain
# Notes:        gain=0: mute the microphone; gain=1~8: actual gain=0dB~21dB (3dB steps)
def AUDIO_SetMicrophoneGain(args):
    gain = int(args[0])
    MAX_MICROPHONE_LEVELS = 8
    if gain > MAX_MICROPHONE_LEVELS:
        return AUDIO_INVALID_VOLUME_GAIN
    st.microphoneGain(gain)
    return RESULT_OK

# UInt8 AUDIO_GetMicrophoneGain (void)
def AUDIO_GetMicrophoneGain(args):
    return "%d=gain" % st.microphoneGain()

# Result_t AUDIO_SetSpeakerVol(UInt8 vol)
def AUDIO_SetSpeakerVol(args):
    vol = int(args[0])
    MAX_SPEAKER_LEVELS = 8
    if vol > MAX_SPEAKER_LEVELS:
        return AUDIO_INVALID_VOLUME_GAIN
    st.speakerVol(vol)
    return RESULT_OK

# UInt8 AUDIO_GetSpeakerVol (void)
def AUDIO_GetSpeakerVol(args):
    return "%d=vol" % st.speakerVol()

# Result_t AUDIO_PlayTone (SpeakerTone_t tone, UInt32 duration);
def AUDIO_PlayTone(args):
    return RESULT_OK

# Result_t AUDIO_StopPlaytone (void);
def AUDIO_StopPlaytone(args):
    return RESULT_OK


def MICROPHONE_On(args):
    st.microphoneOn(1)
    return VOID

def MICROPHONE_Off(args):
    st.microphoneOn(0)
    return VOID

def MICROPHONE_GetStatus(args):
    return "%d=on" % st.microphoneOn()

# UInt8 AUDIO_GetMicrophoneGain (void)
def AUDIO_GetMicrophoneGain(args):
    return "%d=gain" % st.microphoneGain()

def get_LID_status(args):
    return "%d=sts" %  (not gui.varLidClosed.get())

def VIBRATOR_On(args):
    vib_mode = int(args[0])
    return VOID

# UInt8 *MS_FindPLMNNameFromRawPLMN(UInt8 Format, UInt16 mcc, UInt16 mnc)
def MS_FindPLMNNameFromRawPLMN(args):
    Format = int(args[0])
    rawmcc = int(args[1])
    rawmnc = int(args[2])
    networkMcc = (rawmcc & 0xf0f) | ((rawmcc&0xf000) >> 8)
    networkMnc = ((rawmnc & 0x0f) << 4) | ((rawmnc&0xf0) >> 4)
#networkMcc = MS_PlmnConvertRawMcc(rawmcc);
#networkMnc = MS_PlmnConvertRawMnc(rawmcc, rawmnc);
    if networkMcc == 0x242 and networkMnc == 1:
        return '"Telenor N"'
    if networkMcc == 0x242 and networkMnc == 2:
        return '"Netcom N"'
    if networkMcc == 0x310 and networkMnc == 0x38:
        return '"AT&T WS"'
    return '"Unknown"'


#Boolean
#MS_GetPLMNNameByCode(UInt16 mcc,UInt16 mnc, char **long_name,char **short_name )
def MS_GetPLMNNameByCode(args):
    rawmcc = int(args[0])
    rawmnc = int(args[1])
    lac = int(args[2])
    networkMcc = (rawmcc & 0xf0f) | ((rawmcc&0xf000) >> 8)
    networkMnc = ((rawmnc & 0x0f) << 4) | ((rawmnc&0xf0) >> 4)
    if networkMcc == 0x242 and networkMnc == 1:
        return '"Telenor N", "TNOR"'
    if networkMcc == 0x242 and networkMnc == 2:
        return '"Netcom N", "N-COM"'
    if networkMcc == 0x310 and networkMnc == 0x38:
        return '"AT&T WS", "AWS"'
    return '"Unknown"'


# UInt16 MS_GetPlmnMCC(void)
def MS_GetPlmnMCC(args):
    return "0x%x=rawmcc" % (st.rawmcc)

# UInt8 MS_GetPlmnMNC(void)
def MS_GetPlmnMNC(args):
    return "0x%x=rawmnc" % (st.rawmnc)

# UInt16 MS_PlmnConvertRawMcc(UInt16 mcc)
def MS_PlmnConvertRawMcc(args):
    rawmcc = int(args[0])
    mcc = (rawmcc & 0xf0f) | ((rawmcc&0xf000) >> 8)
    return "0x%x=mcc" % (mcc)

# UInt16 MS_PlmnConvertRawMnc(UInt16 mcc, UInt16 mnc)
def MS_PlmnConvertRawMnc(args):
    rawmcc = int(args[0])
    rawmnc = int(args[1])
    mnc = ((rawmnc & 0x0f) << 4) | ((rawmnc&0xf0) >> 4)
    return "0x%x=mnc" % (mnc)

#Uint16 MS_ConvertStringToRawPlmnId(Uint *oper, PLMNId_t *plmn_id);
def MS_ConvertStringToRawPlmnId(args):
    return "0"

#Result_t MS_SetPowerDownTimer(UInt8 powerDownTimer)
def MS_SetPowerDownTimer(args):
	return RESULT_OK;

# void BATTMGR_RegisterStatus()
def BATTMGR_RegisterStatus(args):
    st.Battmgr_Active = TRUE
    return VOID

# Boolean MS_IsGSMRegistered(void)
# Is GSM carrier available at all?
def MS_IsGSMRegistered(args):
    if st.registeredGSM():
        return BOOL_TRUE
    return BOOL_FALSE

# RegisterStatus_t SYS_GetGSMRegStatus(void)
# GSM registration status
def SYS_GetGSMRegStatus(args):
    if st.registeredGSM():
        return REGISTERSTATUS_NORMAL
    # BUG: there are lots of other statuses...
    return REGISTERSTATUS_NO_NETWORK

# Boolean MS_IsGPRSRegistered(void)
# Is GPRS carrier available at all?
def MS_IsGPRSRegistered(args):
    if st.registeredGPRS():
        return BOOL_TRUE
    return BOOL_FALSE

# RegisterStatus_t SYS_GetGPRSRegStatus(void)
# GPRS registration status
def SYS_GetGPRSRegStatus(args):
    if st.registeredGPRS():
        return REGISTERSTATUS_NORMAL
    # BUG: there are lots of other statuses...
    return REGISTERSTATUS_NO_NETWORK


# RegisterStatus_t SYS_IsRegisteredGSMOrGPRS(void)
# GPRS or GSM registration status
def SYS_IsRegisteredGSMOrGPRS(args):
    if st.registeredGSM() or st.registeredGPRS():
        return BOOL_TRUE
    return BOOL_FALSE



################################  SMS API ##############################################################


sca_storage = [ ['4085061234', 0], ['55554321',0], ['8009997777',0]]

def SMS_SendSMSSrvCenterNumberUpdateReq(args):
    ton = int(args[1])
    inNumber = args[2]
    rec_no = int(args[3])
    if rec_no == 255:
        sca_storage[0][0] = inNumber
        sca_storage[0][1] = 0
    elif rec_no < len(sca_storage):
        sca_storage[rec_no][0] = inNumber
        sca_storage[rec_no][1] = 0
    else:
        return RESULT_ERROR
    return RESULT_OK

def SMS_GetSMSrvCenterNumber( args ):
    rec_no = int(args[0])
    result = RESULT_OK
    if rec_no == 255:
        number = sca_storage[0][0]
        ton = int(sca_storage[0][1])
    elif rec_no < len(sca_storage):
        number = sca_storage[rec_no][0]
        ton = int(sca_storage[rec_no][1])
    else:
        number = ''
        ton = 0
        result = RESULT_ERROR

    result += ',"%s",%d' % ( number, ton ) 
    return result

class SMSTxParams:
    def __init__(self):
        self.Alphabet = SMS_ALPHABET_DEFAULT
        self.msgClass = SMS_MSG_NO_CLASS
        self.codingGroup = 0
        self.isCompression = 0
        self.procId = 0
        self.replyPath = 0
        self.statusRptRequest = 0
        self.validatePeriod = 167
        self.msgRefNum = 0
        self.rejDupl = 0
        self.userDataHeaderInd = 0

smsTxParams = SMSTxParams()

preferred_storage = SMS_STO_TYPE_SM
status_change_mode = 0

#Result_t SMS_GetTxParamInTextMode( SmsTxTextModeParms_t* smsParms )
def SMS_GetTxParamInTextMode(args):
    result = "%s,%d,%d,%d,%d,%d,%d,%d,%s,%s,%d" % ( 
        RESULT_OK, 
        1, 
        smsTxParams.rejDupl, 
        smsTxParams.validatePeriod, 
        smsTxParams.statusRptRequest,
        smsTxParams.userDataHeaderInd,
        smsTxParams.replyPath,
        smsTxParams.procId,
        smsTxParams.msgClass,
        smsTxParams.Alphabet,
        smsTxParams.codingGroup )
    return result
     
#Result_t SMS_GetSmsTxParams( SmsTxParam_t* params )
def SMS_GetSmsTxParams(args):
    result = "%s,%s,%s,%d,%d,%d,%d,%d,%d,%d,%d,%d" % ( 
        RESULT_OK, 
        smsTxParams.Alphabet, 
        smsTxParams.msgClass, 
        smsTxParams.codingGroup, 
        smsTxParams.isCompression, 
        smsTxParams.procId, 
        smsTxParams.replyPath, 
        smsTxParams.statusRptRequest, 
        smsTxParams.validatePeriod, 
        smsTxParams.msgRefNum, 
        smsTxParams.rejDupl, 
        smsTxParams.userDataHeaderInd )
    return result

def SMS_SetSMSTxParamProcId(args):
    smsTxParams.procId = int(args[0])
    return RESULT_OK

def SMS_SetSMSParamCodingType(args):
    smsTxParams.Alphabet = args[0]
    smsTxParams.msgClass = args[1]
    return RESULT_OK

def SMS_SetSmsTxParamValidPeriod(args):
    smsTxParams.validatePeriod = int(args[0])
    return RESULT_OK

def SMS_SetSMSTxParamCompression(args):
    smsTxParams.isCompression = int(args[0])
    return RESULT_OK   

def SMS_SetSmsTxParamReplyPath(args):
	smsTxParams.replyPath = int(args[0])
	return RESULT_OK

def SMS_SetSmsTxParamStatusRptReqFlag(args):
    smsTxParams.statusRptRequest = int(args[0])
    return RESULT_OK

def SMS_SetSmsReadStatusChangeMode(args):
    status_change_mode = int(args[0])
    return VOID

def SMS_WriteSMSPduToSIMReq(args):
    return RESULT_OK

def SMS_GetLastTpMr(args):
    return "0"

def SMS_SetSMSPrefStorage(args):
    st.pref_storage = args[0]
    return RESULT_OK

def SMS_GetSMSPrefStorage(args):
   return st.pref_storage
 
def SMS_GetSMSStorageStatus(args):
    storageType = int(args[0])
    return "%s,%d,%d" % (RESULT_OK, smsdb.getFree(storageType), smsdb.getUsed(storageType))

def SMS_GetSmsStoredState(args):
    storageType = int(args[0])
    rec_no = int(args[1])
    record = smsdb.getRecord( storageType, rec_no, 0 )
    return "%s,%s" % (RESULT_OK, record[1] )

def SMS_SetSmsStoredState(args):
    storageType = int(args[0])
    rec_no = int(args[1])
    status = args[2]
    record= smsdb.getRecord(storageType, rec_no, 0)
    smsdb.putRecord(storageType, rec_no, record[0], status, record[2], record[3])
    return VOID

def SMS_ChangeSmsStatusReq(args):
    storageType = int(args[0])
    rec_no = int(args[2])
    status = 1
    record= smsdb.getRecord(storageType, rec_no, 0)
    smsdb.putRecord(storageType, rec_no, record[0], status, record[2], record[3])
    return VOID

# Result_t SMS_SendSMSReq(UInt8 clientID, UInt8* inNum, UInt8* inSMS,
#                         SmsTxParam_t* params, UInt8* inSca)
# Send a text SMS
def SMS_SendSMSReq(args):
    clientID = int(args[0])
    inNum    = args[1]
    inSMS    = args[2]
    result = "%s,%s,%s" % (
                    SMS_SUBMIT_RSP_TYPE_SUBMIT, MN_SMS_NO_ERROR, RESULT_OK)
    q.append_message(MSG_SMS_SUBMIT_RSP, result)
    return RESULT_OK

# Result_t SMS_ReadSmsMsgReq(UInt8 clientID, SmsStorage_t storageType,
#                            UInt16 rec_no)
def SMS_ReadSmsMsgReq(args):
    clientID    = args[0]
    storageType = int(args[1])
    rec_no      = int(args[2])
    record = smsdb.getRecord(storageType, rec_no, status_change_mode)
    if record != RESULT_ERROR:
        result = '%s,%s,%s,%s,%s,%s' % (
             record[0],             # MTI
             SIMACCESS_SUCCESS,     
             "%d=rec_no" % rec_no,
             record[1],             # Status
             record[3],             # PDU
             record[2])             # SMSC
    else:
        result = '%s,%s,%s,%s,%s' % (record[0], SMS_INVALID_INDEX, "0=rec_no", "", "[]") 
    q.append_message(MSG_SIM_SMS_DATA_RSP, result, 0.5)
    return RESULT_OK

def SMS_ListSmsMsgReq(args):
    clientID    = args[0]
    storageType = int(args[1])
    for rec_no in range( smsdb.getSize(storageType) ):
       if smsdb.isFree(storageType, rec_no) == False:
           record = smsdb.getRecord(storageType, rec_no, status_change_mode)
           result = '%s,%s,%s,%s,%s,%s' % (
                record[0],             # MTI
                SIMACCESS_SUCCESS,     
                "%d=rec_no" % rec_no,
                record[1],             # Status
                record[3],             # PDU
                record[2])             # SMSC
           q.append_message(MSG_SIM_SMS_DATA_RSP, result)
    # Use mti=255 to signal end of list
    q.append_message(MSG_SIM_SMS_DATA_RSP, '255=EOL,"","","","[]"')
    return RESULT_OK

# internal helper function
def convertToSMSDeliver(message):

    # convert the message to a SMS-DELIVER message to allow loopback
    # assume 1 octect for validity-period
    # assumes always more messages to send

    message = message.replace('"', '')

    # check for (TP-UDHI and TP-RP = 0xC0), and set TP-MMS 0x04 by default
    headerOctet = int(message[0:2], 16) & 0xC0 | 0x04
    headerOctetString = "%02X" % headerOctet

    # if the phone number length is odd, then round up to an even number
    phoneNumLen  = int(message[4:6], 16) + (int(message[4:6], 16) % 2)

    # skip the TP-Message-Reference Octet and get the Phone number
    # (address Len + address type + phone number)
    phoneNum = message[4:(4 + 2 + 2 + phoneNumLen)]

    # get the PID and DCS octets
    PID_DCS   = message[(4 + 2 + 2 + phoneNumLen):(4 + 2 + 2 +phoneNumLen) + 2 + 2]

    timeStamp = get_gsm_gmt()

    # skip the validity period Octet
    actualMsg = message[(4 + 2 + 2 + phoneNumLen) + 2 + 2 + 2 : ]

    message   = '"' + headerOctetString + phoneNum + PID_DCS + timeStamp + actualMsg + '"'
    return message

#Result_t SMS_WriteSMSPduReq(UInt8 clientID, UInt8 length, UInt8* inSmsPdu,
#                            Sms_411Addr_t* sca, SmsStorage_t storageType)
def SMS_WriteSMSPduReq(args):
    clientID = int(args[0])
    length = int(args[1])
    pdu = args[2]
    sca = args[3]
    storageType = int(args[4])
    if sca == '"[]"':
       sca = '"%s"' % (sca_storage[0])
    rec_no = smsdb.findFree( storageType)
    if rec_no != -1:
       smsdb.putRecord( storageType, rec_no, SMS_SUBMIT, SIMSMSMESGSTATUS_UNSENT, sca, pdu )
       result = "%s,%d=rec_no,%s,%s" % (SIMACCESS_SUCCESS, rec_no, storageType, SMS_STORAGE_WAIT_NONE )
    else:
       result = "%s,%d,%s,%s" % (SIMACCESS_MEMORY_ERR, 0, storageType, SMS_STORAGE_WAIT_NONE )
    q.append_message(MSG_SMS_WRITE_RSP_IND, result, 0.5)
    return RESULT_OK


# Result_t SMS_SendSMSPduReq(UInt8 clientID, UInt8 length, UInt8* inSmsPdu,
#                            Sms_411Addr_t* sca)
# Send a PDU SMS

def hoti(h):
   hexdigits='0123456789abcdef'
   for i in range(len(hexdigits)):
      if h == hexdigits[i]:
         return i

def SMS_SendSMSPduReq(args):
    clientID = int(args[0])
    length   = int(args[1])
    message  = args[2]
    inSca    = args[3]

    message = convertToSMSDeliver(message)
    gui.sms_content.set(message)
    gui.sms_smsc.set(inSca)
    if gui.varloopbackSMS.get() == TRUE:
        gui.send_sms_pdu()
    result = "%s,%s,%s" % (
                    SMS_SUBMIT_RSP_TYPE_SUBMIT, MN_SMS_NO_ERROR, RESULT_OK)
    q.append_message(MSG_SMS_SUBMIT_RSP, result )
    gui.blink_field(gui.sms_msg)
    return RESULT_OK

# Result_t SMS_DeleteSmsMsgByIndexReq(UInt8 clientID, SmsStorage_t storeType, UInt16 rec_no)
def SMS_DeleteSmsMsgByIndexReq(args):
    clientID    = args[0]
    storageType = int(args[1])
    rec_no = int(args[2])
    if storageType == int(ME_STORAGE[0]):
       storage_response = ME_STORAGE
    elif storageType == int(SM_STORAGE[0]):
       storage_response = SM_STORAGE
    else:
       return RESULT_ERROR
    smsdb.deleteRecord( storageType, rec_no )
    result = "%s,%d,%s" % (SIMACCESS_SUCCESS, rec_no, storage_response ) 
    q.append_message(MSG_SIM_SMS_STATUS_UPD_RSP, result )
    return RESULT_OK

def SMS_GetVmscNumber(args):
    return RESULT_ERROR

# SMS_BEARER_PREFERENCE_t  GetSMSBearerPreference(void)
def GetSMSBearerPreference(args):
    # BUG: should rerieve this one...
    return SMS_OVER_CS_ONLY

# void SetSMSBearerPreference(SMS_Bearer_Preference_t pref)
def SetSMSBearerPreference(args):
    # BUG: should store this one...
    return VOID

# Boolean SMS_IsSmsServiceAvail(void)
def SMS_IsSmsServiceAvail(args):
    if (gui.varRegisterGSM.get() == REG_STATE_NORMAL_SERVICE) or (gui.varRegisterGSM.get() == REG_STATE_ROAMING_SERVICE):
        return BOOL_TRUE
    else:
        return BOOL_FALSE

# Result_t SMS_SetVMIndOnOff(Boolean on_off)
def SMS_SetVMIndOnOff(args):
    return RESULT_OK

# Set the display preference for newly received SMS.
def SMS_SetNewMsgDisplayPref(args):
    msg_type = int(args[0])
    mode = int(args[1])
    st.display_pref[msg_type] = mode
    return RESULT_OK

def SMS_GetNewMsgDisplayPref(args):
    msg_type = int(args[0])
    result = [ SMS_MT, SMS_BM, SMS_DS, SMS_BFR ]
    return result[msg_type]

# Result_t SMS_GetVMWaitingStatus(pointer)
def SMS_GetVMWaitingStatus(args):
    return RESULT_ERROR

################################  SATK API ##############################################################

# Boolean SATKCmdResp(UInt16 clientID, SATK_EVENTS_t toEvent, UInt8 result1, 
#        UInt8 result2, SATKString_t* inText, UInt8 menuID)
def SATKCmdResp(args):
    clientID = int(args[0])
    toEvent  = int(args[1])
    result1  = int(args[2])
    result2  = int(args[3])
    inText   = args[4]
    unicode_type = int(args[5])
    menuID   = int(args[6])
    # Display text responce ?
    if toEvent == intUntilEqu(SATK_EVENT_DISPLAY_TEXT):
        if result1 == intUntilEqu(SATK_Result_CmdSuccess):
            print SATK_Result_CmdSuccess
        elif result1 == intUntilEqu(SATK_Result_SIMSessionEndSuccess):
            print SATK_Result_SIMSessionEndSuccess
        elif result1 == intUntilEqu(SATK_Result_BackwardMove):
            print SATK_Result_BackwardMove
        elif result1 == intUntilEqu(SATK_Result_NoRspnFromUser):
            print SATK_Result_NoRspnFromUser
        elif result1 == intUntilEqu(SATK_Result_MeUnableToProcessCmd):
            print SATK_Result_MeUnableToProcessCmd
        elif result1 == intUntilEqu(SATK_Result_BeyondMeCapability):
            print SATK_Result_BeyondMeCapability
        else:
            return BOOL_FALSE

    # Get inKey responce ?
    elif toEvent == intUntilEqu(SATK_EVENT_GET_INKEY):
        result = "%s" % ('"Got key %s from you."' % inText[1:len(inText)-1])
        q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)

    # Get input responce ?
    elif toEvent == intUntilEqu(SATK_EVENT_GET_INPUT):
        result = "%s" % ('"Got input %s from you."' % inText[1:len(inText)-1])
        q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)

    # Play tone responce ?
    elif toEvent == intUntilEqu(SATK_EVENT_PLAY_TONE):
        result = "%s" % ('"Now playing tone..."')
        q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)

    # Sub menu selection responce ?
    elif toEvent == intUntilEqu(SATK_EVENT_SELECT_ITEM):
        result = "%s" % ('"Item %d was selected."' % menuID)
        q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)

    elif toEvent == intUntilEqu(SATK_EVENT_SEND_SS):
        print SATK_EVENT_SEND_SS
    elif toEvent == intUntilEqu(SATK_EVENT_SEND_USSD):
        print SATK_EVENT_SEND_USSD
    elif toEvent == intUntilEqu(SATK_EVENT_SETUP_CALL):
        print SATK_EVENT_SETUP_CALL
    elif toEvent == intUntilEqu(SATK_EVENT_SETUP_MENU):
        print SATK_EVENT_SETUP_MENU
    # Root menu selection ?
    elif toEvent == intUntilEqu(SATK_EVENT_MENU_SELECTION):
        # Telenor ?
        if gui.varHomeOperator.get() == 1:
            if menuID == 1:
                result = "%s" % (
                    '"For mobilhandel se web:telenormobil.no/mobilhandel"')
            elif menuID == 2:
                result = "%s" % (
                    '"Disse tjenestene er forelopig ikke tilgjengelig"')
            else:
                result = "%s" % ('"BUG: Ikke gyldig valg menuID=%d !"' % menuID)
            q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)
        # Netcom ?
        elif gui.varHomeOperator.get() == 2:
            result = "%s" % '"BUG: Ikke gyldig valg!"'
            q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)
        # AT&T SATK test menu
        else:
            if menuID == 1: # SELECT_ITEM ?
                result = "%s,%d,%d,%d,[%s,%s,%s,%s,%s]" % (
                    '"SELECT_ITEM"',    # Title
                    0,                  # Title icon
                    0,                  # No alpha id
                    5,                  # Number of entries
                    '"Item 1"',         # First menu item
                    '"Item 2"',         # ...                 
                    '"Item 3"',
                    '"Item 4"',
                    '"Item 5"')
                q.append_message(MSG_SATK_EVENT_SELECT_ITEM, result)

            elif menuID == 2: # DISPLAY_TEXT ?
                result = "%s%s%s" % ('"The quick brown fox jumps over the lazy dog. ',
                                     'The quick brown fox jumps over the lazy dog. ',
                                     'The quick brown fox jumps over the lazy dog."' )
                q.append_message(MSG_SATK_EVENT_DISPLAY_TEXT, result)

            elif menuID == 3: # GET_INKEY ?
                result = "%s,%d,%s" % ('"GET\x11INKEY Prompt"', 0, S_IKT_DIGIT)
                q.append_message(MSG_SATK_EVENT_GET_INKEY, result)

            elif menuID == 4: # GET_INPUT ?
                result = "%d,%d,%s,%s,%s,%d" % (4, 8, '"GET\x11INPUT Prompt"','"<input>"', S_IKT_SMSDEFAULTSET, 0)
                q.append_message(MSG_SATK_EVENT_GET_INPUT, result)

            elif menuID == 5: # PLAY_TONE ?
                result = "%s,%s,%s" % ("PLAYING THIS TONE", S_TT_DEFAULTTONE, "100=ms")
                q.append_message(MSG_SATK_EVENT_PLAY_TONE, result)

            elif menuID == 6: # SEND_SS ?
                # Supplementary Services
                result = "%s,%s,%d,%d,%d,%s,%d" % (S_SST_SS_TYPE,'"12345678=num"',0,0,0,"SS STRING",0)
                q.append_message(MSG_SATK_EVENT_SEND_SS, result)

            elif menuID == 7: # SEND_USSD ?
                # Unstructured Supplementary Services Data
                result = "%s,%d,%s,%s,%d" % (S_SST_SS_TYPE,0,'"1984"','"*100#"',0 )
                q.append_message(MSG_SATK_EVENT_SEND_USSD, result)

            elif menuID == 8: # SETUP_CALL ?
                result = "%d=emergency,%s,%d=alpha,%s,%s,%s,%s,%s,%d,%d,%d" % (
                        0, S_CT_ONIDLE,0,'"12345678"', NationalTON, UnknownNP,
                        '"Do you want to dial 12345678 ?"', '"Dialing 12345678"', 0,0, 100)
                q.append_message(MSG_SATK_EVENT_SETUP_CALL, result)

            elif menuID == 9: # REFRESH ?
                print SATK_EVENT_REFRESH
            elif menuID == 10:# STK_SESSION_END
                print MSG_SATK_EVENT_STK_SESSION_END
                q.append_message(MSG_SATK_EVENT_STK_SESSION_END, "")
    elif toEvent == intUntilEqu(SATK_EVENT_REFRESH):
        print SATK_EVENT_REFRESH
    elif toEvent == intUntilEqu(SATK_EVENT_SEND_SHORT_MSG):
        print SATK_EVENT_SEND_SHORT_MSG
    return BOOL_TRUE

################################  SS API ##############################################################

# Result_t SS_SendCallForwardReq( 
#     UInt8                    clientID, 
#     SS_Mode_t                mode, 
#     SS_CallFwdReason_t        reason, 
#     SS_SvcCls_t                svcCls, 
#     UInt8                    waitToFwdSec, 
#     UInt8*                    number) ;
def SS_SendCallForwardReq(args):
    clientID = int(args[0])
    mode     = SS_Mode_t(args[1])
    reason   = SS_CallFwdReason_t(args[2]) # SS_CALLFWD_REASON_....
    ss_class = SS_SvcCls_t(args[3])        # SS_SVCCLS_....
    waitToFwdSec = args[4]
    number       = args[5]

    cf = st.getCallforward(reason)
    if cf == None:
        return RESULT_ERROR

    if gui.varSsFail.get() == TRUE:
        result = "%s" % ( GSMCAUSE_ERROR_SS_ERROR_STATUS )
    else:
        result = "%s" % ( GSMCAUSE_SUCCESS )
        for ix in range(len(cf.call_forward_class_info_list)):
            if ss_class == SS_SVCCLS_NOTSPECIFIED or cf.call_forward_class_info_list[ix].ss_class == ss_class:
                if mode == SS_MODE_DISABLE:
                    cf.call_forward_class_info_list[ix].activated = FALSE
                elif mode == SS_MODE_ENABLE:
                    cf.call_forward_class_info_list[ix].activated = TRUE
                    cf.call_forward_class_info_list[ix].forwarded_to_number = number[1:-1]
    q.append_message(MSG_SS_CALL_FORWARD_RSP, result, 0.2)
    return RESULT_OK

#Result_t SS_QueryCallForwardStatus(
#    UInt8              clientID, 
#    SS_CallFwdReason_t reason, 
#    SS_SvcCls_t        svcCls) ;
def SS_QueryCallForwardStatus(args):
    clientID = args[0]
    reason   = SS_CallFwdReason_t(args[1])
    ss_class = SS_SvcCls_t(args[2])

    cf = st.getCallforward(reason)
    if cf == None:
        return RESULT_ERROR

    # Set to fail by GUI ?
    if gui.varSsFail.get() == TRUE:
        result = '%s,%s,%d' % (
                GSMCAUSE_ERROR_SS_ERROR_STATUS,
                reason,
                0
        )
    else:
        gsmcause = GSMCAUSE_SUCCESS
        length = 0
        ss_info = ''
        for ix in range(len(cf.call_forward_class_info_list)):
            if ss_class == SS_SVCCLS_NOTSPECIFIED or ss_class == cf.call_forward_class_info_list[ix].ss_class:
                length = length + 1
                ss_info += ',[%d,%s,"%s"]' % (
                        cf.call_forward_class_info_list[ix].activated,
                        cf.call_forward_class_info_list[ix].ss_class,
                        cf.call_forward_class_info_list[ix].forwarded_to_number 
            )
        result = '%s,%s,%d%s' % (
                GSMCAUSE_SUCCESS,
                reason,
                length,
                ss_info
        )
    q.append_message(MSG_SS_CALL_FORWARD_STATUS_RSP, result, 0.2)
    return RESULT_OK

#
# Call Barring
#
#Result_t SS_SendCallBarringReq(
#    UInt8                   clientID, 
#    SS_Mode_t               mode,
#    SS_CallBarType_t        callBarType, 
#    SS_SvcCls_t             svcCls, 
#    UInt8*                  password) ;
def SS_SendCallBarringReq(args):
    clientID    = args[0]
    mode        = SS_Mode_t(args[1])
    callBarType = SS_CallBarType_t(args[2])
    svcCls      = SS_SvcCls_t(args[3])
    password    = args[4]

    # Look up in status
    cbs = st.getCallbarring(callBarType)
    if cbs == None:
        return RESULT_ERROR

    if gui.varSsFail.get() == TRUE:
        result = "%s" % ( GSMCAUSE_ERROR_SS_ERROR_STATUS )
    elif mode == SS_MODE_DISABLE:
        # Look up in status
        if password == cbs.cbPassword:
            gsmcause = GSMCAUSE_SUCCESS
            for ix in range(len(cbs.ss_activation_class_info)):
                if cbs.ss_activation_class_info[ix].ss_class == svcCls or svcCls == SS_SVCCLS_NOTSPECIFIED:
                    # Disable
                    cbs.ss_activation_class_info[ix].activated = 0
        else:
            gsmcause = GSMCAUSE_ERROR_NEGATIVE_PASSWD_CHECK
        result = "%s" % ( gsmcause )
    elif mode == SS_MODE_ENABLE:
        # Look up in status
        cbs = st.getCallbarring(callBarType)
        if password == cbs.cbPassword:
            gsmcause = GSMCAUSE_SUCCESS
            for ix in range(len(cbs.ss_activation_class_info)):
                if cbs.ss_activation_class_info[ix].ss_class == svcCls or svcCls == SS_SVCCLS_NOTSPECIFIED:
                    # Enable
                    cbs.ss_activation_class_info[ix].activated = 1
        else:
            gsmcause = GSMCAUSE_ERROR_NEGATIVE_PASSWD_CHECK
        result = "%s" % ( gsmcause )

    q.append_message(MSG_SS_CALL_BARRING_RSP, result, 2.0)
    return RESULT_OK

def SS_QueryCallBarringStatus(args):
    clientID    = args[0]
    callBarType = SS_CallBarType_t(args[1])
    svcCls      = SS_SvcCls_t(args[2])

    cbs = st.getCallbarring(callBarType)

    if cbs == None:
        return RESULT_ERROR

    # Set to fail by GUI ?
    if gui.varSsFail.get() == TRUE:
        result = "%s,%s,%d" % (
                GSMCAUSE_ERROR_SS_ERROR_STATUS,
                callBarType,
                0
        )
    else:
        length = 0
        ss_info = ''
        for ix in range(len(cbs.ss_activation_class_info)):
            if svcCls == cbs.ss_activation_class_info[ix].ss_class or svcCls == SS_SVCCLS_NOTSPECIFIED:
                length = length + 1 
                ss_info += ",[%d,%s]" % (
                        cbs.ss_activation_class_info[ix].activated,
                        cbs.ss_activation_class_info[ix].ss_class,
                )
        result = "%s,%s,%d%s" % (
                GSMCAUSE_SUCCESS,
                callBarType,
                length,
                ss_info
        )
    # result is CallBarringStatus_t
    q.append_message(MSG_SS_CALL_BARRING_STATUS_RSP, result, 2.0)
    return RESULT_OK

# Result_t SS_SendCallBarringPWDChangeReq(
#     UInt8                    clientID, 
#     SS_CallBarType_t        callBarType, 
#     UInt8*                    oldPwd, 
#     UInt8*                    newPwd) ;
def SS_SendCallBarringPWDChangeReq(args):
    clientID    = args[0]
    callBarType = args[1]
    oldPwd      = args[2]
    newPwd      = args[3]

    cbs = st.getCallbarring(callBarType)

    if cbs == None:
        return RESULT_ERROR

    # Set to fail by GUI ?
    if gui.varSsFail.get() == TRUE:
        result = GSMCAUSE_ERROR_SS_ERROR_STATUS
    elif oldPwd == cbs.cbPassword:
        cbs.cbPassword = newPwd
        result = RESULT_OK
    else:
        result = RESULT_ERROR
    q.append_message(MSG_SS_CALL_BARRING_PWD_CHANGE_RSP, result, 2.0)
    return RESULT_OK

# call waiting

# Result_t SS_SendCallWaitingReq(
#    UInt8                    clientID, 
#    SS_Mode_t                mode, 
#    SS_SvcCls_t                svcCls);
def SS_SendCallWaitingReq(args):
    clientID = args[0]
    mode = SS_Mode_t(args[1])
    svcCls = SS_SvcCls_t(args[2])
    result = RESULT_OK

    cw = st.getCallwaiting(svcCls)

    if cw == None:
	   return RESULT_ERROR

    # Set to fail by GUI ?
    if gui.varSsFail.get() == FALSE:
        if mode == SS_MODE_ENABLE:
            cw.activated = TRUE
        elif mode == SS_MODE_DISABLE:
            cw.activated = FALSE
        else:
            return RESULT_ERROR
        result = RESULT_OK
    else:
        result = RESULT_ERROR
    q.append_message(MSG_SS_CALL_WAITING_RSP, result, 3.0)
    return RESULT_OK

# Result_t SS_QueryCallWaitingStatus(
#     UInt8                    clientID, 
#     SS_SvcCls_t                svcCls);
def SS_QueryCallWaitingStatus(args):
    clientID = args[0]
    svcCls = SS_SvcCls_t(args[1])

    if gui.varSsFail.get() == TRUE:
        result = "%s,%d" % ( GSMCAUSE_ERROR_SS_ERROR_STATUS, 0 )
    elif svcCls == SS_SVCCLS_NOTSPECIFIED:
        # All Service Classes
        cw = st.getAllCallwaiting()
        result = "%s,%d" % ( GSMCAUSE_SUCCESS, len(cw) )
        for ix in range(len(cw)):
            result +=  ",[%d,%s]" % (
                        cw[ix].activated,
                        cw[ix].ss_class,
            )
    else:
        # Specific Service Class
        cw = st.getCallwaiting(svcCls)
        if cw == None:
           return RESULT_ERROR
        result = "%s,%d,[%d,%s]" % ( 
            GSMCAUSE_SUCCESS,
            1,
            cw.activated,
            cw.ss_class
        )
    q.append_message(MSG_SS_CALL_WAITING_STATUS_RSP, result, 3.0)
    return RESULT_OK

# Result_t SS_QueryCallingLineIDStatus( UInt8 clientID ) ;
def SS_QueryCallingLineIDStatus(args):
    if gui.varSsFail.get() == TRUE:
        gsmcause = GSMCAUSE_ERROR_SS_ERROR_STATUS
    else:
        gsmcause = GSMCAUSE_SUCCESS

    if gui.varCLIP.get() == TRUE:
        status = 1
    else:
        status = 0

    result = "%s,%d" % (gsmcause, status) 
    q.append_message(MSG_SS_CALLING_LINE_ID_STATUS_RSP, result );
    return RESULT_OK

# Result_t SS_QueryConnectedLineIDStatus( UInt8 clientID ) ;
def SS_QueryConnectedLineIDStatus(args):
    if gui.varSsFail.get() == TRUE:
        gsmcause = GSMCAUSE_ERROR_SS_ERROR_STATUS
    else:
        gsmcause = GSMCAUSE_SUCCESS

    if gui.varCOLP.get() == TRUE:
        status = 1
    else:
        status = 0

    result = "%s,%d" % (gsmcause, status) 
    q.append_message(MSG_SS_CONNECTED_LINE_RESTRICTION_STATUS_RSP, result );
    return RESULT_OK

# Result_t SS_QueryCallingLineRestrictionStatus( UInt8 clientID ) ;
def SS_QueryCallingLineRestrictionStatus(args):
    if gui.varSsFail.get() == TRUE:
        gsmcause = GSMCAUSE_ERROR_SS_ERROR_STATUS
    else:
        gsmcause = GSMCAUSE_SUCCESS

    if gui.varCLIR.get() == TRUE:
        status = 1
    else:
        status = 0

    result = "%s,%d" % (gsmcause, status) 
    q.append_message(MSG_SS_CALLING_LINE_RSTRICTION_STATUS_RSP, result );
    return RESULT_OK

# Result_t SS_QueryConnectedLineRestrictionStatus( UInt8 clientID ) ;
def SS_QueryConnectedLineRestrictionStatus(args):
    if gui.varSsFail.get() == TRUE:
        gsmcause = GSMCAUSE_ERROR_SS_ERROR_STATUS
    else:
        gsmcause = GSMCAUSE_SUCCESS

    if gui.varCOLR.get() == TRUE:
        status = 1
    else:
        status = 0

    result = "%s,%d" % (gsmcause, status) 
    q.append_message(MSG_SS_CONNECTED_LINE_RESTRICTION_STATUS_RSP, result );
    return RESULT_OK
#
# USSD
#
# Result_t SS_SendUSSDConnectReq(UInt8 clientID, UInt8* phoneNum )
def SS_SendUSSDConnectReq(args):
    clientID = args[0]
    phoneNum = args[1]
    result2 = "%d," % 11
    result2 += "%s" % '"Hello World"'
#    q.append_message(MSG_USSD_DATA_RSP, result, 1.0)
#    q.append_message(MSG_USSD_SESSION_END_IND, result, 2.0)
    q.append_message(MSG_USSD_CALLINDEX_IND, "", 1.0)
    q.append_message(MSG_USSD_DATA_RSP, result2, 2.0)
    return RESULT_OK

# Result_t SS_SendUSSDData( UInt8 clientID, CallIndex_t ussd_id, UInt8 dcs,
#                           UInt8 len, UInt8* ussdString ) 
def SS_SendUSSDData(args):
    clientID    = args[0]
    ussd_id     = args[1]
    dcs         = args[2]
    len         = int(args[3])
    ussdString  = args[4]
    result = "%d,\"%s\"" % (len, ussdString)
	# Call Index 0 is MO, 1 is MT
    if ussd_id == 0:
       q.append_message(MSG_USSD_DATA_RSP, result)
    else:
       q.append_message(MSG_USSD_DATA_IND, result)

    return RESULT_OK

# Result_t SS_EndUSSDConnectReq( UInt8 clientID, CallIndex_t ussd_id ) 
def SS_EndUSSDConnectReq(args):
    clientID = args[0]
    ussd_id  = args[1]
    q.append_message(MSG_USSD_SESSION_END_IND,"")
    return RESULT_OK


# void MS_SearchAvailablePLMN(void)
def MS_SearchAvailablePLMN(args):
    # Array of SEARCHED_PLMNId_t:
    # UInt16 mcc;           // unconverted
    # UInt16 something;
    # UInt8 mnc;            // unconverted
    # Boolean is_forbidden; // TRUE, if forbidden

    # Cause 
    result  = "%d," % 0
    # Number of records
    result += "%d," % 3
    # AT&T
    result += "[%d=mcc,%d=lac,%d=mnc,0=false]," % (0x1300, 0x0000, 0x83)
    # Telenor
    result += "[%d=mcc,%d=lac,%d=mnc,0=false]," % (0x42f2, 0x0000, 0x10)
    # Netcom
    result += "[%d=mcc,%d=lac,%d=mnc,1=true]"  % (0x42f2, 0x0000, 0x20)
    q.append_message(MSG_PLMNLIST_IND, result, 3.0)
    return VOID

# void MS_AbortSearchPLMN(void)
def MS_AbortSearchPLMN(args):
    # Probably don't need to do anything...
    return VOID

# Result_t MS_PlmnSelect(
#           UInt8 clientID, 
#           PlmnSelectMode_t selectMode, 
#           PlmnSelectFormat_t format, 
#           char *plmnValue,
#           Boolean *netReqSent);
def MS_PlmnSelect(args):
    clientID    = args[0]
    selectMode  = int(args[1])
    format      = int(args[2])
    plmnValue   = args[3]
    netReqSent  = args[4]

    result = "%d" % 6
    q.append_message(MSG_PLMN_SELECT_CNF, result, 3.0)
    return RESULT_OK

def MS_GetPlmnMode(args):
    return "0"
    
def MS_SetPlmnMode(args):
    return VOID

def MS_GetPlmnFormat(args):
    return "PLMN_FORMAT_LONG"
    
def SIM_GetSmsParamRecNum(args):
    result = "%s,%d=rec_no" % ( RESULT_OK, len(sca_storage) )
    return result

# bool
def SIM_IsALSEnabled(args):
    if gui.varALSEnabled.get() == TRUE:
        return BOOL_TRUE
    return BOOL_FALSE

def SIM_IsMoSmsCallCtrEnabled(args):
    return BOOL_FALSE

#
# int8
def SIM_SetAlsDefaultLine(args):
    line        = int(args[0])
    st.ALS_default_line = line
    return RESULT_OK

#
# UInt8 SIM_GetAlsDefaultLine(void);
def SIM_GetAlsDefaultLine(args):
    return "%d" % (st.ALS_default_line)

    
#UInt8 *SYSPARM_GetIMEI( void );            // Return the IMEI
def SYSPARM_GetIMEI(args):
#            123456789012345678
#            XttttttFFssssssXXX
    return '"300470198000001000"'
    

# PowerOnCause_t SYS_GetMSPowerOnCause(void)
def SYS_GetMSPowerOnCause(args):
    return "%s" % gui.varPowerOnCause.get()

# SystemState_t SYS_GetSystemState(void)
def SYS_GetSystemState(args):
	return "SYSTEM_STATE_ON"	# **FixMe** Must implement

# UInt8 SLEEP_AllocId( void );
def SLEEP_AllocId(args):
    return "%d=id" % 1

# void SLEEP_EnableDeepSleep( UInt8 id );
def SLEEP_EnableDeepSleep(args):
    return VOID

# void SLEEP_DisableDeepSleep( UInt8 id ); 
def SLEEP_DisableDeepSleep(args):
    return VOID

# UInt32 GetDeepSleepIDStatus( void );
def GetDeepSleepIDStatus(args):
    return "%d=id" % 1

# void MS_SetStartBand( UInt8 startBand );
def MS_SetStartBand(args):
    return VOID


# *EK* BUG: should do callback...
# PMU_Read(addr)
def PMU_Read(args):
    return VOID

# void AT_ApiMeasurmentReportReq(Boolean on_off);
def AT_ApiMeasurmentReportReq(on_off):
    st.setFieldTest( on_off )
    return VOID


###################### Data Account API ################################################

PCHContextTbl = [ CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED,
                  CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED, CONTEXT_UNDEFINED ]

class contextEntry:
    def __init__(self):
        self.cid = 0
        self.priCid = 0
        self.isSec = FALSE
        self.nsapi = 0
        self.ssapi = 0
        self.state = CONTEXT_UNDEFINED
        self.pdpType = ''
        self.apn = ''
        self.addr = 0
        self.qos = []
        self.qosmin = []
        self.xid = []
        self.iptype = []

class contextDb:
    def __init__(self):
        self.size = 10
        self.db = []
        for i in range(self.size):
            self.db.append(contextEntry())
    def getEntry(self, i):
        return self.db[i]
    def clearEntry(self,i):
	    self.db[i].state = CONTEXT_UNDEFINED
    def getSize(self):
        return self.size

PDPDefaultContextDb = contextDb()

class accountEntry:
    def __init__(self):
        self.acctID = 0
        self.acctType = DATA_ACCOUNT_NOT_USED
        self.username = ''
        self.password = ''
        self.staticIPAddr = 0
        self.priDnsAddr = 0
        self.sndDnsAddr = 0
        self.dataSentSize = 0
        self.dataRcvSize = 0
        self.acctLock = 0
        self.u = []
    def clear(self):
        self.acctID = 0
        self.acctType = DATA_ACCOUNT_NOT_USED
        self.username = ''
        self.password = ''
        self.staticIPAddr = 0
        self.priDnsAddr = 0
        self.sndDnsAddr = 0
        self.dataSentSize = 0
        self.dataRcvSize = 0
        self.acctLock = 0
        self.u = []

class accountDb:
    def __init__(self):
        self.size = 10
        self.db = []
        for i in range(self.size):
            self.db.append(accountEntry())
    def getEntry(self, acctID):
        return self.db[acctID-1]
    def deleteEntry(self, acctID):
        self.db[acctID-1].clear()
    def clearAll(self):
        for i in range(self.size):
            self.db[i].clear()
    def getSize(self):
        return self.size

dataAccountDb = accountDb()


def DATA_InitAllDataAcct():
    dataAccountDb.clearAll()
    return VOID

def DATA_IsAcctIDValid( args ):
    acctID=int(args)
    result = FALSE
    if acctID > 0 and acctID <= dataAccountDb.getSize():
        result = TRUE
    return result

def DATA_CreateGPRSDataAcct( args ):
    acctID = int(args[0])
    gprsSettings = args[1:12]
    qos = args[12:17]
    if DATA_IsAcctIDValid(acctID) == TRUE:
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_NOT_USED:
            for cid in range(len(PCHContextTbl)):
                if PCHContextTbl[cid] == CONTEXT_UNDEFINED:
                    PCHContextTbl[cid] = CONTEXT_DEFINED
                    account.acctID        = acctID
                    account.acctType      = DATA_ACCOUNT_GPRS
                    account.username      = gprsSettings[1]      
                    account.password      = gprsSettings[2]      
                    account.staticIPAddr  = int(gprsSettings[5]) 
                    account.priDnsAddr    = int(gprsSettings[6]) 
                    account.sndDnsAddr    = int(gprsSettings[7]) 
                    account.dataSentSize  = 0                    
                    account.dataRcvSize   = 0     
                    account.acctLock      = 0               
                    account.u             = [ cid, gprsSettings[8]]         # [CID,Authentication Type]  

                    context         = PDPDefaultContextDb.getEntry(cid)
                    context.cid     = cid               
                    context.priCid  = 0                 
                    context.isSec   = FALSE             
                    context.nsapi   = 0                 
                    context.ssapi   = PCH_SAPI_3        
                    context.state   = CONTEXT_DEFINED   
                    context.pdpType = gprsSettings[3]   
                    context.apn     = gprsSettings[4]   
                    context.xid     = [ gprsSettings[9], gprsSettings[10] ] # [Data,Header] Compression
                    print context.xid
                    context.qos     = qos
                    DATA_UpdateAccountToFileSystem()
                    return RESULT_OK
            return DATA_GPRS_NO_CID_AVAILABLE
        return DATA_ACCTID_IN_USED
    return DATA_INVALID_ACCTID


def DATA_CreateCSDDataAcct( args ):
    acctID = int(args[0])
    csdSettings = args[1:14]
    if DATA_IsAcctIDValid(acctID) == TRUE:
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_NOT_USED:
            account.acctID       = acctID
            account.acctType     = DATA_ACCOUNT_CSD
            account.username     = csdSettings[1]
            account.password     = csdSettings[2]
            account.staticIPAddr = int(csdSettings[3])
            account.priDnsAddr   = int(csdSettings[4])
            account.sndDnsAddr   = int(csdSettings[5])
            account.dataSentSize = 0
            account.dataRcvSize  = 0
            account.acctLock     = 0 
            account.u = [ csdSettings[6], csdSettings[7], csdSettings[8], csdSettings[9], csdSettings[10], csdSettings[11], csdSettings[12] ]
            DATA_UpdateAccountToFileSystem()
            return RESULT_OK
        return DATA_ACCTID_IN_USED
    return DATA_INVALID_ACCTID

def DATA_DeleteDataAcct( args ):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID) == TRUE:
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            if PCHContextTbl[cid] == CONTEXT_DEFINED:
                PCHContextTbl[cid] = CONTEXT_UNDEFINED
                PDPDefaultContextDb.clearEntry(cid)
            else:
                return RESULT_ERROR
        dataAccountDb.deleteEntry(acctID)
        DATA_UpdateAccountToFileSystem()
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetGPRSContext( args ):
    acctID = int(args[0])
    result = ""
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            result = "%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d,[%d,%d,%d,%d,%d]" % (
                account.acctID,
                account.username,
                account.password,
                context.pdpType,
                context.apn,
                account.staticIPAddr,
                account.priDnsAddr,
                account.sndDnsAddr,
                account.u[1],
                context.xid[0],
                context.xid[1],
                context.qos[0],
                context.qos[1],
                context.qos[2],
                context.qos[3],
                context.qos[4]
			)
    return result
    
def DATA_GetCSDContext( args ):
    acctID = int(args[0])
    result = ""
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        if account.acctType == DATA_ACCOUNT_CSD:
            result = "%d,\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",\"%s\",%d,%d,%d,%d,%d,%d" % (
                account.acctID,
                account.username,
                account.password,
                account.staticIPAddr,
                account.priDnsAddr,
                account.sndDnsAddr,
                account.u[0],                           # Dialed Number
                account.u[1],                           # Dial Type
                account.u[2],                           # Baud Rate
                account.u[3],                           # Error Correction Type
                account.u[4],                           # Compression Type
                account.u[5],                           # Compression Enabled
                account.u[6]                            # Connection Element
            )
   	return result
                
def DATA_SetUsername( args ):
    acctID = int(args[0])
    username = args[1]
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        if username != '':
            account.username = username
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetUsername(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        result = '%s' % ( account.username )
        return result
    return ''

def DATA_SetPassword( args ):
    acctID = int(args[0])
    password = args[1]
    if DATA_IsAcctIDValid( acctID ):
        if password != '':
            account = dataAccountDb.getEntry( acctID )
            account.password = password
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetPassword(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        result = '%s' % ( account.password )
        return result
    return ''

def DATA_SetStaticIPAddr( args ):
    acctID = int(args[0])
    addr = int(args[1])
    if DATA_IsAcctIDValid( acctID ):
        if addr != '':
            account = dataAccountDb.getEntry( acctID )
            account.staticIPAddr = addr
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetStaticIPAddr(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        result = '%d' % ( account.staticIPAddr )
        return result
    return ''

def DATA_SetPrimaryDnsAddr( args ):
    acctID = int(args[0])
    addr = int(args[1])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        account.priDnsAddr = addr
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetPrimaryDnsAddr(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        result = '%d' % ( account.priDnsAddr )
        return result
    return ''

def DATA_SetSecondDnsAddr( args ):
    acctID = int(args[0])
    addr = int(args[1])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        account.sndDnsAddr = addr
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetSecondDnsAddr(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        result = '%d' % ( account.sndDnsAddr )
        return result
    return ''

def DATA_SetDataCompression( args ):
    acctID = int(args[0])
    on = args[1]
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            context.xid[0] = on
        elif dataAccount[acctID-1] == DATA_ACCOUNT_CSD:
            account.u[5] = on
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetDataCompression(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid( acctID ):
        account = dataAccountDb.getEntry( acctID )
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            return context.xid[0]
        elif account.acctType == DATA_ACCOUNT_CSD:
            return account.u[5]
    return FALSE

def DATA_GetAcctType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry( acctID )
        return account.acctType
    return DATA_ACCOUNT_NOT_USED

def DATA_GetEmptyAcctSlot(args):
    for i in range(dataAccountDb.getSize()):
        account = dataAccountDb.getEntry(i+1)
        if account.acctType == DATA_ACCOUNT_NOT_USED:
            return "%d" % (i + 1)
    return '0'

def DATA_GetCidFromDataAcctID(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            return "%d" % (account.u[0])
    return '0'

def DATA_GetAcctIDFromCid(args):
    cid = int(args[0])
    for i in range(dataAccountDb.getSize()):
        account = dataAccountDb.getEntry(i+1)
        if account.u[0] == cid:
            return "%d" % (i + 1)
    return '0'

def DATA_GetDataSentSize(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return "%d" % (account.dataSentSize)
    return '0'

def DATA_GetDataRcvSize(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return "%d" % (account.dataRcvSize)
    return '0'

def resetDataSize(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.dataRcvSize = 0
        account.dataSentSize = 0
    return '0'

def addDataSentSize(args):
    acctID = int(args[0])
    val = int(args[1])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.dataSentSize = account.dataSentSize + val;
    return '0'

def addDataRcvSize(args):
    acctID = int(args[0])
    val = int(args[1])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.dataRcvSize = account.dataRcvSize + val;
    return '0'

def DATA_SetGPRSPdpType(args):
    acctID = int(args[0])
    pdpType = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            context.pdpType = pdpType
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetGPRSPdpType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            return context.pdpType
    return ''

def DATA_SetGPRSApn(args):
    acctID = int(args[0])
    apn = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            context.apn = apn
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetGPRSApnType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            return context.apn
    return ''

def DATA_SetAuthenMethod(args):
    acctID = int(args[0])
    authenType = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            account.u[1] = authenType
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetAuthenMethod(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            return account.u[1]
    return ''

def DATA_SetGPRSHeaderCompression(args):
    acctID = int(args[0])
    on = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            context.xid[1] = on
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetGPRSHeaderCompression(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            return context.xid[1]
    return ''

def DATA_SetGPRSQos(args):
    acctID = int(args[0])
    qos = args[1:6]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            context.qos = qos
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetGPRSQos(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        if account.acctType == DATA_ACCOUNT_GPRS:
            cid = account.u[0]
            context = PDPDefaultContextDb.getEntry(cid)
            result = "[%s,%s,%s,%s,%s]" % (
                context.qos[0],
                context.qos[1],
                context.qos[2],
                context.qos[3],
                context.qos[4]
            )
            return result
    return ''

def DATA_SetCSDDialNumber(args):
    acctID = int(args[0])
    dialnumber = args[1]
    if DATA_IsAcctIDValid(acctID):
        if dialnumber != '':
            account = dataAccountDb.getEntry(acctID)
            account.u[0] = dialnumber
            DATA_UpdateAccountToFileSystem();
            return RESULT_OK
        return RESULT_ERROR
    return DATA_INVALID_ACCTID

def DATA_GetCSDDialNumber(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[0]
    return ''

def DATA_SetCSDDialType(args):
    acctID = int(args[0])
    dialtype = args[1]
    if DATA_IsAcctIDValid(acctID):
         account = dataAccountDb.getEntry(acctID)
         account.u[1] = dialtype
         DATA_UpdateAccountToFileSystem();
         return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetCSDDialType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[1]
    return ''

def DATA_SetCSDBaudRate(args):
    acctID = int(args[0])
    baudrate = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.u[2] = baudrate
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetCSDBaudRate(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[2]
    return ''

def DATA_SetCSDErrCorrectionType(args):
    acctID = int(args[0])
    ectype = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.u[3] = ectype
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetCSDErrCorrectionType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[3]
    return ''

def DATA_SetCSDDataCompType(args):
    acctID = int(args[0])
    dctype = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.u[4] = dctype
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetCSDDataCompType(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[4]
    return ''

def DATA_SetCSDConnElement(args):
    acctID = int(args[0])
    ce = args[1]
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.u[5] = ce
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetCSDConnElement(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return account.u[5]
    return ''

def DATA_SetAcctLock(args):
    acctID = int(args[0])
    ce = int(args[1])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        account.acctLock = ce
        DATA_UpdateAccountToFileSystem();
        return RESULT_OK
    return DATA_INVALID_ACCTID

def DATA_GetAcctLock(args):
    acctID = int(args[0])
    if DATA_IsAcctIDValid(acctID):
        account = dataAccountDb.getEntry(acctID)
        return "%d" % (account.acctLock)
    return ''

def DATA_UpdateAccountToFileSystem():
    MSDATA_UpdateDataAcctReq()
     
############################# MSDATA API ##################################################################
 

def MSDATA_InitMsData():
    if MSDATA_RetrieveDataAcct() == RESULT_ERROR:
        DATA_InitAllDataAcct()
    if MSDATA_RetrieveMsData() == RESULT_ERROR:
        print "fixme - initialize SMS database"

    else:
        DATA_InitAllDataAcct()
    
def MSDATA_UpdateMsData( MsData ):
    if os.path.exists('smsdata.dat'):
        f1=open('smsdata.dat','rb')
        pickle.dump(MsData, f1, True)
        f1.close()

def MSDATA_RetrieveMsData():
    if os.path.exists('smsdata.dat'):
        f1=open('smsdata.dat','rb')
        #fixme
        #sms_me = pickle.load(f1)
    	f1.close()
        return RESULT_OK
    else:
        return RESULT_ERROR


def MSDATA_UpdateDataAcct():
    global dataAccountDb, PDPDefaultContextDb
    f1=file('dataacct.dat', 'wb')
    pickle.dump(dataAccountDb, f1, True)
    pickle.dump(PDPDefaultContextDb, f1, True)
    f1.close()
    return RESULT_OK

def MSDATA_RetrieveDataAcct():
    global dataAccountDb, PDPDefaultContextDb
    if os.path.exists('dataacct.dat'):
        f1=open('dataacct.dat','rb') 
        dataAccountDb = pickle.load(f1)
        PDPDefaultContextDb=pickle.load(f1)
        for i in range(PDPDefaultContextDb.getSize()):
            context = PDPDefaultContextDb.getEntry(i)
            cid = context.cid
            if context.state == CONTEXT_DEFINED:
            	PCHContextTbl[cid] = context.state
        f1.close()
        return RESULT_OK
    else:
        return RESULT_ERROR

def MSDATA_UpdateAllMsDataReq():
    MSDATA_UpdateMsData()
    MSDATA_UpdateDataAcct()

def MSDATA_UpdateDataAcctReq():
    MSDATA_UpdateDataAcct()



#######################################################################
# API Function dispatcher
#######################################################################
def callApiFunc(func, args):
    #try:
    result = eval(func)(args)
    #except NameError, msg:
        # Unknown API function 
    #    result = RESULT_UNKNOWN
    #except:
    #    pass
    print tod(), "=>Result:", result
    return result + "\n"



    
