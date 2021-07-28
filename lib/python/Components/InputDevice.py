from fcntl import ioctl
from os import listdir, open as osopen, close as osclose, write as oswrite, O_RDWR, O_NONBLOCK
from os.path import isdir, isfile
from platform import machine
from boxbranding import getBoxType, getBrandOEM
from struct import pack

from Components.config import config, ConfigSubsection, ConfigInteger, ConfigYesNo, ConfigText, ConfigSlider
from Tools.Directories import pathExists
from six import ensure_str


class InputDevices:

	def __init__(self):
		self.Devices = {}
		self.currentDevice = ""
		devices = listdir("/dev/input/")

		for device in devices:
			try:
				_buffer = "\0" * 512
				self.fd = osopen("/dev/input/" + device, O_RDWR | O_NONBLOCK)
				self.name = ioctl(self.fd, self.EVIOCGNAME(256), _buffer)
				self.name = self.name[:self.name.find(b"\0")]
				self.name = ensure_str(self.name)
				if str(self.name).find("Keyboard") != -1:
					self.name = 'keyboard'
				osclose(self.fd)
			except (IOError, OSError) as err:
				print("[InputDevice] Error: device='%s' getInputDevices <ERROR: ioctl(EVIOCGNAME): '%s'>" % (device, str(err)))
				self.name = None

			if self.name:
				self.Devices[device] = {'name': self.name, 'type': self.getInputDeviceType(self.name), 'enabled': False, 'configuredName': None}
				if getBoxType().startswith('et'):
					self.setDeviceDefaults(device) # load default remote control "delay" and "repeat" values for ETxxxx ("QuickFix Scrollspeed Menues" proposed by Xtrend Support)

	def EVIOCGNAME(self, length):
		# include/uapi/asm-generic/ioctl.h
		IOC_NRBITS = 8
		IOC_TYPEBITS = 8
		IOC_SIZEBITS = 13 if "mips" in machine() else 14
		IOC_NRSHIFT = 0
		IOC_TYPESHIFT = IOC_NRSHIFT + IOC_NRBITS
		IOC_SIZESHIFT = IOC_TYPESHIFT + IOC_TYPEBITS
		IOC_DIRSHIFT = IOC_SIZESHIFT + IOC_SIZEBITS
		IOC_READ = 2
		return (IOC_READ << IOC_DIRSHIFT) | (length << IOC_SIZESHIFT) | (0x45 << IOC_TYPESHIFT) | (0x06 << IOC_NRSHIFT)

	def getDeviceAttribute(self, device, attribute):
		if device in self.Devices:
			if attribute in self.Devices[device]:
				return self.Devices[device][attribute]
		return None

	def getDeviceName(self, x):
		if x in list(self.Devices.keys()):
			return self.Devices[x].get("name", x)
		else:
			return "Unknown device name"

	def getDeviceList(self):
		return sorted(list(self.Devices.keys()))

	def getInputDeviceType(self, name):
		if "remote control" in name:
			return "remote"
		elif "keyboard" in name:
			return "keyboard"
		elif "mouse" in name:
			return "mouse"
		else:
			print("[InputDevices] Unknown device type: %s" % name)
			return None

	def setDeviceAttribute(self, device, attribute, value):
		#print "[InputDevices] setting for device", device, "attribute", attribute, " to value", value
		if device in self.Devices:
			self.Devices[device][attribute] = value

	#struct input_event {
	#	struct timeval time;    -> ignored
	#	__u16 type;             -> EV_REP (0x14)
	#	__u16 code;             -> REP_DELAY (0x00) or REP_PERIOD (0x01)
	#	__s32 value;            -> DEFAULTS: 700(REP_DELAY) or 100(REP_PERIOD)
	#}; -> size = 16

	def setDeviceDefaults(self, device):
		print("[InputDevices] setDeviceDefaults for device %s" % device)
		self.setDeviceAttribute(device, 'configuredName', None)
		eventRepeat = pack("LLHHi", 0, 0, 0x14, 0x01, 100)
		eventDelay = pack("LLHHi", 0, 0, 0x14, 0x00, 700)
		fd = osopen("/dev/input/%s" % device, O_RDWR)
		oswrite(fd, eventRepeat)
		oswrite(fd, eventDelay)
		osclose(fd)

	def setDeviceDelay(self, device, value): #REP_DELAY
		if self.getDeviceAttribute(device, 'enabled'):
			print("[InputDevices] setDeviceDelay for device %s to %d ms" % (device, value))
			event = pack('LLHHi', 0, 0, 0x14, 0x00, int(value))
			fd = osopen("/dev/input/" + device, O_RDWR)
			oswrite(fd, event)
			osclose(fd)

	def setDeviceName(self, device, value):
		#print "[InputDevices] setDeviceName for device %s to %s" % (device,value)
		self.setDeviceAttribute(device, 'configuredName', value)

	def setDeviceRepeat(self, device, value): #REP_PERIOD
		if self.getDeviceAttribute(device, 'enabled'):
			print("[InputDevices] setDeviceRepeat for device %s to %d ms" % (device, value))
			event = pack('LLHHi', 0, 0, 0x14, 0x01, int(value))
			fd = osopen("/dev/input/" + device, O_RDWR)
			oswrite(fd, event)
			osclose(fd)

	def setDeviceEnabled(self, device, value):
		oldval = self.getDeviceAttribute(device, 'enabled')
		#print "[InputDevices] setDeviceEnabled for device %s to %s from %s" % (device,value,oldval)
		self.setDeviceAttribute(device, 'enabled', value)
		if oldval is True and value is False:
			self.setDeviceDefaults(device)


class InitInputDevices:

	def __init__(self):
		self.currentDevice = ""
		config.inputDevices = ConfigSubsection()
		for device in sorted(list(iInputDevices.Devices.keys())):
			self.currentDevice = device
			#print "[InitInputDevices] -> creating config entry for device: %s -> %s  " % (self.currentDevice, iInputDevices.Devices[device]["name"])
			self.setupConfigEntries(self.currentDevice)
			self.currentDevice = ""

	def setupConfigEntries(self, device):
		setattr(config.inputDevices, device, ConfigSubsection())
		configItem = getattr(config.inputDevices, device)
		boxtype = getBoxType()
		configItem.enabled = ConfigYesNo(default=(boxtype == 'dm800' or boxtype == 'azboxhd'))
		configItem.enabled.addNotifier(self.inputDevicesEnabledChanged)
		configItem.name = ConfigText(default="")
		configItem.name.addNotifier(self.inputDevicesNameChanged)
		repeat = 100
		if boxtype in ('maram9', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo', 'galaxym6'):
			repeat = 400
		elif boxtype == 'azboxhd':
			repeat = 150
		configItem.repeat = ConfigSlider(default=repeat, increment = 10, limits=(0, 500))
		configItem.repeat.addNotifier(self.inputDevicesRepeatChanged)
		if boxtype in ('maram9', 'classm', 'axodin', 'axodinc', 'starsatlx', 'genius', 'evo', 'galaxym6'):
			delay = 200
		else:
			delay = 700
		configItem.delay = ConfigSlider(default=delay, increment = 100, limits=(0, 5000))
		configItem.delay.addNotifier(self.inputDevicesDelayChanged)

	def inputDevicesEnabledChanged(self, configElement):
		if self.currentDevice != "" and iInputDevices.currentDevice == "":
			iInputDevices.setDeviceEnabled(self.currentDevice, configElement.value)
		elif iInputDevices.currentDevice != "":
			iInputDevices.setDeviceEnabled(iInputDevices.currentDevice, configElement.value)

	def inputDevicesNameChanged(self, configElement):
		if self.currentDevice != "" and iInputDevices.currentDevice == "":
			iInputDevices.setDeviceName(self.currentDevice, configElement.value)
			if configElement.value != "":
				devname = iInputDevices.getDeviceAttribute(self.currentDevice, 'name')
				if devname != configElement.value:
					configItem = getattr(config.inputDevices, "%s.enabled" % self.currentDevice)
					configItem.value = False
					configItem.save()
		elif iInputDevices.currentDevice != "":
			iInputDevices.setDeviceName(iInputDevices.currentDevice, configElement.value)

	def inputDevicesRepeatChanged(self, configElement):
		if self.currentDevice != "" and iInputDevices.currentDevice == "":
			iInputDevices.setDeviceRepeat(self.currentDevice, configElement.value)
		elif iInputDevices.currentDevice != "":
			iInputDevices.setDeviceRepeat(iInputDevices.currentDevice, configElement.value)

	def inputDevicesDelayChanged(self, configElement):
		if self.currentDevice != "" and iInputDevices.currentDevice == "":
			iInputDevices.setDeviceDelay(self.currentDevice, configElement.value)
		elif iInputDevices.currentDevice != "":
			iInputDevices.setDeviceDelay(iInputDevices.currentDevice, configElement.value)


iInputDevices = InputDevices()


config.plugins.remotecontroltype = ConfigSubsection()
config.plugins.remotecontroltype.rctype = ConfigInteger(default=0)


class RcTypeControl():
	def __init__(self):
		if pathExists('/proc/stb/ir/rc/type') and getBrandOEM() not in ('gigablue', 'odin', 'ini', 'entwopia', 'tripledot'):
			self.isSupported = True

			if config.plugins.remotecontroltype.rctype.value != 0:
				self.writeRcType(config.plugins.remotecontroltype.rctype.value)
		else:
			self.isSupported = False

	def multipleRcSupported(self):
		return self.isSupported

	def writeRcType(self, rctype):
		fd = open('/proc/stb/ir/rc/type', 'w')
		fd.write('%d' % rctype)
		fd.close()


iRcTypeControl = RcTypeControl()
