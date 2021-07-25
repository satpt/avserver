from __future__ import print_function
from __future__ import absolute_import
from enigma import eListboxPythonMultiContent, eListbox, gFont
from Screens.Screen import Screen
from Components.Pixmap import MovingPixmap, MultiPixmap
from Components.Label import Label
from Components.ActionMap import ActionMap, queryKeyBinding
from Components.GUIComponent import GUIComponent
from Components.RcModel import rc_model
from Components.config import config
from Tools.KeyBindings import getKeyDescription
from Tools.Directories import resolveFilename, SCOPE_SKIN
import skin

from xml.etree.ElementTree import ElementTree
from boxbranding import getBoxType


class ShowRemoteControl:
	def __init__(self):
		self["rc"] = MultiPixmap()
		self["arrowdown"] = MovingPixmap()
		self["arrowdown2"] = MovingPixmap()
		self["arrowup"] = MovingPixmap()
		self["arrowup2"] = MovingPixmap()

		self.isDefaultRc = rc_model.rcIsDefault()
		self.rcheight = 500
		self.rcheighthalf = 250

		self.selectpics = []
		self.selectpics.append((self.rcheighthalf, ["arrowdown", "arrowdown2"], (-18, -70)))
		self.selectpics.append((self.rcheight, ["arrowup", "arrowup2"], (-18, 0)))

		self.readPositions()
		self.clearSelectedKeys()
		self.onShown.append(self.initRc)

	def initRc(self):
		if getBoxType() in ('uniboxhd1', 'uniboxhd2', 'uniboxhd3', 'sezam5000hd', 'mbtwin', 'beyonwizt3'):
			self["rc"].setPixmapNum(config.misc.rcused.value)
		else:
			if self.isDefaultRc:
				self["rc"].setPixmapNum(config.misc.rcused.value)
			else:
				self["rc"].setPixmapNum(0)

	def readPositions(self):
		if self.isDefaultRc:
			target = resolveFilename(SCOPE_SKIN, "rcpositions.xml")
		else:
			target = rc_model.getRcLocation() + 'rcpositions.xml'
		tree = ElementTree(file=target)
		rcs = tree.getroot()
		self.rcs = {}
		for rc in rcs:
			id = int(rc.attrib["id"])
			self.rcs[id] = {}
			for key in rc:
				name = key.attrib["name"]
				pos = key.attrib["pos"].split(",")
				self.rcs[id][name] = (int(pos[0]), int(pos[1]))

	def getSelectPic(self, pos):
		for selectPic in self.selectpics:
			if pos[1] <= selectPic[0]:
				return selectPic[1], selectPic[2]
		return None

	def hideRc(self):
		self["rc"].hide()
		self.hideSelectPics()

	def showRc(self):
		self["rc"].show()

	def selectKey(self, key):
		if self.isDefaultRc:
			rc = self.rcs[config.misc.rcused.value]
		else:
			try:
				rc = self.rcs[2]
			except:
				rc = self.rcs[config.misc.rcused.value]

		if key in rc:
			rcpos = self["rc"].getPosition()
			pos = rc[key]
			selectPics = self.getSelectPic(pos)
			selectPic = None
			for x in selectPics[0]:
				if x not in self.selectedKeys:
					selectPic = x
					break
			if selectPic is not None:
				print("selectPic:", selectPic)
				self[selectPic].moveTo(rcpos[0] + pos[0] + selectPics[1][0], rcpos[1] + pos[1] + selectPics[1][1], 1)
				self[selectPic].startMoving()
				self[selectPic].show()
				self.selectedKeys.append(selectPic)

	def clearSelectedKeys(self):
		self.showRc()
		self.selectedKeys = []
		self.hideSelectPics()

	def hideSelectPics(self):
		for selectPic in self.selectpics:
			for pic in selectPic[1]:
				self[pic].hide()


class HelpMenu(Screen, Rc):
	def __init__(self, session, list):
		Screen.__init__(self, session)
		Screen.setTitle(self, _("Help"))
		self.onSelChanged = []
		self["list"] = HelpMenuList(list, self.close)
		self["list"].onSelChanged.append(self.SelectionChanged)
		Rc.__init__(self)
		self["long_key"] = Label("")

		self["actions"] = ActionMap(["WizardActions"],
		{
			"ok": self["list"].ok,
			"back": self.close,
		}, -1)

		self.onLayoutFinish.append(self.SelectionChanged)

	def SelectionChanged(self):
		self.clearSelectedKeys()
		selection = self["list"].getCurrent()
		if selection:
			selection = selection[3]
		#arrow = self["arrowup"]
		#print("selection:", selection)

		longText = ""
		if selection and len(selection) > 1:
			if selection[1] == "SHIFT":
				self.selectKey("SHIFT")
			elif selection[1] == "long":
				longText = _("Long key press")
		self["long_key"].setText(longText)

		self.selectKey(selection[0])
		#if selection is None:
		print("select arrow")
		#	arrow.moveTo(selection[1], selection[2], 1)
		#	arrow.startMoving()
		#	arrow.show()


class HelpableScreen:
	def __init__(self):
		self["helpActions"] = ActionMap(["HelpActions"],
			{
				"displayHelp": self.showHelp,
			})

	def showHelp(self):
		try:
			if self.secondInfoBarScreen and self.secondInfoBarScreen.shown:
				self.secondInfoBarScreen.hide()
		except:
			pass
		self.session.openWithCallback(self.callHelpAction, HelpMenu, self.helpList)

	def callHelpAction(self, *args):
		if args:
			(actionmap, context, action) = args
			actionmap.action(context, action)


class HelpMenuList(GUIComponent):
	def __init__(self, helplist, callback):
		GUIComponent.__init__(self)
		self.onSelChanged = []
		self.l = eListboxPythonMultiContent()
		self.callback = callback
		self.extendedHelp = False

		l = []
		for (actionmap, context, actions) in helplist:
			for (action, help) in actions:
				if hasattr(help, '__call__'):
					help = help()
				if not help:
					continue
				buttons = queryKeyBinding(context, action)

				# do not display entries which are not accessible from keys
				if not len(buttons):
					continue

				name = None
				flags = 0

				for n in buttons:
					(name, flags) = (getKeyDescription(n[0]), n[1])
					if name is not None:
						break

				# only show entries with keys that are available on the used rc
				if name is None:
					continue

				if flags & 8: # for long keypresses, prepend l_ into the key name.
					name = (name[0], "long")

				entry = [(actionmap, context, action, name)]

				if isinstance(help, list):
					self.extendedHelp = True
					print("extendedHelpEntry found")
					x, y, w, h = skin.parameters.get("HelpMenuListExtHlp0", (0, 0, 600, 26))
					x1, y1, w1, h1 = skin.parameters.get("HelpMenuListExtHlp1", (0, 28, 600, 20))
					entry.extend((
						(eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 0, 0, help[0]),
						(eListboxPythonMultiContent.TYPE_TEXT, x1, y1, w1, h1, 1, 0, help[1])
					))
				else:
					x, y, w, h = skin.parameters.get("HelpMenuListHlp", (0, 0, 600, 28))
					entry.append((eListboxPythonMultiContent.TYPE_TEXT, x, y, w, h, 0, 0, help))

				l.append(entry)

		self.l.setList(l)
		if self.extendedHelp is True:
			font = skin.fonts.get("HelpMenuListExt0", ("Regular", 24, 50))
			self.l.setFont(0, gFont(font[0], font[1]))
			self.l.setItemHeight(font[2])
			font = skin.fonts.get("HelpMenuListExt1", ("Regular", 18))
			self.l.setFont(1, gFont(font[0], font[1]))
		else:
			font = skin.fonts.get("HelpMenuList", ("Regular", 24, 38))
			self.l.setFont(0, gFont(font[0], font[1]))
			self.l.setItemHeight(font[2])

	def ok(self):
		# a list entry has a "private" tuple as first entry...
		l = self.getCurrent()
		if l is None:
			return
		# ...containing (Actionmap, Context, Action, keydata).
		# we returns this tuple to the callback.
		self.callback(l[0], l[1], l[2])

	def getCurrent(self):
		sel = self.l.getCurrentSelection()
		return sel and sel[0]

	GUI_WIDGET = eListbox

	def postWidgetCreate(self, instance):
		instance.setContent(self.l)
		instance.selectionChanged.get().append(self.selectionChanged)
		self.instance.setWrapAround(True)

	def preWidgetRemove(self, instance):
		instance.setContent(None)
		instance.selectionChanged.get().remove(self.selectionChanged)

	def selectionChanged(self):
		for x in self.onSelChanged:
			x()
