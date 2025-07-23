# Import all handlers to register them
from . import start_handler
from . import play_handler
from . import control_handler
from . import admin_handler
from . import callback_handler

__all__ = [
    "start_handler",
    "play_handler", 
    "control_handler",
    "admin_handler",
    "callback_handler"
]