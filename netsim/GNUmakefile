# ****************************************************************************
# *
# *		Copyright (c) 2005 Broadcom Corporation
# *		All Rights Reserved
# *
# *		No portions of this material may be reproduced in any form without the
# *		written permission of:
# *
# *			Broadcom Corporation
# *			16215 Alton Parkway
# *			P.O. Box 57013
# *			Irvine, California 92619-7013
# *
# *		All information contained in this document is Broadcom Corporation
# *		company private, proprietary, and trade secret.
# *
# *****************************************************************************

MSP_HOME=../..

include $(MSP_HOME)/env/platform.gmk
include $(MSP_HOME)/env/stddefs.gmk

PYTHON	=	python
CC		=	cl
CFLAGS	= /D"_$(BASEBAND_CHIP)_" /DCHIP_REVISION=$(CHIP_REVISION) /DSDTENV /DSTACK_$(PRJ_STACK)  /DSTACK_$(__PRJ_STACK) /DMSP $(PMU_MODULE) /D_CRT_SECURE_NO_DEPRECATE 

#all: taskmsgs.py ms_pwron_enum.py mstypes.py mstypes_enum.py smsutil.py callctrl.py sim.py resultcode.py \
#    smsapi.py stk_api.py stk_def.py ss_api.py msnu.py kpd_drv.py common_defs.py \
#    dataComm.py dataacct_api.py pchtypes.py serialapi.py phonebk.py phonebk_api.py common_cc_ds.py \
#		 common_sms.py pch_def.py dataacct_def.py sim_api.py sim_def.py sim_common.py capi2_ss_ds.py

BUILT_SOURCES  = taskmsgs.py ms_pwron_enum.py mstypes.py mstypes_enum.py smsutil.py callctrl.py sim.py resultcode.py \
    smsapi.py stk_api.py stk_def.py ss_api.py msnu.py kpd_drv.py common_defs.py \
    dataComm.py dataacct_api.py pchtypes.py serialapi.py phonebk.py phonebk_api.py common_cc_ds.py \
    common_sms.py pch_def.py dataacct_def.py sim_api.py sim_def.py sim_common.py capi2_ss_ds.py 

COMPILED_SOURCES = $(addsuffix .pyc,$(basename ${BUILT_SOURCES}))

all			:	
				@$(VERIFY_PLATFORM) || exit 1
				@$(MAKE) PLATFORM=$(GET_PLATFORM) all_r

clean		:	
				@$(VERIFY_PLATFORM) || exit 1
				@$(MAKE) PLATFORM=$(GET_PLATFORM) clean_r

all_r :	$(BUILT_SOURCES) $(COMPILED_SOURCES)

clean_r:	
	$(RM) $(CLEANFILES)

CLEANFILES = *.pyc taskmsgs.py smsutil.py ms_pwron_enum.py mstypes.py  mstypes_enum.py callctrl.py sim.py \
     resultcode.py smsapi.py stk_api.py stk_def.py ss_api.py kpd_drv.py msnu.py \
     dataComm.py dataacct_api.py pchtypes.py serialapi.py phonebk.py phonebk_api.py sim_brcm.py \
     common_cc_ds.py common_sms.py pch_def.py dataacct_def.py sim_api.py sim_common.py sim_def.py \
     capi2_ss_ds.py  common_defs.py \
	 $(COMPILED_SOURCES)

INCLUDES = \
  -I $(MSP_HOME)/inc \
  -I $(MSP_HOME)/dev/inc \
  -I $(MSP_HOME)/debug/inc \
  -I $(MSP_HOME)/sim/inc \
  -I $(MSP_HOME)/sms/inc \
  -I $(MSP_HOME)/mpx/inc \
  -I $(MSP_HOME)/msc/inc \
  -I $(MSP_HOME)/ecdc/inc \
  -I $(MSP_HOME)/pch/inc \
  -I $(MSP_HOME)/util/inc \
  -I $(MSP_HOME)/public/inc \
  -I $(MSP_HOME)/simlock/inc \
  -I $(MSP_HOME)/capi2/inc \
  -I $(MSP_HOME)/capi2/ss/inc \
  -I $(MSP_HOME)/capi2/lcs/inc \
  -I $(MSP_HOME)/baseband/inc \
  -I $(MSP_HOME)/rtos/inc \
  -I $(MSP_HOME)/rtos/nucleus/inc \
  -I $(MSP_HOME)/stack/$(PRJ_STACK)/inc \
  -I $(MSP_HOME)/stack/$(PRJ_STACK)/sdtc \
  -I $(MSP_HOME)/baseband/arm/$(BASEBAND_CHIP)/inc \
  -I $(MSP_HOME)/DSP/inc \
  -I $(MSP_HOME)/HAL/inc \
  -I $(MSP_HOME)/system/inc \
  -I $(MSP_HOME)/dlink_multi/ip/inc \
  -I $(MSP_HOME)/phy/inc

taskmsgs.py: $(MSP_HOME)/inc/taskmsgs.h
	$(PYTHON) extractenums.py $(MSP_HOME)/inc/taskmsgs.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_taskmsgs mk_taskmsgs.c
	./mk_taskmsgs
	rm mk_taskmsgs*

ms_pwron_enum.py: $(MSP_HOME)/inc/ms_pwron_enum.h
	$(PYTHON) extract_pwron_enum.py $(MSP_HOME)/inc/ms_pwron_enum.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_ms_pwron_enum mk_ms_pwron_enum.c
	./mk_ms_pwron_enum
	rm mk_ms_pwron_enum*
	
mstypes.py: $(MSP_HOME)/inc/mstypes.h
	$(PYTHON) extractenums.py $(MSP_HOME)/inc/mstypes.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_mstypes mk_mstypes.c
	./mk_mstypes
	rm mk_mstypes*

mstypes_enum.py: $(MSP_HOME)/inc/mstypes_enum.h
	$(PYTHON) extractenums.py $(MSP_HOME)/inc/mstypes_enum.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_mstypes_enum mk_mstypes_enum.c
	./mk_mstypes_enum
	rm mk_mstypes_enum*
	
smsutil.py : $(MSP_HOME)/sms/inc/smsutil.h
	$(PYTHON) extractenums.py $(MSP_HOME)/sms/inc/smsutil.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_smsutil mk_smsutil.c
	./mk_smsutil
	rm mk_smsutil*

kpd_drv.py: $(MSP_HOME)/baseband/inc/kpd_drv.h
	$(PYTHON) extractenums.py $(MSP_HOME)/baseband/inc/kpd_drv.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_kpd_drv mk_kpd_drv.c
	./mk_kpd_drv
	rm mk_kpd_drv*

callctrl.py : $(MSP_HOME)/msc/inc/callctrl.h
	$(PYTHON) extractenums.py $(MSP_HOME)/msc/inc/callctrl.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_callctrl mk_callctrl.c
	./mk_callctrl
	rm mk_callctrl*

sim.py : $(MSP_HOME)/sim/inc/sim_brcm.h
	$(PYTHON) extractenums.py $(MSP_HOME)/sim/inc/sim_brcm.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_sim_brcm mk_sim_brcm.c
	./mk_sim_brcm
	rm mk_sim_brcm*

sim_api.py : $(MSP_HOME)/public/inc/sim_api.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/sim_api.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_sim_api mk_sim_api.c
	./mk_sim_api
	rm mk_sim_api*

sim_def.py : $(MSP_HOME)/public/inc/sim_def.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/sim_def.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_sim_def mk_sim_def.c
	./mk_sim_def
	rm mk_sim_def*

sim_common.py : $(MSP_HOME)/public/inc/sim_common.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/sim_common.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_sim_common mk_sim_common.c
	./mk_sim_common
	rm mk_sim_common*
		
resultcode.py : $(MSP_HOME)/inc/resultcode.h
	$(PYTHON) extractenums.py $(MSP_HOME)/inc/resultcode.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_resultcode mk_resultcode.c
	./mk_resultcode
	rm mk_resultcode*

smsapi.py : $(MSP_HOME)/sms/inc/smsapi.h
	$(PYTHON) extractenums.py $(MSP_HOME)/sms/inc/smsapi.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_smsapi mk_smsapi.c
	./mk_smsapi
	rm mk_smsapi*

stk_api.py : $(MSP_HOME)/public/inc/stk_api.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/stk_api.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_stk_api mk_stk_api.c
	./mk_stk_api
	rm mk_stk_api*

stk_def.py : $(MSP_HOME)/public/inc/stk_def.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/stk_def.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_stk_def mk_stk_def.c
	./mk_stk_def
	rm mk_stk_def*
	
ss_api.py : $(MSP_HOME)/msc/inc/ss_api.h
	$(PYTHON) extractenums.py $(MSP_HOME)/msc/inc/ss_api.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_ss_api mk_ss_api.c
	./mk_ss_api
	rm mk_ss_api*

msnu.py : $(MSP_HOME)/stack/$(PRJ_STACK)/sdtc/msnu.h
	$(PYTHON) extractenums.py $(MSP_HOME)/stack/$(PRJ_STACK)/sdtc/msnu.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_msnu mk_msnu.c
	./mk_msnu
	rm mk_msnu*

dataComm.py : $(MSP_HOME)/dlink_multi/ppp/inc/dataComm.h
	$(PYTHON) extractenums.py $(MSP_HOME)/dlink_multi/ppp/inc/dataComm.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_dataComm mk_dataComm.c
	./mk_dataComm
	rm mk_dataComm*

dataacct_api.py : $(MSP_HOME)/public/inc/dataacct_api.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/dataacct_api.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_dataacct_api mk_dataacct_api.c
	./mk_dataacct_api
	rm mk_dataacct_api*

dataacct_def.py : $(MSP_HOME)/public/inc/dataacct_def.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/dataacct_def.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_dataacct_def mk_dataacct_def.c
	./mk_dataacct_def
	rm mk_dataacct_def*
	
pchtypes.py : $(MSP_HOME)/inc/pchtypes.h
	$(PYTHON) extractenums.py $(MSP_HOME)/inc/pchtypes.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_pchtypes mk_pchtypes.c
	./mk_pchtypes
	rm mk_pchtypes*

serialapi.py : $(MSP_HOME)/baseband/inc/serialapi.h
	$(PYTHON) extractenums.py $(MSP_HOME)/baseband/inc/serialapi.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_serialapi mk_serialapi.c
	./mk_serialapi
	rm mk_serialapi*

phonebk.py : $(MSP_HOME)/phonebk/inc/phonebk.h
	$(PYTHON) extractenums.py $(MSP_HOME)/phonebk/inc/phonebk.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_phonebk mk_phonebk.c
	./mk_phonebk
	rm mk_phonebk*

phonebk_api.py : $(MSP_HOME)/public/inc/phonebk_api.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/phonebk_api.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_phonebk_api mk_phonebk_api.c
	./mk_phonebk_api
	rm mk_phonebk_api*

common_cc_ds.py: $(MSP_HOME)/public/inc/common_cc_ds.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/common_cc_ds.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_common_cc_ds mk_common_cc_ds.c
	./mk_common_cc_ds
	rm mk_common_cc_ds*

common_sms.py: $(MSP_HOME)/public/inc/common_sms.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/common_sms.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_common_sms mk_common_sms.c
	./mk_common_sms
	rm mk_common_sms*

common_defs.py: $(MSP_HOME)/public/inc/common_defs.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/common_defs.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_common_defs mk_common_defs.c
	./mk_common_defs
	rm mk_common_defs*
	
pch_def.py: $(MSP_HOME)/public/inc/pch_def.h
	$(PYTHON) extractenums.py $(MSP_HOME)/public/inc/pch_def.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_pch_def mk_pch_def.c
	./mk_pch_def
	rm mk_pch_def*
		
capi2_ss_ds.py: $(MSP_HOME)/capi2/ss/inc/capi2_ss_ds.h
	$(PYTHON) extractenums.py $(MSP_HOME)/capi2/ss/inc/capi2_ss_ds.h
	$(CC) $(CFLAGS) ${INCLUDES} -o mk_capi2_ss_ds mk_capi2_ss_ds.c
	./mk_capi2_ss_ds
	rm mk_capi2_ss_ds*

$(COMPILED_SOURCES) : $(BUILT_SOURCES)
	$(PYTHON) compileall-wrapper.py
	rm -f compileall-wrapper.pyc
