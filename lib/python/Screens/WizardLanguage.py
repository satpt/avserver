from Components.International import international
from Components.Label import Label
from Components.Sources.StaticText import StaticText
from Screens.Wizard import Wizard


class WizardLanguage(Wizard):
	def __init__(self, session, showSteps=True, showStepSlider=True, showList=True, showConfig=True):
		Wizard.__init__(self, session, showSteps, showStepSlider, showList, showConfig)
		self.locales = []
		if international.packageDirectories:
			for package in international.packageDirectories:
				self.locales.append(international.packageToLocales(package)[0])
		if "en_US" not in self.locales:
			self.locales.append("en_US")
		self.locale = international.getLocale()
		self.localeIndex = 0
		if len(self.locales) > 1:
			self["key_red"] = StaticText(_("Change Locale"))
			try:
				self.localeIndex = self.locales.index(self.locale)
			except ValueError:
				pass
		else:
			self["key_red"] = StaticText("")
		self["localetext"] = Label()
		self.updateLanguageDescription()

	def red(self):
		self.resetCounter()
		self.languageSelect()

	def languageSelect(self):
		self.localeIndex += 1
		if self.localeIndex >= len(self.locales):
			self.localeIndex = 0
		self.locale = self.locales[self.localeIndex]
		international.activateLocale(self.locale)
		self.updateTexts()

	def updateLanguageDescription(self):
		self["localetext"].text = "%s:  %s (%s)  :  %s (%s)  :  %s" % (_("Locale"), international.getLanguageNative(self.locale), international.getCountryNative(self.locale), international.getLanguageName(self.locale), international.getCountryName(self.locale), self.locale)

	def updateTexts(self):
		self.updateText(firstset=True)
		self.updateValues()
		self.updateLanguageDescription()
