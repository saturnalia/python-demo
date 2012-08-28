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
#
# Compile all python source files (*.py) in this directory.
#
import compileall

print "Compiling sources..."

compileall.compile_dir(".", force=1)
