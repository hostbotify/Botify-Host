"""
Callback handlers for JhoomMusic Bot
"""

# Import all callback modules to register handlers
from . import main_menu
from . import commands_menu
from . import player_menu
from . import settings_menu
from . import diagnostics_menu

__all__ = [
    "main_menu",
    "commands_menu",
    "player_menu", 
    "settings_menu",
    "diagnostics_menu"
]