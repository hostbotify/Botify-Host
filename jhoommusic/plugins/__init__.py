"""
JhoomMusic Bot Plugins
All command and callback handlers are loaded from here
"""

# Import all command handlers to ensure they are registered
from .commands import *
from .callbacks import *

# Import individual plugins to ensure registration
from . import start
from . import ping  
from . import alive

__all__ = [
    "start",
    "ping", 
    "alive"
]