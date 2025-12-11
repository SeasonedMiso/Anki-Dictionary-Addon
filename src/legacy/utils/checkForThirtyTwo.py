from aqt.qt import *
from .dialogs import ask_user as ask_user_dialog
from anki.utils import is_win, is_mac
from anki.hooks import addHook
from aqt.utils import openLink


def checkForThirtyTwo():
	if is_win or is_mac:
		qVer = QT_VERSION_STR
		invalid = ['5.12.6', '5.9.7']
		if qVer in invalid:
			msg = 'You are on 32-bit Anki!\n32-bit Anki has known compatibility issues with these addons.\n\nIf you\'re on a 64-bit system, please update to the 64-bit version of Anki.'
			if ask_user_dialog(msg, customText = ["Download Now! 😄", "I like 32 bit. 🥺"]):
				openLink("https://apps.ankiweb.net/")
addHook("profileLoaded", checkForThirtyTwo)