from Screens.HelpMenu import ShowRemoteControl

# Fallback class for old plugins
class Rc(ShowRemoteControl):
	def __init__(self):
		ShowRemoteControl.__init__(self)
