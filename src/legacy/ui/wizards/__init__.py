# -*- coding: utf-8 -*-
"""
UI Wizards Module

Contains wizard dialogs for dictionary installation and configuration.
"""

from .dict_wizard import MiWizard, MiWizardPage
from .dictionaryWebInstallWizard import DictionaryWebInstallWizard
from .freqConjWebWindow import FreqConjWebWindow

__all__ = [
    'MiWizard',
    'MiWizardPage',
    'DictionaryWebInstallWizard',
    'FreqConjWebWindow',
]
