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


import os
import sys
import threading
import Tkinter as tk
from segment import *
from GSM_State import *
from queue import *
from kpd_drv import *
from broadcomapi import *

from ms_pwron_enum  import *
from mstypes  import *
from mstypes_enum  import *
from smsutil  import *
from sim_brcm import *
from callctrl import *
from sms_storage import *
from common import *

# If no save preferences, set default
prefALSEnabled      = 1
prefSIMinserted     = 1
prefChargerInserted = 0
prefHasKeypad       = 0
prefHaveSVC         = 0
prefLargefont       = 1
prefLogKeypad       = 0
prefNetworkNameInd  = 1
prefPinEnabled      = 0
prefRegisterGPRS    = REG_STATE_NORMAL_SERVICE
prefRegisterGSM     = REG_STATE_NORMAL_SERVICE
prefReplayKeypad    = 0
prefSatkEnabled     = 0
prefSendBATTLEV     = 1
prefBattlevel       = 4
prefSendRSSI        = 1
prefSignallevel     = 47
prefShfStatus       = 0
prefReplayFile      = ""
try:
    from preferences import *
except:
    print "Using default GUI preferences...\n"

from taskmsgs import *

class GUI(threading.Thread):
    def __init__(self, state, queue, sms, Revision):
        global st,q,smsdb
        st = state
        q = queue
        smsdb = sms
        
        self.fp = 0
        self.root = tk.Tk()
        self.root.title('Broadcom GSM/GPRS/WEDGE API Simulator')
        ########################################################################
        # [Call Control] [SIM] [Network] [Battery]
        ########################################################################
        self.mb = tk.Menu(self.root)
        # Preferences
        self.cc_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="Preferences", menu=self.cc_mb)
        self.cc_mb.add_command(label="Save", command=self.pref_save)
        self.cc_mb.add_command(label="Default", command=self.pref_default)
        self.varLargeFont = tk.IntVar()
        self.varLargeFont.set(prefLargefont)# Set to user preferences
        self.cc_mb.add_checkbutton(label="Large font", variable=self.varLargeFont, command=self.cmdLargeFont)
        
        # Call Control
        self.cc_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="CC", menu=self.cc_mb)
        self.varMoAction = tk.IntVar()
        self.cc_mb.add_radiobutton(label="Accept MO", variable=self.varMoAction, value=0)
        self.cc_mb.add_radiobutton(label="Reject MO", variable=self.varMoAction, value=1)
        self.cc_mb.add_radiobutton(label="Busy MO",   variable=self.varMoAction, value=2)

        # SIM
        self.sim_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="SIM", menu=self.sim_mb)
        self.varSIMinserted = tk.IntVar()
        self.varSIMinserted.set(prefSIMinserted)
        self.sim_mb.add_checkbutton(label="Inserted", variable=self.varSIMinserted, command=self.sim_inserted)
        self.sim_mb.add_command(label="Unblock", command=self.sim_unblock)
        self.sim_mb.add_command(label="Block", command=self.sim_block)
        self.varPinEnabled = tk.IntVar()
        self.varPinEnabled.set(prefPinEnabled) # Set to user preferences
        self.sim_mb.add_checkbutton(label="PIN1 Enabled", variable=self.varPinEnabled, command=self.cmdPinEnabled)

        self.varSatkEnabled = tk.IntVar()
        self.varSatkEnabled.set(prefSatkEnabled) # Set to user preferences
#        self.sim_mb.add_checkbutton(label="SATK Enabled", variable=self.varSatkEnabled, command=self.cmdSatkEnabled)

        self.varALSEnabled = tk.IntVar()
        self.varALSEnabled.set(prefALSEnabled) # Set to user preferences
        self.sim_mb.add_checkbutton(label="ALS Enabled", variable=self.varALSEnabled, command=self.cmdALSEnabled)

        self.varHaveSVC = tk.IntVar()
        self.varHaveSVC.set(prefHaveSVC) # Set to user preferences
        self.sim_mb.add_checkbutton(label="Service provider", variable=self.varHaveSVC, command=self.cmdHaveSVC)
        self.varHomeOperator = tk.IntVar()
        self.sim_mb.add_radiobutton(label="AT&T",    variable=self.varHomeOperator, value=0, command=self.cmdHomeOperator)
        self.sim_mb.add_radiobutton(label="Telenor", variable=self.varHomeOperator, value=1, command=self.cmdHomeOperator)
        self.sim_mb.add_radiobutton(label="Netcom",  variable=self.varHomeOperator, value=2, command=self.cmdHomeOperator)

        # Network
        self.nw_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="Network", menu=self.nw_mb)
        self.nw_mb.add_command(label="Temporary failure", command=self.temporaryFailure)

        self.nw_mb.add('separator')
        self.varSendRSSI = tk.IntVar()
        self.varSendRSSI.set(prefSendRSSI)  # Set to user preferences
        self.nw_mb.add_checkbutton(label="Send RSSI_IND", variable=self.varSendRSSI,  command=self.cmdSendRSSI)
        self.varSignallevel = tk.IntVar()
        self.varSignallevel.set(prefSignallevel) # Set to user preferences
        self.nw_mb.add_radiobutton(label=" -- Level 63", variable=self.varSignallevel, command=self.cmdSignallevel, value=63)
        self.nw_mb.add_radiobutton(label=" -- Level 47", variable=self.varSignallevel, command=self.cmdSignallevel, value=47)
        self.nw_mb.add_radiobutton(label=" -- Level 31", variable=self.varSignallevel, command=self.cmdSignallevel, value=31)
        self.nw_mb.add_radiobutton(label=" -- Level 15", variable=self.varSignallevel, command=self.cmdSignallevel, value=15)
        self.nw_mb.add_radiobutton(label=" -- Level 0", variable=self.varSignallevel, command=self.cmdSignallevel, value=0)

        self.nw_mb.add('separator')
        self.varRegisterGSM = tk.StringVar()
        self.varRegisterGSM.set(prefRegisterGSM)# Set to user preferences
        self.nw_mb.add_radiobutton(label="GSM: Off", variable=self.varRegisterGSM, value=REG_STATE_NO_SERVICE, command=self.cmdvarRegisterGSM)
        self.nw_mb.add_radiobutton(label="GSM: Normal", variable=self.varRegisterGSM, value=REG_STATE_NORMAL_SERVICE, command=self.cmdvarRegisterGSM)
        self.nw_mb.add_radiobutton(label="GSM: Searching", variable=self.varRegisterGSM, value=REG_STATE_SEARCHING, command=self.cmdvarRegisterGSM)
        self.nw_mb.add_radiobutton(label="GSM: Limited", variable=self.varRegisterGSM, value=REG_STATE_LIMITED_SERVICE, command=self.cmdvarRegisterGSM)
        self.nw_mb.add_radiobutton(label="GSM: Unknown", variable=self.varRegisterGSM, value=REG_STATE_UNKNOWN, command=self.cmdvarRegisterGSM)
        self.nw_mb.add_radiobutton(label="GSM: Roaming", variable=self.varRegisterGSM, value=REG_STATE_ROAMING_SERVICE, command=self.cmdvarRegisterGSM)

        self.nw_mb.add('separator')
        self.varRegisterGPRS = tk.StringVar()
        self.varRegisterGPRS.set(prefRegisterGPRS)# Set to user preferences
        self.nw_mb.add_radiobutton(label="GPRS: Off", variable=self.varRegisterGPRS, value=REG_STATE_NO_SERVICE, command=self.cmdvarRegisterGPRS)
        self.nw_mb.add_radiobutton(label="GPRS: Normal", variable=self.varRegisterGPRS, value=REG_STATE_NORMAL_SERVICE, command=self.cmdvarRegisterGPRS)
        self.nw_mb.add_radiobutton(label="GPRS: Searching", variable=self.varRegisterGPRS, value=REG_STATE_SEARCHING, command=self.cmdvarRegisterGPRS)
        self.nw_mb.add_radiobutton(label="GPRS: Limited", variable=self.varRegisterGPRS, value=REG_STATE_LIMITED_SERVICE, command=self.cmdvarRegisterGPRS)
        self.nw_mb.add_radiobutton(label="GPRS: Unknown", variable=self.varRegisterGPRS, value=REG_STATE_UNKNOWN, command=self.cmdvarRegisterGPRS)
        self.nw_mb.add_radiobutton(label="GPRS: Roaming", variable=self.varRegisterGPRS, value=REG_STATE_ROAMING_SERVICE, command=self.cmdvarRegisterGPRS)

        self.nw_mb.add('separator')
        self.varOperator = tk.IntVar()
        self.nw_mb.add_radiobutton(label="AT&T",    variable=self.varOperator, value=0, command=self.cmdOperator)
        self.nw_mb.add_radiobutton(label="Telenor", variable=self.varOperator, value=1, command=self.cmdOperator)
        self.nw_mb.add_radiobutton(label="Netcom",  variable=self.varOperator, value=2, command=self.cmdOperator)

        self.nw_mb.add('separator')
        self.varNetworkNameInd = tk.IntVar()
        self.varNetworkNameInd.set(prefNetworkNameInd)# Set to user preferences
        self.nw_mb.add_checkbutton(label="Send Network name", variable=self.varNetworkNameInd, command=self.cmdNetworkNameInd)


        # Battery & charger
#        self.batt_mb = tk.Menu(self.mb)
#        self.mb.add_cascade(label="Battery", menu=self.batt_mb)
#        self.varSendBATTLEV = tk.IntVar()
#        self.varSendBATTLEV.set(prefSendBATTLEV)   # Set to user preferences
#        self.batt_mb.add_checkbutton(label="Send BATTMGR_LEVEL", variable=self.varSendBATTLEV, command=self.cmdSendBATTLEV)
#
#        self.varBattlevel = tk.IntVar()
#        self.varBattlevel.set(prefBattlevel) # Set to user preferences
#        self.batt_mb.add_radiobutton(label=" -- Level 4", variable=self.varBattlevel, command=self.cmdBattlevel, value=4)
#        self.batt_mb.add_radiobutton(label=" -- Level 3", variable=self.varBattlevel, command=self.cmdBattlevel, value=3)
#        self.batt_mb.add_radiobutton(label=" -- Level 2", variable=self.varBattlevel, command=self.cmdBattlevel, value=2)
#        self.batt_mb.add_radiobutton(label=" -- Level 1", variable=self.varBattlevel, command=self.cmdBattlevel, value=1)
#        self.batt_mb.add_radiobutton(label=" -- Level 0", variable=self.varBattlevel, command=self.cmdBattlevel, value=0)
#
#        self.varBattlevelLowInd = tk.IntVar()
#        self.batt_mb.add_checkbutton(label="Send BATTMGR_BATT_LOW", variable=self.varBattlevelLowInd, command=self.cmdBattlevelLowInd)
#        self.varBattlevelFullInd = tk.IntVar()
#        self.batt_mb.add_checkbutton(label="Send BATTMGR_BATT_FULL", variable=self.varBattlevelFullInd, command=self.cmdBattlevelFullInd)
#        self.varChargerInserted = tk.IntVar()
#        self.varChargerInserted.set(prefChargerInserted) # Set to user preferences
#        self.batt_mb.add_checkbutton(label="Charger inserted", variable=self.varChargerInserted, command=self.cmdChargerInserted)
#        self.varShfStatus = tk.IntVar()
#        self.varShfStatus.set(prefShfStatus) # Set to user preferences
#        self.batt_mb.add_checkbutton(label="SHF inserted", variable=self.varShfStatus, command=self.cmdShfStatus)

        # SIM Customer Service Profile

        self.csp_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="Customer-Service Profile", menu=self.csp_mb)
        self.csp_cfu = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CFU", variable=self.csp_cfu)
        self.csp_cfb = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CFB", variable=self.csp_cfb)
        self.csp_cfnry = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CFNRY", variable=self.csp_cfnry)
        self.csp_cfnrc = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CFNRC", variable=self.csp_cfnrc)
        self.csp_ct = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CT", variable=self.csp_ct)
        self.csp_boac = tk.IntVar()
        self.csp_mb.add_checkbutton(label="BOAC", variable=self.csp_boac)
        self.csp_boic = tk.IntVar()
        self.csp_mb.add_checkbutton(label="BOIC", variable=self.csp_boic)
        self.csp_boic_exhc = tk.IntVar()
        self.csp_mb.add_checkbutton(label="BOIC EXHC", variable=self.csp_boic_exhc)
        self.csp_baic = tk.IntVar()
        self.csp_mb.add_checkbutton(label="BAIC", variable=self.csp_baic)
        self.csp_bic_roam = tk.IntVar()
        self.csp_mb.add_checkbutton(label="BIC ROAM", variable=self.csp_bic_roam)
        self.csp_mpty = tk.IntVar()
        self.csp_mb.add_checkbutton(label="MPTY", variable=self.csp_mpty)
        self.csp_cug = tk.IntVar()
        self.csp_mb.add_checkbutton(label="CUG", variable=self.csp_cug)

        # SS
        self.ss_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="SS", menu=self.ss_mb)
        self.varSsFail = tk.IntVar()
        self.ss_mb.add_checkbutton(label="SS_Fail", variable=self.varSsFail, command=self.cmdSsFail)
        self.varCLIP = tk.IntVar()
        self.ss_mb.add_checkbutton(label="CLIP", variable=self.varCLIP, command=self.cmdCLIP)
        self.varCLIR = tk.IntVar()
        self.ss_mb.add_checkbutton(label="CLIR", variable=self.varCLIR, command=self.cmdCLIR)
        self.varCOLP = tk.IntVar()
        self.ss_mb.add_checkbutton(label="COLP", variable=self.varCOLP, command=self.cmdCOLP)
        self.varCOLR = tk.IntVar()
        self.ss_mb.add_checkbutton(label="COLR", variable=self.varCOLR, command=self.cmdCOLR)


        # Power
        self.power_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="Power-Up", menu=self.power_mb)
        self.varPowerOnCause = tk.StringVar()
        self.varPowerOnCause.set(POWER_ON_CAUSE_NORMAL) 
        self.varPowerOnCause.set(1) # Set to user preferences
        self.power_mb.add_radiobutton(label=" Normal",        variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_NORMAL)
        self.power_mb.add_radiobutton(label=" Alarm",         variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_ALARM)
        self.power_mb.add_radiobutton(label=" Charging off",  variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_CHARGING_OFF)
        self.power_mb.add_radiobutton(label=" Charging on",   variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_CHARGING_ON)
        self.power_mb.add_radiobutton(label=" Assertion",     variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_ERR_RESET)
        self.power_mb.add_radiobutton(label=" STK Reset",     variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_STK_RESET)
        self.power_mb.add_radiobutton(label=" Watchdog",      variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_WATCHDOG_RESET)
        self.power_mb.add_radiobutton(label=" USB Download",  variable=self.varPowerOnCause, command=self.cmdPowerOnCause, value=POWER_ON_CAUSE_USB_DL)
# SS
#         self.ss_mb = tk.Menu(self.mb)
#         self.mb.add_cascade(label="SS", menu=self.ss_mb)
#         self.varSsFail= tk.IntVar()
#         self.ss_mb.add_checkbutton(label="SS Fail", variable=self.varSsFail, command=self.cmdSsFail)
#        # DS
#        self.ds_mb = tk.Menu(self.mb)
#        self.mb.add_cascade(label="DS", menu=self.ds_mb)
#        self.ds_mb.add_checkbutton(label="What?")

        # SMSMMS

        self.smsmms_mb = tk.Menu(self.mb)
        self.mb.add_cascade(label="SMS/MMS", menu=self.smsmms_mb)
        self.smsmms_mb.add_command(label="Canned SMS Pdu", command=self.generate_sms_pdu)

        self.varloopbackSMS = tk.IntVar()
        self.smsmms_mb.add_checkbutton(label="SMS loopback", variable=self.varloopbackSMS, command=self.loopbackSMS)
        self.varloopbackSMS.set(TRUE)

        self.varloopbackMMS = tk.IntVar()
        self.smsmms_mb.add_command(label="Canned MMS Pdu", command=self.generate_mms_pdu)
        self.smsmms_mb.add_checkbutton(label="MMS loopback", variable=self.varloopbackMMS, command=self.loopbackMMS)
        self.varloopbackMMS.set(TRUE)

        change_theme(self.root)
        
        self.root.config(menu=self.mb)
        ########################################################################
        # Number XXXXXXXXXXXXXXXXX [CALL] [HANGUP]
        ########################################################################
        self.frame1 = tk.Frame(self.root)
        self.number = tk.Label(self.frame1, justify=tk.LEFT, text='Number')
        self.number.grid(row=0, column=0)
        self.call_number = tk.Entry(self.frame1)
        self.call_number.bind('<Return>', self.cc_call_enter)
        self.call_number.grid(row=0, column=1)
        self.call_button = tk.Button(self.frame1, text="Call", command=self.cc_call)
        self.call_button.grid(row=0, column=2)
        self.call_hangup = tk.Button(self.frame1, text="Hangup", command=self.cc_hangup)
        self.call_hangup.grid(row=0, column=3)
        self.frame1.pack()

        self.frame_sim = tk.Frame(self.root)
        self.simpin = []
        self.simpuk = []
        self.simpintry = []
        self.simpuktry = []
        # Make heading 
        # No    Pin  Tries        PUK Tries
        tk.Label(self.frame_sim, text="No", bg="white").grid(row=0, column=0, sticky=tk.W,  padx=4)
        tk.Label(self.frame_sim, text='PIN:',  width=6, bg="white").grid(row=0, column=1, padx=4)
        tk.Label(self.frame_sim, text='Remain:', bg="white").grid(row=0, column=2, padx=4)
        tk.Label(self.frame_sim, text='PUK',   width=12, bg="white").grid(row=0, column=3, padx=4)
        tk.Label(self.frame_sim, text='Remain:', bg="white").grid(row=0, column=4, padx=4)
        for no in range(2):
            self.simpin.append(tk.StringVar())
            self.simpin[no].set(st.PIN_code(no+1))
            self.simpintry.append(tk.IntVar())
            self.simpintry[no].set(st.PIN_attempts(no+1))
            self.simpuk.append(tk.StringVar())
            self.simpuk[no].set(st.PUK_code(no+1))
            self.simpuktry.append(tk.IntVar())
            self.simpuktry[no].set(st.PUK_attempts(no+1))
            tk.Label(self.frame_sim, text="%d" % (no+1), justify=tk.LEFT).grid(row=no+1, column=0)
            tk.Label(self.frame_sim, textvariable=self.simpin[no]).grid(row=no+1, column=1)
            tk.Label(self.frame_sim, textvariable=self.simpintry[no]).grid(row=no+1, column=2)
            tk.Label(self.frame_sim, textvariable=self.simpuk[no]).grid(row=no+1, column=3)
            tk.Label(self.frame_sim, textvariable=self.simpuktry[no]).grid(row=no+1, column=4)
        self.frame_sim.pack()


        # Call Control Frame
        self.ccct = []  # Call Type
        self.cccs = []  # Call State
        self.ccid = []  # Call ID
        self.frame_cc = tk.Frame(self.root)
        # Make heading 
        # CI    Call-Type:          Call-State      Remote ID
        tk.Label(self.frame_cc, text="CI", bg="white").grid(row=0, column=0, sticky=tk.W,  padx=4)
        tk.Label(self.frame_cc, text='Call-Type:',  width=20, bg="white").grid(row=0, column=1, padx=4)
        tk.Label(self.frame_cc, text='Call-State:', width=25, bg="white").grid(row=0, column=2, padx=4)
        tk.Label(self.frame_cc, text='Remote ID',   width=30, bg="white").grid(row=0, column=3, padx=4)
        tk.Label(self.frame_cc, text='HUP',   width=3, bg="white").grid(row=0, column=4, padx=4)
        # and statusgrid
        self.hup_func = [self.hup_func0, self.hup_func1, self.hup_func2, self.hup_func3,
                         self.hup_func4, self.hup_func5, self.hup_func6, self.hup_func7,
                         self.hup_func8, self.hup_func9]
        for ix in range(len(st.cc)):
            self.ccct.append(tk.StringVar())
            self.cccs.append(tk.StringVar())
            self.ccid.append(tk.StringVar())
            tk.Label(self.frame_cc,  text="%d" % ix, justify=tk.LEFT).grid(row=ix+1, column=0)
            tk.Label(self.frame_cc,  textvariable=self.ccct[ix]).grid(row=ix+1, column=1)
            tk.Label(self.frame_cc,  textvariable=self.cccs[ix]).grid(row=ix+1, column=2)
            tk.Label(self.frame_cc,  textvariable=self.ccid[ix]).grid(row=ix+1, column=3)
            tk.Button(self.frame_cc, text="%d" % ix, command=self.hup_func[ix]).grid(row=ix+1, column=4)
        self.frame_cc.pack()
    
        self.area = tk.Frame(self.root)

#        if self.varHasKeypad.get() == TRUE:
#            #
#            # Phone keypad
#            self.phone = tk.Frame(self.area)
#            self.keypadButton(" SKL ",  0, 0,  self.button_f1)
#            self.keypadButton(" Up ",  0, 1,  self.button_up)
#            self.keypadButton(" SKR ",  0, 2,  self.button_f2)
#            #
#            self.keypadButton("Left",  1, 0,  self.button_left)
#            self.keypadButton("Sel ",  1, 1,  self.button_sel)
#            self.keypadButton("Right", 1, 2,  self.button_right)
#            #
#            self.keypadButton("Back",  2, 0,  self.button_menu)
#            self.keypadButton("Down ", 2, 1,  self.button_down)
#            self.keypadButton("????", 2, 2,  self.button_pbook)
#            #
#            self.keypadButton("Send",  3, 0,  self.button_call)
#            self.keypadButton("CLR ",  3, 1,  self.button_clr)
#            self.keypadButton("End",3, 2,  self.button_hangup)
#            #
#            self.butt_func = [self.button_1, self.button_2, self.button_3,
#            self.button_4, self.button_5, self.button_6, self.button_7,
#            self.button_8, self.button_9]
#            butt = 0
#            for ro in range(3):
#                for co in range(3):
#                    self.keypadButton(" %d " % (butt + 1),  ro+4, co , self.butt_func[butt])
#                    butt += 1
#            #
#            self.keypadButton(" * ", 7, 0,  self.button_star)
#            self.keypadButton(" 0 ", 7, 1,  self.button_0)
#            self.keypadButton(" # ", 7, 2,  self.button_hash)
#
#            self.keypadButton("HsSw", 5, 3,  self.button_hsSw)
#            self.keypadButton("VolU", 6, 3,  self.button_volUp)
#            self.keypadButton("VolD", 7, 3,  self.button_volDown)
#            self.phone.grid(row=0, column=0)




        self.sms = tk.LabelFrame(self.area,text="SMS")

        tk.Label(self.sms, justify=tk.LEFT, text='smsc').grid(row=0,column=0, sticky=tk.E)
        self.sms_smsc = tk.StringVar()
        self.sms_number_smsc = tk.Entry(self.sms, textvariable=self.sms_smsc, width=10)
        self.sms_number_smsc.grid(row=0,column=1, sticky=tk.W, pady=5)

        tk.Label(self.sms, justify=tk.LEFT, text='SMS pdu via Sim').grid(row=1,column=0, pady=5, sticky=tk.E)
        self.sms_content = tk.StringVar()
        self.sms_msg = tk.Entry(self.sms, textvariable=self.sms_content, width=58)
        self.sms_msg.grid(row=1,column=1, sticky=tk.W)
        tk.Button(self.sms, text="Send", command=self.send_sms_pdu).grid(row=1,column=2, padx=5, sticky=tk.E)

        tk.Label(self.sms, justify=tk.LEFT, text='SMS pdu via WAP Push').grid(row=2,column=0, pady=5, sticky=tk.E)
        self.wap_push_content = tk.StringVar()
        self.wap_push_msg = tk.Entry(self.sms, textvariable=self.wap_push_content, width=58)
        self.wap_push_msg.grid(row=2,column=1, sticky=tk.W)
        tk.Button(self.sms, text="Send", command=self.send_wap_push_pdu).grid(row=2,column=2, padx=5, sticky=tk.E)

        self.sms_content_frame = tk.Frame(self.sms)
        tk.Label(self.sms, justify=tk.LEFT, text='SMS text via Sim').grid(row=3,column=0, pady=5, sticky=tk.E+tk.N)
        self.sms_textLen = tk.StringVar()
        self.sms_text_lenlabel = tk.Label(self.sms, justify=tk.LEFT, textvariable=self.sms_textLen)
        self.sms_textLen.set("")
        self.sms_text_lenlabel.grid(row=3,column=0, pady=5, sticky=tk.E+tk.S)

        self.sms_text_content = tk.Text(self.sms_content_frame, width=55, height=3, wrap="word")
        self.sms_text_content.grid(row=0, column=0, pady=5)
        self.sms_text_content.bind("<KeyRelease>", self.updateLenCount) 
        self.sms_text_content.bind("<Key>", self.updateLenCount)

        sms_text_content_scrollBar = tk.Scrollbar(self.sms_content_frame)
        sms_text_content_scrollBar.grid(row=0, column=1, sticky=tk.N+tk.S)
        self.sms_text_content.config(yscrollcommand=sms_text_content_scrollBar.set)
        sms_text_content_scrollBar.config(command=self.sms_text_content.yview)
        self.sms_content_frame.grid(row=3, column=1, sticky=tk.W)

        tk.Button(self.sms, text="Send", command=self.send_sms_sim_text).grid(row=3,column=2, padx=5 ,sticky=tk.W+tk.S)


        self.sms.pack(padx=5, pady=5, ipadx=5, ipady=5)#, fill=tk.X)




#        self.lid = tk.Frame(self.area)
#
#        self.varLidClosed = tk.IntVar()
#        tk.Checkbutton(self.sms, text="Lid Closed", variable=self.varLidClosed, command=self.cmdLidClosed).grid(row=4,column=0)
#
#        self.varHandsFree = tk.IntVar()
#        tk.Checkbutton(self.sms, text="Hands Free", variable=self.varHandsFree, command=self.cmdHandsFree).grid(row=5,column=0)
#
#        self.varVoiceMailCount1 = tk.IntVar()
#        tk.Checkbutton(self.sms, text="Voicemail 1 active", variable=self.varVoiceMailCount1).grid(row=4,column=1)
#        self.varVoiceMailCount2 = tk.IntVar()
#        tk.Checkbutton(self.sms, text="Voicemail 2 active", variable=self.varVoiceMailCount2).grid(row=5,column=1)
#
#        self.varLed1stBacklight = tk.StringVar()
#        self.varLed1stBacklight.set("off")
#        self.varLedLabel = tk.Label(self.sms, textvariable=self.varLed1stBacklight, bg="black", fg="white")
#        self.varLedLabel.grid(row=6,column=0)
#
#        self.varLed2ndBacklight= tk.StringVar()
#        self.varLed2ndBacklight.set("Off Off Steady")
#        tk.Label(self.sms, textvariable=self.varLed2ndBacklight, bg="black", fg="white").grid(row=6,column=1)
#
#        self.varLedKeyBacklight = tk.StringVar()
#        self.varLedKeyBacklight.set(0)
#        self.varLedLabel = tk.Label(self.sms, textvariable=self.varLedKeyBacklight, bg="black", fg="white")
#        self.varLedLabel.grid(row=6,column=2)

        self.area.pack(expand=1, fill=tk.BOTH)

        # Info
        self.frame3 = tk.Frame(self.root)
        self.info = tk.StringVar()
        self.infolabel = tk.Label(self.frame3, justify=tk.LEFT, textvariable=self.info)
        self.infolabel.pack()
        self.frame3.pack()
        threading.Thread.__init__(self, name="GuiThread")

#    def led1stBacklight(self, status):
#        onoff = [
#            "Off",
#            "33%",								
#            "66%",
#            "100%"
#        ]
#        self.varLed1stBacklight.set(onoff[status])
#        #self.varLed1stBacklight.config(bg="black")
#
#    def ledKeyBacklight(self, status):
#        self.varLedKeyBacklight.set(status)
#        #self.varLedKeyBacklight.config(bg="black")
#
#    def led2ndBacklight(self, steady_colour, flash_colour, rate):
#        colours = [
#            "Off",
#            "Midnight",
#            "Skyblue",
#            "Cyan",
#            "Torquoise",
#            "Green",
#            "Lt Green",
#            "Yellow",
#            "Orange",
#            "Red",
#            "Purple",
#            "Magenta",
#            "Pearl",
#            "Gradation",
#        ]
#        rates = [
#            "Steady",
#            "Slow",
#            "Fast",
#            "Blink",
#        ]
#        self.varLed2ndBacklight.set(colours[steady_colour] + " " + colours[flash_colour] + " " + rates[rate])
#
#    def keypadButton(self, kpText, rowNo, colNo,  callback):
#        self.butt = tk.Button(self.phone, text=kpText, width=4)
#        self.butt.grid(row=rowNo, column=colNo)
#        self.butt.bind("<ButtonPress-1>", callback)
#        self.butt.bind("<ButtonRelease-1>", callback)

    def update_cc(self,ci):
        global st
        if st.activeCallIndex(ci):
            self.ccct[ci].set(st.callType(ci))
            self.cccs[ci].set(st.callState(ci))
            self.ccid[ci].set(st.callConnectedID(ci))
        else:
            self.ccct[ci].set('')
            self.cccs[ci].set('')
            self.ccid[ci].set('')
    # Update SIM status
    def update_sim(self):
        global st
        for no in range(2):
            self.simpin[no].set(st.PIN_code(no+1))
            self.simpintry[no].set(st.PIN_attempts(no+1))
            self.simpuk[no].set(st.PUK_code(no+1))
            self.simpuktry[no].set(st.PUK_attempts(no+1))
        
    def run(self):
        tk.mainloop()
        os._exit(0)

    # Enter in field
    def cc_call_enter(self, number):
        self.cc_call()

    # [CALL] Button pressed
    def cc_call(self):
        global st
        if st.registeredGSM() == TRUE:
            already_active = st.activeCallIndex()
            # Make a new call
            number = '"%s"' % self.call_number.get()
            ci = st.newCall(MTVOICE_CALL, CC_CALL_BEGINNING, number, 99)
            result = "%d=CI,0=CUG,0=AUX,0=TON,0=NPI,0=PRESENT,0=SCREEN,%s" % (ci,number)
            # Call already active ?
            if already_active:
                q.append_message(MSG_VOICECALL_WAITING_IND, result)
            else:
                q.append_message(MSG_INCOMING_CALL_IND, result)
            self.call_number.delete(0, tk.END)
            self.info.set('Calling from' + number) 
        else:
            self.info.set('Not registered yet') 
    def cc_hangup(self):
        global st
        if st.activeCallIndex():
            result = "%d,%s" % (st.ci, MNCAUSE_NORMAL_CALL_CLEARING)
            q.append_message(MSG_VOICECALL_RELEASE_IND, result)
            self.info.set('Hanging up active call') 
        else:
            self.info.set('No active call') 
    def temporaryFailure(self):
        global st
        # Any call active ?
        if st.activeCallIndex():
            if st.Release_Call == FALSE:
                self.info.set('Network temporary failure') 
                st.Release_Call = TRUE
        else:
            self.info.set('No active call') 
    def sim_inserted(self):
        global st
        if self.varSIMinserted.get() == FALSE:
		    st.SIM_removed(TRUE)
		    self.info.set('SIM Removed') 
        else:
            st.SIM_removed(FALSE)
            self.info.set('SIM Inserted') 
    def sim_unblock(self):
        global st
        if st.PIN_attempts(1) < 3:
            st.PIN_attempts(1,3)
            st.PIN_attempts(2,3)
            st.PUK_attempts(1,3)
            st.PUK_attempts(2,3)
            self.info.set('PIN/PUK Unblocked') 
        else:
            self.info.set('PIN/PUK not blocked') 
    def sim_block(self):
        global st
        if st.PIN_attempts(1) != 0:
            st.PIN_attempts(1,0)
            self.info.set('PIN1 Blocked') 
        else:
            self.info.set('PIN1 already blocked') 
    def cmdPinEnabled(self):
        if self.varPinEnabled.get() == TRUE:
            self.info.set('Need PIN code') 
        else:
            self.info.set('PIN Disabled') 
    def cmdALSEnabled(self):
        if self.varALSEnabled.get() == TRUE:
            self.info.set('Alternate Line Select Enabled')
        else:
            self.info.set('ALS Disabled')
    def cmdHaveSVC(self):
        if self.varHaveSVC.get() == TRUE:
            self.info.set('Have Service Provider name')
        else:
            self.info.set('No Service Provider name')
    def cmdSendRSSI(self):
        if self.varSendRSSI.get() == TRUE:
            self.info.set('Sending RSSI messages') 
        else:
            self.info.set('No RSSI messages') 

    def cmdSignallevel(self):
        self.info.set('Signal level set to %d on next update' % self.varSignallevel.get())


    def cmdSendBATTLEV(self):
        if self.varSendBATTLEV.get() == TRUE:
            self.info.set('Enable batt level messages') 
        else:
            self.info.set('No batt level messages') 

    def cmdBattlevel(self):
        self.info.set('Battery level set to %d on next update' % self.varBattlevel.get())

    def cmdBattlevelLowInd(self):
        self.varBattlevelLowInd.set(0)
        q.append_message(MSG_BATTMGR_BATT_LOW, "")

    def cmdBattlevelFullInd(self):
        self.varBattlevelFullInd.set(0)
        q.append_message(MSG_BATTMGR_BATT_FULL, "")

    def cmdChargerInserted(self):
        if self.varChargerInserted.get() == TRUE:
            self.info.set('Charger inserted')
            q.append_message(MSG_BATTMGR_CHARGING, "")
        else:
            self.info.set('Charger not inserted')
            q.append_message(MSG_BATTMGR_NOT_CHARGING, "")
    def cmdShfStatus(self):
        if self.varShfStatus.get() == TRUE:
            result = "1=Inserted"
            self.info.set('Secondary Hands Free kit inserted')
        else:
            result = "0=Removed"
            self.info.set('Secondary Hands Free kit removed')
        q.append_message(MSG_SHF_STATUS, result)
    def cmdNetworkNameInd(self):
        if self.varNetworkNameInd.get() == TRUE:
            self.info.set('Sending Network Name messages') 
        else:
            self.info.set('No Network Name messages') 

    def cmdvarRegisterGSM(self):
        if st.active:
            service = self.varRegisterGSM.get()
            if service == REG_STATE_NO_SERVICE:
                self.info.set('No GSM Network') 
            elif service == REG_STATE_UNKNOWN:
                self.info.set('GSM Network available (Unknown)') 
            elif service == REG_STATE_SEARCHING:
                self.info.set('GSM Network available (Searching)')
            else:
                if service == REG_STATE_NORMAL_SERVICE:
                    self.info.set('GSM Network available (Normal)') 
                elif service == REG_STATE_ROAMING_SERVICE:
                    self.info.set('GSM Network available (Roaming)') 
                elif service == REG_STATE_LIMITED_SERVICE:
                    self.info.set('GSM Network available (Limited)') 

                # send the network name if normal or roaming service
                if st.gui.varNetworkNameInd.get():
                    networkName = "\"%s\",\"%s\"" % (st.operatorLong, st.operatorShort)
                    q.append_message(MSG_NETWORK_NAME_IND, networkName, 6.0)

            result = "%s,%s" % (service,"0,0,0")
            q.append_message(MSG_REG_GSM_IND, result, 2.0)
        else:
            self.info.set('No active client') 
        return

    def cmdvarRegisterGPRS(self):
        if st.active:
            service = self.varRegisterGPRS.get()
            if service == REG_STATE_NO_SERVICE:
                self.info.set('No GPRS Network') 
            elif service == REG_STATE_UNKNOWN:
                self.info.set('GPRS Network available (Unknown)') 
            elif service == REG_STATE_SEARCHING:
                self.info.set('GPRS Network available (Searching)')
            elif service == REG_STATE_LIMITED_SERVICE:
                self.info.set('GPRS Network available (Limited)') 
            elif service == REG_STATE_NORMAL_SERVICE:
                self.info.set('GPRS Network available (Normal)') 
            elif service == REG_STATE_ROAMING_SERVICE:
                self.info.set('GPRS Network available (Roaming)') 

            result = "%s,%s" % (service,"0,0,0")
            q.append_message(MSG_REG_GPRS_IND, result, 2.0)
        else:
            self.info.set('No active client') 

    def cmdOperator(self):
        operator = self.varOperator.get()
        if operator == 0:
            self.info.set('Operator set to AT&T') 
            st.operator('ATWS', 'AT&T Wireless', 0x1300, 0x83)
        elif operator == 1:
            self.info.set('Operator set to Telenor') 
            st.operator('TELEN', 'N Telenor',0x42f2, 0x10) # BUG: TELEN ?
        elif operator == 2:
            self.info.set('Operator set to Netcom') 
            st.operator('NCOM"', 'N Netcom',0x42f2, 0x20)

    def cmdHomeOperator(self):
        HomeOperator = self.varHomeOperator.get()
        if HomeOperator == 0:
            self.info.set('Home operator set to AT&T')
            st.homeoperator(0x1300, 38)
        elif HomeOperator == 1:
            self.info.set('Home operator set to Telenor')
            st.homeoperator(0x4202, 0x10)
        elif HomeOperator == 2:
            self.info.set('Home operator set to Netcom')
            st.homeoperator(0x4202, 0x20)

    def cmdSatkEnabled(self):
        if self.varSatkEnabled.get() == TRUE:
            self.info.set('SATK enabled') 
        else:
            self.info.set('SATK disabled') 

    def pref_default(self):
        self.varPinEnabled.set(1)
        self.varSendRSSI.set(1)
        self.varSignallevel.set(PrefSignallevel)
        self.varNetworkNameInd.set(1)
        self.varSendBATTLEV.set(PrefSendBATTLEV)
        self.varBattlevel.set(PrefBattlevel)
        self.varChargerInserted.set(0)
        self.varHaveSVC.set(0)
        self.varALSEnabled.set(1)
        try:
            os.remove('preferences.py')
            os.remove('preferences.pyc')
        except:
            self.info.set('No preferences.py') 
        self.info.set('Setting default preferences') 

#    def cmdHasKeypad(self):
#        if self.varHasKeypad.get() == TRUE:
#            self.info.set('Keypad enabled, save and restart to update') 
#        else:
#            self.info.set('Keypad disabled, save and restart to update') 
    def cmdLargeFont(self):
        if self.varLargeFont.get() == TRUE:
            self.info.set('Large font, save and restart to update') 
        else:
            self.info.set('Small font, save and restart to update') 
    def pref_save(self):
        pref = open('preferences.py','w+')
        # Make the preferences file
        pref.write('# Saved with $Id: GUI.py,v 1.109 2004/07/29 14:19:19 perkristian Exp $\n')
        pref.write('prefALSEnabled     = ' + "%d\n" % self.varALSEnabled.get())
        pref.write('prefSIMinserted    = ' + "%d\n" % self.varSIMinserted.get())
        pref.write('prefHaveSVC        = ' + "%d\n" % self.varHaveSVC.get())
        pref.write('prefLargefont      = ' + "%d\n" % self.varLargeFont.get())
#        pref.write('prefLogKeypad      = ' + "%d\n" % self.varLogKeypad.get())
        pref.write('prefNetworkNameInd = ' + "%d\n" % self.varNetworkNameInd.get())
        pref.write('prefPinEnabled     = ' + "%d\n" % self.varPinEnabled.get())
        pref.write('prefRegisterGPRS   = ' + "%d\n" % self.varRegisterGPRS.get())
        pref.write('prefRegisterGSM    = ' + "%d\n" % self.varRegisterGSM.get())
#        pref.write('prefReplayKeypad   = ' + "%d\n" % self.varReplayKeypad.get())
        pref.write('prefSatkEnabled    = ' + "%d\n" % self.varSatkEnabled.get())
        pref.write('prefSendRSSI       = ' + "%d\n" % self.varSendRSSI.get())
        pref.write('prefSignallevel    = ' + "%d\n" % self.varSignallevel.get())
#        pref.write('prefSendBATTLEVEL  = ' + "%d\n" % self.varSendBATTLEV.get())
#        pref.write('prefBattlevel      = ' + "%d\n" % self.varBattlevel.get())
#        pref.write('prefShfStatus      = ' + "%d\n" % self.varShfStatus.get())
        pref.close()
        self.info.set('Preferences are saved to preferences.py')

    def send_modemStatus(self):
        q.append_message(MSG_MODEM_STATUS_IND, "%d" % (self.varModemStatus.get()))

    def send_kpKey(self, key, event):
        if st.active:
            if event.state == 0 or event.state == 8:
                self.push_start = time.time()
                result = "%s,%s" % (key, KEY_ACTION_PRESS)
            else:
                result = "%s,%s" % (key, KEY_ACTION_RELEASE)
            q.append_message("KPD_DRV_Callback", result)
            # Log all keypress to file ?
            if self.varLogKeypad.get():
                # File not open ?
                if st.fp == 0:
                    logfile = time.strftime("%d_%b_%y_%H_%M_%S",time.localtime())
                    self.info.set('Logging keypad press to %s' % logfile)
                    st.fp = open("kp_%s.log" % logfile , "w+")
                    if self.fp != 0:
                        self.fp.close()
                    self.fp = st.fp
                st.fp.write("%s %s %f\n" % ("KPD_DRV_Callback", result,
                            time.time() - st.startTime))
        else:
            self.info.set('No active client') 
    def button_f1(self, event):
        self.send_kpKey(KEY_SKL, event)
    def button_up(self, event):
        self.send_kpKey(KEY_UP, event)
    def button_f2(self, event):
        self.send_kpKey(KEY_SKR, event)
    def button_left(self, event):
        self.send_kpKey(KEY_LEFT, event)
    def button_sel(self, event):
        self.send_kpKey(KEY_SELECT, event)
    def button_right(self, event):
        self.send_kpKey(KEY_RIGHT, event)
    def button_down(self, event):
        self.send_kpKey(KEY_DOWN, event)
    def button_menu(self, event):
        self.send_kpKey(KEY_MENU, event)
    def button_pbook(self, event):
        self.send_kpKey(KEY_PHBOOK, event)
    def button_call(self, event):
        self.send_kpKey(KEY_SEND, event)
    def button_clr(self, event):
        self.send_kpKey(KEY_CLEAR, event)
    def button_hangup(self, event):
        self.send_kpKey(KEY_END, event)
    def button_1(self, event):
        self.send_kpKey(KEY_1, event)
    def button_2(self, event):
        self.send_kpKey(KEY_2, event)
    def button_3(self, event):
        self.send_kpKey(KEY_3, event)
    def button_4(self, event):
        self.send_kpKey(KEY_4, event)
    def button_5(self, event):
        self.send_kpKey(KEY_5, event)
    def button_6(self, event):
        self.send_kpKey(KEY_6, event)
    def button_7(self, event):
        self.send_kpKey(KEY_7, event)
    def button_8(self, event):
        self.send_kpKey(KEY_8, event)
    def button_9(self, event):
        self.send_kpKey(KEY_9, event)
    def button_0(self, event):
        self.send_kpKey(KEY_0, event)
    def button_star(self, event):
        self.send_kpKey(KEY_STAR, event)
    def button_hash(self, event):
        self.send_kpKey(KEY_POUND, event)
    def button_volUp(self, event):
        self.send_kpKey(KEY_VOL_UP, event)
    def button_volDown(self, event):
        self.send_kpKey(KEY_VOL_DOWN, event)
    def button_hsSw(self, event):
        self.send_kpKey(KEY_HSSW, event)

    
    def hup_function(self, ci):
        global st
        if st.activeCallIndex(ci):
            result = "%d,%s" % (ci, MNCAUSE_NORMAL_CALL_CLEARING)
            q.append_message(MSG_VOICECALL_RELEASE_IND, result)
            self.info.set('Hanging up CI %d' % ci) 
        else:
            self.info.set('CI %d not active' % ci) 
    def hup_func0(self):
        self.hup_function(0)
    def hup_func1(self):
        self.hup_function(1)
    def hup_func2(self):
        self.hup_function(2)
    def hup_func3(self):
        self.hup_function(3)
    def hup_func4(self):
        self.hup_function(4)
    def hup_func5(self):
        self.hup_function(5)
    def hup_func6(self):
        self.hup_function(6)
    def hup_func7(self):
        self.hup_function(7)
    def hup_func8(self):
        self.hup_function(8)
    def hup_func9(self):
        self.hup_function(9)

    def send_sms_sim_text(self):
        # strip out the line feed added by the text widget
        strippedLength = len(self.sms_text_content.get(1.0, tk.END))-1
        data = self.sms_text_content.get(1.0, tk.END)

        # encode the data as "Latin 1" or ISO-8859-1, which is the
        # standard 8-bit encoding for Western European languages 
        data = (data[0:strippedLength]).encode("Latin-1")

        segmentList = createSMSSegments(data, FALSE)
        for segment in segmentList:
            self.send_sms_sim_pdu(TRUE, '"' + segment + '"')
        self.info.set("SMS text message sent")
            

    def send_sms_sim_pdu(self, isSmsText = FALSE, inData = ""):
        if isSmsText == FALSE:
            msg = self.sms_content.get()
        else:
            msg = inData
        smsc = self.sms_smsc.get()


        if st.display_pref[1] == 2:
            result = '%s,%s,"%s","%s"' % (SMS_DELIVER, SIMACCESS_SUCCESS, msg, smsc)
            q.append_message(MSG_SMSPP_DELIVER_IND, result)
        # if display preference is 0 or 1 then message is saved and
        # a storage indication is sent to the client
        else:
            # Try to store the message in ME storage first and if that
            # fails try SIM storage
            rec_no = smsdb.findFree( int(ME_STORAGE[0]) )
            if rec_no != -1:
                smsdb.putRecord( int(ME_STORAGE[0]), rec_no, SMS_DELIVER, SIMSMSMESGSTATUS_UNREAD, smsc, msg )
                result = "%s,%d=rec_no,%s,%s" % (SIMACCESS_SUCCESS, rec_no, ME_STORAGE, SMS_STORAGE_WAIT_NONE)
            else:
                rec_no = smsdb.findFree( int(SM_STORAGE[0]) )
                if rec_no != -1:
                    smsdb.putRecord( int(SM_STORAGE[0]), rec_no, SMS_DELIVER, SIMSMSMESGSTATUS_UNREAD, smsc, msg )
                    result = "%s,%d=rec_no,%s,%s" % (SIMACCESS_SUCCESS, rec_no, SM_STORAGE, SMS_STORAGE_WAIT_NONE)
                else:                 
                    result = "%s,%d=rec_no,%s,%s" % (SIMACCESS_MEMORY_ERR, 0, st.pref_storage, SMS_STORAGE_WAIT_NONE)
            q.append_message(MSG_SMSPP_STORED_IND, result)

    def send_sms_pdu(self):
        self.send_sms_sim_pdu()

    def send_wap_push_pdu(self):
      if st.registeredGSM():
          msg = self.wap_push_content.get()
          smsc = self.sms_smsc.get()
          if msg !="" and smsc !="":
              result = '%s,%s,%s,%s' % (SMS_DELIVER, SIMACCESS_SUCCESS, msg, smsc)
              q.append_message(MSG_SMSPP_DELIVER_IND, result)
              self.info.set('WAP push message sent')
      else:
            self.info.set('Phone not connected') 

    def send_sms_vm(self):
        result = '%d,%d,0,0,%d,0' % ( self.varVoiceMailCount1.get(),
                                      self.varVoiceMailCount2.get(),
                  self.varVoiceMailCount1.get()+self.varVoiceMailCount2.get())
        q.append_message(MSG_VM_WAITING_IND , result)

    def send_sms_sim(self):
        global st
        if st.registeredGSM() == TRUE:
            msg = self.sms_content.get()
            result = '%s,%s,%s,%s' % (
                    SIMACCESS_SUCCESS,
                    "0=rec_no",
                    SM_STORAGE,
                    SMS_MT_STORAGE_WAIT)
            q.append_message(MSG_SIM_SMS_WRITE_RSP, result)
        else:
            self.info.set('Not registered yet') 

    def generate_mms_pdu(self):
        self.wap_push_msg.delete(0,tk.END)
        self.wap_push_msg.insert(0,"\"40069111111100F506062209370800730605040B8400010006266170706C69636174696F6E2F766E642E7761702E6D6D732D6D65737361676500AF84B4818DCA8C8298246D32008D908A808E02052088068104449D6A3496546573740083687474703A2F2F3132372E302E30302E313A313636342F6D6D73632F54483F7469643D3100\"")
        self.sms_number_smsc.delete(0,tk.END)
        self.sms_number_smsc.insert(0,"\"[]\"")

    def generate_sms_pdu(self):
        self.sms_msg.delete(0,tk.END)
        self.sms_msg.insert(0,"\"0006911111110002020301151659080CC8329BFD06DDDF72363904\"")
        self.sms_number_smsc.delete(0,tk.END)
        self.sms_number_smsc.insert(0,"\"[]\"")

    def cmdLidClosed(self):
        q.append_message("LID_status","%d" % (not self.varLidClosed.get()))

    def cmdHandsFree(self):
        q.append_message("Is_HANDS_FREE","%d" % self.varHandsFree.get())

    def cmdSsFail(self):
        if self.varSsFail.get() == TRUE:
            self.info.set('Supplementary services will fail') 
        else:
            self.info.set('Supplementary services will success') 

    def cmdCLIP(self):
        if self.varCLIP.get() == TRUE:
            self.info.set('CLIP Enabled')
        else:
            self.info.set('CLIP Disabled')

    def cmdCLIR(self):
        if self.varCLIR.get() == TRUE:
            self.info.set('CLIR Enabled')
        else:
            self.info.set('CLIR Disabled')

    def cmdCOLP(self):
        if self.varCOLP.get() == TRUE:
            self.info.set('COLP Enabled')
        else:
            self.info.set('COLP Disabled')

    def cmdCOLR(self):
        if self.varCOLR.get() == TRUE:
            self.info.set('COLR Enabled')
        else:
            self.info.set('COLR Disabled')

    def cmdPowerOnCause(self):
        if   self.varPowerOnCause.get() == POWER_ON_CAUSE_NORMAL:
            self.info.set('Power on Normal (keypad)')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_ALARM:
            self.info.set('Power on by Alarm timer')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_CHARGING_OFF:
            self.info.set('Power on by Charging Off')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_CHARGING_ON:
            self.info.set('Power on by Charging On')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_ERR_RESET:
            self.info.set('Power on by Assertion')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_STK_RESET:
            self.info.set('Power on by STK Reset')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_WATCHDOG_RESET:
            self.info.set('Power on by Watchdog')
        elif self.varPowerOnCause.get() == POWER_ON_CAUSE_USB_DL:
            self.info.set('Power on by USB Download')
        else:
            self.info.set('Unknown')


    def loopbackSMS(self):
        if self.varloopbackSMS.get():
            self.info.set('SMS loopback Enabled')
        else:
            self.info.set('SMS loopback Disabled')

    def loopbackMMS(self):
        if self.varloopbackMMS.get():
            self.info.set('MMS loopback Enabled')
        else:
            self.info.set('MMS loopback Disabled')

    def updateLenCount(self, event):
        # minus 1 for the line feed added by the text widget 
        # at the end added
        length = len(self.sms_text_content.get(1.0,tk.END))-1
        self.sms_textLen.set(length)

    def blink_field(self, field):
        for iterations in range(0, 2):
            field.config(bg="yellow")
            time.sleep(0.5)
            field.config(bg="white")
            time.sleep(0.5)

def change_theme(parent):
    print sys.platform
    if sys.platform[:3] == 'win' or sys.platform == 'cygwin':
        font=('lucida console', 8)
    else:
        font=('Fixed', 14)        # all text (Label, Button, Listbox....
    bg='grey88'                   # all backgrounds (Frame, Button etc)  
    tbg='white'                   # Text backgrounds (Entry, Listbox,Text)
    fg='black'                    # All foreground text 
    sbg='navy'                    # selected background
    sfg='white'                   # selected foreground 
    abg='grey77'                  # active background
    afg='black'                   # active foreground
    # all widgets
    parent.option_add('*background', bg)
    parent.option_add('*foreground', fg)
    parent.option_add('*activeBackground', abg)
    parent.option_add('*activeForeground', afg)
    parent.option_add('*selectBackground', sbg)
    parent.option_add('*selectForeground', sfg)
    if prefLargefont == 1:
        parent.option_add('*font', font) 
    # Listbox widget
    parent.option_add('*Listbox.background', tbg)
    # Text widget
    parent.option_add('*Text.background', tbg)
    # Entry widget
    parent.option_add('*Entry.background', tbg)
    # Canvas widget
    parent.option_add('*Canvas.background', tbg)
    parent.option_add('*Menu.background', tbg)

# Standalone test
if __name__ == '__main__':
    st = GSM_State()
    gui = GUI(st,queue(st))
    # Connect the GUI to the state
    st.setGUI(gui)
    gui.start()
