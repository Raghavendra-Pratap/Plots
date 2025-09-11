"""
Pages package for Unified Plotter.

Contains all UI page modules for different screens.
"""

from .welcome_page import WelcomePage
from .settings_page import SettingsPage
from .error_page import ErrorPage
from .loading_page import LoadingPage
from .progress_page import ProgressPage

__all__ = [
    'WelcomePage',
    'SettingsPage', 
    'ErrorPage',
    'LoadingPage',
    'ProgressPage'
]
