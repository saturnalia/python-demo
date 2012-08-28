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


from ss_api import *
from sim_brcm import *
from sim_def   import *
from sim_api import *
from phonebk import *

def SS_CallBarType_t(callBarType):
    callBarTypes = [
        SS_CALLBAR_TYPE_NOTSPECIFIED,
        SS_CALLBAR_TYPE_OUT_ALL,
        SS_CALLBAR_TYPE_OUT_INTL,
        SS_CALLBAR_TYPE_OUT_INTL_EXCL_HPLMN,
        SS_CALLBAR_TYPE_INC_ALL,        
        SS_CALLBAR_TYPE_INC_ROAM_OUTSIDE_HPLMN,
        SS_CALLBAR_TYPE_ALL,    
        SS_CALLBAR_TYPE_OUTG,
        SS_CALLBAR_TYPE_INC 
    ]
    return callBarTypes[int(callBarType)]

def SS_SvcCls_t(svcCls):
    svcClss = [
        SS_SVCCLS_NOTSPECIFIED,
        SS_SVCCLS_SPEECH,
        SS_SVCCLS_ALT_SPEECH,
        SS_SVCCLS_DATA,
        SS_SVCCLS_FAX,
        SS_SVCCLS_ALL_TELESERVICE_EXCEPT_SMS,
        SS_SVCCLS_SMS,
        SS_SVCCLS_DATA_CIRCUIT_SYNC,
        SS_SVCCLS_DATA_CIRCUIT_ASYNC,
        SS_SVCCLS_DEDICATED_PACKET,
        SS_SVCCLS_ALL_SYNC_SERVICES,
        SS_SVCCLS_DEDICATED_PAD,
        SS_SVCCLS_ALL_ASYNC_SERVICES,
        SS_SVCCLS_ALL_BEARER_SERVICES
    ]
    return svcClss[int(svcCls)]

def SS_CallFwdReason_t(reason):
    reasons = [
        SS_CALLFWD_REASON_NOTSPECIFIED,
        SS_CALLFWD_REASON_UNCONDITIONAL,
        SS_CALLFWD_REASON_BUSY,
        SS_CALLFWD_REASON_NO_REPLY,
        SS_CALLFWD_REASON_NOT_REACHABLE,
        SS_CALLFWD_REASON_ALL_CF,
        SS_CALLFWD_REASON_ALL_CONDITIONAL
    ]
    return reasons[int(reason)]

def SS_Mode_t(mode):
    modes = [
        SS_MODE_NOTSPECIFIED,
        SS_MODE_DISABLE,
        SS_MODE_ENABLE,
        SS_MODE_INTERROGATE,
        SS_MODE_REGISTER,
        SS_MODE_ERASE
    ]
    return modes[int(mode)]

def SIMPBK_ID_t(id):
    ids = [
        SIMPBK_ADN,	 
        SIMPBK_FDN,	 
        SIMPBK_SDN,	 
        SIMPBK_LND,	 
        SIMPBK_MSISDN,
        SIMPBK_BDN
    ] 
    return ids[int(id)]

def PBK_ID_t(id):
    pbkids = [
	PB_ME,
	PB_FDN,
	PB_ADN,
	PB_EN,
	PB_SDN,
	PB_LND,
	PB_MSISDN,
	PB_INVALID_TYPE
    ] 
    return pbkids[int(id)]

def SS_Mode_t(mode):
    modes = [
        SS_MODE_NOTSPECIFIED,
        SS_MODE_DISABLE,
        SS_MODE_ENABLE,
        SS_MODE_INTERROGATE,
        SS_MODE_REGISTER,
        SS_MODE_ERASE
    ]
    return modes[int(mode)]

