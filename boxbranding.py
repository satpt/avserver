# Fake module for Hisilicon compatibility
# Created by: leandrotsampa
# E-Mail: leandrotsampa@yahoo.com.br

def getValueFromFile(file, return_if_failed):
	try:
		fd = open(file, "r")
		return fd.read().rstrip('\n')
	except:
		return return_if_failed

def getMachineBuild():
	return getValueFromFile("/proc/stb/info/model", "")

def getMachineMake():
	return getMachineBuild()

def getMachineProcModel():
	return getValueFromFile("/proc/stb/info/boxtype", "")

def getMachineBrand():
	if getMachineBuild() in [ "ismart", "pixel", "ppremium" ]:
		return "Atto"
	elif getMachineBuild() in [ "poplar" ]:
		return "96Boards"
	elif getMachineBuild() in [ "u5pvr" ]:
		return "SmartSTB"
	elif getMachineBuild() in [ "smini" ]:
		return "Formuler"
	else:
		return "Unknown"

def getMachineName():
	if getMachineBuild() == "ismart":
		return "i-Smart"
	elif getMachineBuild() == "pixel":
		return "Pixel"
	elif getMachineBuild() == "ppremium":
		return "Pixel Premium"
	elif getMachineBuild() == "poplar":
		return "Poplar"
	elif getMachineBuild() == "u5pvr":
		return "U5-PVR"
	elif getMachineBuild() == "smini":
		return "S-Mini"
	else:
		return "Unknown"

def getMachineMtdKernel():
	return "mmcblk0p11"

def getMachineKernelFile():
	return "boot.img"

def getMachineMtdRoot():
	return "mmcblk1"

def getMachineRootFile():
	return "e2d-armhf-pixel.img"

def getMachineMKUBIFS():
	return ""

def getMachineUBINIZE():
	return ""

def getBoxType():
	return getMachineBuild()

def getBrandOEM():
	return getMachineProcModel()

def getOEVersion():
	return "OE-Alliance 4.4"

def getDriverDate():
	# apt install python-dateutil
	from dateutil.parser import parse
	kVersion = getValueFromFile("/proc/version", "")
	kDateTime = parse(kVersion[kVersion.index("SMP ")+4:])
	return kDateTime.strftime('%Y%m%d')

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
    return "img"

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