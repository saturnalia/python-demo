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

import string
from common import *

# Broadcom enums
from mstypes import *
from mstypes_enum import *
from resultcode import *
from callctrl import *
#from moremsgs import *
from dataComm import *
from pchtypes import *

def MSG_POWER_DOWN_CNF(args):
    return
def MSG_ROAMING_STATUS(args):
    return
def MSG_NETWORK_REG_STATUS(args):
    return
def MSG_CIPHER_IND(args):
    return
def MSG_CELL_INFO_CHANGE_IND(args):
    return
def MSG_PLMNLIST_IND(args):
    return
def MSG_RX_SIGNAL_INFO_CHG_IND(args):
    return
def MSG_RSSI_IND(args):
    return
def MSG_PLMN_SELECT_CNF(args):
    return
def MSG_REG_GSM_IND(args):
    if args[0] == REG_STATE_NORMAL_SERVICE:
        st.registeredGSM(TRUE)
    return
def MSG_REG_GPRS_IND(args):
    if args[0] == REG_STATE_NORMAL_SERVICE:
        st.registeredGPRS(TRUE)
    elif args[0] == REG_STATE_NO_SERVICE:
        st.registeredGPRS(FALSE)
    return
def MSG_DATE_TIMEZONE_IND(args):
    return
def MSG_TIMEZONE_IND(args):
    return
def MSG_NETWORK_NAME_IND(args):
    return
def MSG_INCOMING_CALL_IND(args):
    ci = intUntilEqu(args[0])
    # Change state of CI to calling
    st.callState(ci, CC_CALL_CALLING)
    return
def MSG_VOICECALL_CONNECTED_IND(args):
    ci = intUntilEqu(args[0])
    print "Connected ind ci=", ci
    # Change state of CI to connected
    st.callState(ci, CC_CALL_CONNECTED)
    st.callState(ci, CC_CALL_ACTIVE)
    return
def MSG_VOICECALL_WAITING_IND(args):
    ci = intUntilEqu(args[0])
    # Change state of CI to waiting
    st.callState(ci, CC_CALL_WAITING)
    return
def MSG_VOICECALL_ACTION_RSP(args):
    ci = intUntilEqu(args[0])
    if args[1] == CC_HOLD_CALL_SUCCESS:     # Is active
        st.callState(ci, CC_CALL_HOLD)
    elif args[1] == CC_RESUME_CALL_SUCCESS: # Is on hold
        st.callState(ci, CC_CALL_ACTIVE)
    elif args[1] == CC_SWAP_CALL_SUCCESS:   # Is on hold
        st.callState(ci, CC_CALL_ACTIVE)
    return
def MSG_VOICECALL_PRECONNECT_IND(args):
    return
def MSG_VOICECALL_RELEASE_IND(args):
    ci = intUntilEqu(args[0])
    # Save duration in seconds
    st.lastCallDuration = st.callDuration(ci)
    # Release call
    st.releaseCall(ci)
    return
def MSG_CALL_STATUS_IND(args):
    ci = intUntilEqu(args[0])
    if args[1] == MTVOICE_CALL:
        if args[2] == CC_CALL_HOLD:
            st.callState(ci, CC_CALL_HOLD)
        elif args[2] == CC_CALL_ALERTING:
            st.callState(ci, CC_CALL_ALERTING)
    return
def MSG_CALL_CONNECTEDLINEID_IND(args):
    return
def MSG_DATACALL_STATUS_IND(args):
    return
def MSG_DATACALL_CONNECTED_IND(args):
    return
def MSG_DATACALL_RELEASE_IND(args):
    return
def MSG_DATACALL_ECDC_IND(args):
    return
def MSG_CALL_CCM_IND(args):
    return
def MSG_CALL_AOCSTATUS_IND(args):
    return
def MSG_SMSPP_DELIVER_IND(args):
    return
def MSG_SMSPP_STORED_IND(args):
    return
def MSG_SMS_WRITE_RSP_IND(args):
    return
def MSG_SMSCB_DATA_IND(args):
    return
def MSG_SMSSR_REPORT_IND(args):
    return
def MSG_SMS_SUBMIT_RSP(args):
    return
def MSG_SMS_COMMAND_RSP(args):
    return
def MSG_SMS_CB_START_STOP_RSP(args):
    return
def MSG_SMSCB_READ_RSP(args):
    return
def MSG_VM_WAITING_IND(args):
    return
def MSG_SMS_READY_IND(args):
    return
def MSG_BUILD_PBK_REQ(args):
    return
def MSG_REBUILD_ADN_PBK_REQ(args):
    return
def MSG_FIND_PBK_ALPHA_MUL_REQ(args):
    return
def MSG_FIND_PBK_ALPHA_ONE_REQ(args):
    return
def MSG_SHUT_DOWN_PBK_REQ(args):
    return
def MSG_GET_PBK_INFO_REQ(args):
    return
def MSG_GET_PBK_INFO_RSP(args):
    return
def MSG_READ_PBK_ENTRY_REQ(args):
    return
def MSG_PBK_ENTRY_DATA_RSP(args):
    return
def MSG_WRT_PBK_ENTRY_REQ(args):
    return
def MSG_WRT_PBK_ENTRY_RSP(args):
    return
def MSG_WRT_PBK_ENTRY_IND(args):
    return
def MSG_CHK_PBK_DIALLED_NUM_REQ(args):
    return
def MSG_CHK_PBK_DIALLED_NUM_RSP(args):
    return
def MSG_PBK_READY_IND(args):
    st.setPBKReady( TRUE )
    return
def MSG_PPP_OPEN_CNF(args):
    return
def MSG_PPP_CLOSE_CNF(args):
    return
def MSG_PPP_OPEN_IND(args):
    return
def MSG_PPP_CLOSE_IND(args):
    return
def MSG_DC_REPORT_CALL_STATUS(args):
    return
def MSG_GPRS_ACTIVATE_IND(args):
    return
def MSG_GPRS_DEACTIVATE_IND(args):
    return
def MSG_SNPDU_IND(args):
    return
def MSG_SATK_EVENT_DISPLAY_TEXT(args):
    return
def MSG_SATK_EVENT_GET_INKEY(args):
    return
def MSG_SATK_EVENT_GET_INPUT(args):
    return
def MSG_SATK_EVENT_PLAY_TONE(args):
    return
def MSG_SATK_EVENT_SELECT_ITEM(args):
    return
def MSG_SATK_EVENT_SEND_SS(args):
    return
def MSG_SATK_EVENT_SEND_USSD(args):
    return
def MSG_SATK_EVENT_SETUP_CALL(args):
    return
def MSG_SATK_EVENT_SETUP_MENU(args):
    return
def MSG_SATK_EVENT_MENU_SELECTION(args):
    return
def MSG_SATK_EVENT_REFRESH(args):
    return
def MSG_SATK_EVENT_SEND_SHORT_MSG(args):
    return
def MSG_SATK_EVENT_STK_SESSION_END(args):
    return
def MSG_STK_SEND_EMERGENCY_CALL_REQ(args):
    return
def MSG_STK_REPORT_CALL_RECEIVED(args):
    return
def MSG_STK_REPORT_CALL_STATUS(args):
    return
def MSG_STK_REPORT_CALL_CONNECTED_ID(args):
    return
def MSG_STK_REPORT_CALL_ACTION_RESULT(args):
    return
def MSG_STK_REPORT_CALL_RELEASE(args):
    return
def MSG_STK_REPORT_SUPP_SVC_STATUS(args):
    return
def MSG_STK_REPORT_CALL_AOC_STATUS(args):
    return
def MSG_STK_REPORT_CALL_CCM(args):
    return
def MSG_SS_CALL_NOTIFICATION(args):
    return
def MSG_SS_CALL_FORWARD_RSP(args):
    return
def MSG_SS_CALL_FORWARD_STATUS_RSP(args):
    return
def MSG_SS_CALL_BARRING_RSP(args):
    return
def MSG_SS_CALL_BARRING_STATUS_RSP(args):
    return
def MSG_SS_CALL_BARRING_PWD_CHANGE_RSP(args):
    return
def MSG_SS_CALLING_LINE_ID_STATUS_RSP(args):
    return
def MSG_SS_CALL_WAITING_RSP(args):
    return
def MSG_SS_CALL_WAITING_STATUS_RSP(args):
    return
def MSG_SS_CONNECTED_LINE_STATUS_RSP(args):
    return
def MSG_SS_CALLING_LINE_RSTRICTION_STATUS_RSP(args):
    return
def MSG_SS_CONNECTED_LINE_RESTRICTION_STATUS_RSP(args):
    return
def MSG_SS_CALLRELEASE_IND(args):
    return
def MSG_SS_CALLINDEX_IND(args):
    return
def MSG_USSD_DATA_IND(args):
    return
def MSG_USSD_DATA_RSP(args):
    return
def MSG_USSD_SESSION_END_IND(args):
    return
def MSG_USSD_CALLINDEX_IND(args):
    return
def MSG_USSD_CALLRELEASE_IND(args):
    return
def MSG_SIM_EFILE_INFO_RSP(args):
    return
def MSG_SIM_EFILE_DATA_RSP(args):
    return
def MSG_SIM_EFILE_UPDATE_RSP(args):
    return
def MSG_SIM_PIN_ATTEMPT_RSP(args):
    return
def MSG_SIM_SET_FDN_RSP(args):
    return
def MSG_SIM_ENABLE_CHV_RSP(args):
    return
def MSG_SIM_CHANGE_CHV_RSP(args):
    return
def MSG_SIM_VERIFY_CHV_RSP(args):
    return
def MSG_SIM_UNBLOCK_CHV_RSP(args):
    return
def MSG_SIM_PBK_INFO_RSP(args):
    return
def MSG_SIM_PBK_DATA_RSP(args):
    return
def MSG_SIM_PBK_WRITE_RSP(args):
    return
def MSG_SIM_PLMN_WRITE_RSP(args):
    return
def MSG_SIM_MAX_ACM_RSP(args):
    return
def MSG_SIM_ACM_VALUE_RSP(args):
    return
def MSG_SIM_ACM_UPDATE_RSP(args):
    return
def MSG_SIM_ACM_MAX_UPDATE_RSP(args):
    return
def MSG_SIM_ACM_INCREASE_RSP(args):
    return
def MSG_SIM_SVC_PROV_NAME_RSP(args):
    return
def MSG_SIM_PUCT_DATA_RSP(args):
    return
def MSG_SIM_PUCT_UPDATE_RSP(args):
    return
def MSG_SIM_SMS_SEARCH_STATUS_RSP(args):
    return
def MSG_SIM_SMS_DATA_RSP(args):
    return
def MSG_SIM_SMS_WRITE_RSP(args):
    return
def MSG_SIM_SMS_STATUS_UPD_RSP(args):
    return
def MSG_SIM_SMS_SCA_UPD_RSP(args):
    return
def MSG_SIM_SMS_PARAM_DATA_RSP(args):
    return
def MSG_SIM_SMS_TP_MR_RSP(args):
    return
def MSG_SIM_RESTRICTED_ACCESS_RSP(args):
    return
def MSG_SIM_DETECTION_IND(args):
    return
def MSG_POWER_DOWN_REQ(args):
    return
def MSG_POWER_UP_REQ(args):
    return
def MSG_RESET_REQ(args):
    return
def MSG_MS_WAKEUP_REQ(args):
    return
def MSG_AT_COPS_CMD(args):
    return
def MSG_AT_CGATT_CMD(args):
    return
def MSG_AT_CGACT_CMD(args):
    return
def MSG_AT_CALL_TIMER(args):
    return
def MSG_AT_CALL_ABORT(args):
    return
def MSG_AT_ESC_DATA_CALL(args):
    return
def MSG_MS_READY_IND(args):
    return
def MSG_SMS_COMPOSE_REQ(args):
    return
def MSG_SMS_USR_DATA_IND(args):
    return
def MSG_SMS_PARM_CHECK_RSP(args):
    return
def MSG_SMS_REPORT_IND(args):
    return
def MSG_SMS_MEM_AVAIL_RSP(args):
    return
def MSG_SMS_CNMA_TIMER_IND(args):
    return
def MSG_ATC_TIMEOUT_IND(args):
    return
def MSG_ATTACH_IND(args):
    return
def MSG_DETACH_IND(args):
    return
def MSG_ACTIVATE_IND(args):
    return
def MSG_DEACTIVATE_IND(args):
    return
def MSG_ATTACH_CNF(args):
    return
def MSG_DETACH_CNF(args):
    return
def MSG_ACTIVATE_CNF(args):
    return
def MSG_DEACTIVATE_CNF(args):
    return
def MSG_SN_XID_CNF(args):
    return
def MSG_MODIFY_IND(args):
    return
def MSG_SERVICE_IND(args):
    return
def MSG_CHECK_QOSMIN_IND(args):
    return
def MSG_CELL_ID_IND(args):
    return
def MSG_DATA_STATE_TIMER(args):
    return
def MSG_SATK_EVENT_MENU_SELECTION_REJ(args):
    return
def MSG_SATK_EVENT_SEND_SS_RESULT(args):
    return
def MSG_SATK_EVENT_SEND_USSD_RESULT(args):
    return
def MSG_SATK_EVENT_INVALID(args):
    return
def MSG_STK_MENU_SELECTION_REJ(args):
    return
def MSG_STK_DISPLAY_TEXT_REQ(args):
    return
def MSG_STK_SETUP_IDLEMODE_TEXT_REQ(args):
    return
def MSG_STK_GET_INPUT_REQ(args):
    return
def MSG_STK_GET_INKEY_REQ(args):
    return
def MSG_STK_PLAY_TONE_REQ(args):
    return
def MSG_STK_SELECT_ITEM_REQ(args):
    return
def MSG_STK_SETUP_MENU_REQ(args):
    return
def MSG_STK_SIMTOOLKIT_REFRESH_REQ(args):
    return
def MSG_STK_SIAT_SIMTOOLKIT_REFRESH_REQ(args):
    return
def MSG_STK_STK_END_IND(args):
    return
def MSG_STK_SEND_SS_REQ(args):
    return
def MSG_STK_SETUP_CALL_REQ(args):
    return
def MSG_STK_SETUP_CALL_ACC(args):
    return
def MSG_STK_SETUP_CALL_REJ(args):
    return
def MSG_STK_MOSMS_ALPHA_IND(args):
    return
def MSG_STK_MOSMS_RESULT_IND(args):
    return
def MSG_STK_LOCAL_DATE_REQ(args):
    return
def MSG_STK_LOCAL_LANG_REQ(args):
    return
def MSG_STK_REPORT_NEW_MESSAGE(args):
    return
def MSG_STK_STOP_PLAYTONE_REQ(args):
    return
def MSG_SIM_STATUS_IND(args):
    return
def MSG_SIM_INIT_SMS_STATUS_IND(args):
    return
def MSG_SIM_GENERAL_SERVICE_IND(args):
    return
def MSG_SIM_ACM_UPDATE_IND(args):
    return
def MSG_SIM_SMS_MEM_AVAIL_IND(args):
    return
def MSG_SIM_CACHED_DATA_READY_IND(args):
    return
def MSG_CALL_ESTABLISH_REQ(args):
    return
def MSG_SHF_STATUS(args):
    return
def MSG_SIMULATOR_RTC_FIREALARM(args):
    return
def MSG_INVALID(args):
    return

# moremsgs:
def MSG_BATTMGR_LO_TEMP(args):
    return
def MSG_BATTMGR_CHARGING(args):
    return
def MSG_BATTMGR_NOT_CHARGING(args):
    return
def MSG_BATTMGR_BATT_FULL(args):
    return
def MSG_BATTMGR_BATT_LOW(args):
    return
def MSG_BATTMGR_BATT_FULL(args):
    return
def MSG_BATTMGR_BATT_EMPTY(args):
    return
def MSG_BATTMGR_LEVEL(args):
    return
def MSG_DATA_LINK_UP_STATUS_CALLBACK(args):
    st.GPRSActivate = PDP_CONTEXT_ACTIVATED
    return
def MSG_DATA_LINK_DOWN_STATUS_CALLBACK(args):
    st.GPRSActivate = PDP_CONTEXT_DEACTIVATED
    return

def MSG_USB_EVENT(args):
    return
def MSG_MODEM_STATUS_IND(args):
    return

# Keypad
def KPD_DRV_Callback(args):
    return

# API for field trials / test parameter report
def MSG_MEASURE_REPORT_PARAM_IND(args):
    return

# Event dispatcher
# 
def handleEvent(state, event):
    global st
    st = state

    # Should start with '*[0-9]' to be processed...
    if event[0] != '*' or event[1] < '0' or event[1] > '9':
        return
    equ = string.find(event, "=")
    if equ == -1:
        return
    open  = string.find(event, "(")
    if open == -1:
        return
    close = string.find(event, ")")
    if close == -1:
        return
    func = event[equ+1:open]
    para = string.split(event[open+1:close], ',')
    #try:
    eval(func)(para)
    #except NameError, msg:
        # Unknown Event
    #except:
    #    pass
