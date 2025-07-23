"""
Command handlers for JhoomMusic Bot
"""

# Import all command modules to register handlers
from . import play
from . import controls
from . import admin
from . import player
from . import system
from . import ui
from . import diagnostics
from . import start

__all__ = [
    "play",
    "controls", 
    "admin",
    "player",
    "system",
    "ui",
    "diagnostics",
    "start"
]