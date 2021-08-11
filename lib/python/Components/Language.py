from traceback import print_stack

from Components.International import international


# WARNING:  Old code refers to locales as languages!
#
class Language:
	def __init__(self):
		# print("[Language] International class already initialised.")
		pass

	def InitLang(self):
		pass

	def activateLanguage(self, language):
		international.activateLocale(language)

	def getActiveLanguage(self):
		international.getLocale()

	def addCallback(self, callback):
		if callable(callback):
			international.addCallback(callback)
		elif callback:
			print("[Language] addCallback Error: The callback '%s' is not callable!" % callback)
			print_stack()
		else:
			print("[Language] addCallback Error: The callback is blank or None!")
			print_stack()

	def getLanguage(self):
		return international.getLocale()

	def getLanguageList(self):
		languageList = []
		for language in international.getLanguageList():
			country = international.getLanguageCountryCode(language)
			locale = "%s_%s" % (language, country if country else "??")
			languageList.append((locale, (international.getLanguageNative(language), language, country, international.getLanguageEncoding(language))))
		return languageList


language = Language()
