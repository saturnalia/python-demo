# This file implements the SIM and ME storage.

import string
import sys

import sim_brcm
import smsutil
import resultcode

from sim_def   import *
from sim_api   import *
from sim_common   import *
from common_sms   import *
from sim_brcm import *
from smsutil import *
from resultcode import *

class SmsStorage:
    def __init__(self):
        self.me_sms = [ [ '',       SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ] ]

        self.sm_sms = [ [ '',       SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ],
                   [ '',            SIMSMSMESGSTATUS_FREE, '',    '' ] ]

    def isFree( self, storageType, rec_no ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage =  self.sm_sms
        else:
            return RESULT_ERROR
        if rec_no < len(storage):
            return storage[rec_no][1] == SIMSMSMESGSTATUS_FREE
        else:
            return RESULT_ERROR

    def getRecord( self, storageType, rec_no, mode ):
        if storageType == int(ME_STORAGE[0]):
           storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
           storage =  self.sm_sms
        else:
           return RESULT_ERROR
        if rec_no < len(storage):
           if mode != 0:
               storage[1] = SIMSMSMESGSTATUS_READ
           return storage[rec_no]
        else:
           return RESULT_ERROR

    def putRecord( self, storageType, rec_no, mti, status, sca, msg  ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return RESULT_ERROR
        if rec_no < len(storage):
            storage[rec_no][0] = mti
            storage[rec_no][1] = status
            storage[rec_no][2] = sca
            storage[rec_no][3] = msg
        else:
            return RESULT_ERROR
        return RESULT_OK

    def deleteRecord( self, storageType, rec_no ):
        if storageType == int(ME_STORAGE[0]):
           storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
           storage = self.sm_sms
        else:
           return RESULT_ERROR
        storage[rec_no] =  [ '', SIMSMSMESGSTATUS_FREE, '', '' ]
        return RESULT_OK

    def findFree( self, storageType ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return -1
        rec_no = -1
        for i in range(len(storage)):
            if storage[i][1] == SIMSMSMESGSTATUS_FREE:
                rec_no = i
                break
        return rec_no

    def getSize( self, storageType ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return RESULT_ERROR
        return len(storage)

    def getFree( self, storageType ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return RESULT_ERROR
        free = 0
        for rec_no in range(len(storage)):
           if storage[rec_no][1] == SIMSMSMESGSTATUS_FREE:
               free += 1
        return free

    def getUsed( self, storageType ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return RESULT_ERROR
        used = 0
        for rec_no in range(len(storage)):
           if storage[rec_no][1] != SIMSMSMESGSTATUS_FREE:
               used += 1
        return used

    def getStatus( self, storageType, rec_no ):
        if storageType == int(ME_STORAGE[0]):
            storage = self.me_sms
        elif storageType == int(SM_STORAGE[0]):
            storage = self.sm_sms
        else:
            return RESULT_ERROR
        return storage[rec_no][1]   