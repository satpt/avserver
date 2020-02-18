# Fake module for Hisilicon compatibility
# Created by: leandrotsampa
# E-Mail: leandrotsampa@yahoo.com.br

DriverDate = "20200218"

def getMachineBuild():
	return "pixel"

def getMachineMake():
	return getMachineBuild()

def getMachineProcModel():
	return "hisilicon"

def getMachineBrand():
	return "Atto"

def getMachineName():
	if getMachineBuild() == "pixel":
		return "Pixel"
	else:
		return "Unknown"

def getMachineMtdKernel():
	return "mmcblk0p1"

def getMachineKernelFile():
	return "kernel_auto.bin"

def getMachineMtdRoot():
	return "mmcblk0p4"

def getMachineRootFile():
	return "rootfs.tar.bz2"

def getMachineMKUBIFS():
	return "-m 2048 -e 126976 -c  "

def getMachineUBINIZE():
	return "-m 2048 -p 128KiB"

def getBoxType():
	return getMachineBuild()

def getBrandOEM():
	return getMachineProcModel()

def getOEVersion():
	return "OE-Alliance 4.4"

def getDriverDate():
	return DriverDate

def getImageVersion():
	return "6.4"

def getImageBuild():
	return "000"

def getImageDevBuild():
	return "000"

def getImageType():
	return "release"

def getImageDistro():
    return "openatv"

def getImageFolder():
    return "atto/%s" % getMachineBuild()

def getImageFileSystem():
    return "tar.bz2 "

def getImageArch():
    return "armv7a-neon"

def getFeedsUrl():
    return ""

def getDisplayType():
    return ""

def getHaveHDMI():
    return True

def getHaveYUV():
    return False

def getHaveRCA():
    return False

def getHaveAVJACK():
    return False

def getHaveSCART():
    return False

def getHaveSCARTYUV():
    return False

def getHaveDVI():
    return False

def getHaveMiniTV():
    return False

def getHaveHDMIinHD():
    return False

def getHaveHDMIinFHD():
    return False

def getHaveWOL():
    return False

def getHaveWWOL():
    return False

def getHaveTranscoding1():
    return True

def getHaveTranscoding2():
    return True

def getHaveCI():
    return True