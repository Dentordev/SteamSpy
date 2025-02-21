"""
asynctor
--------

This is essentailly an asynchronous version of the tor stem library
made with only asyncio and no additional dependencies

Feel Free to copy and paste whater parts of the code you are looking for.
It's only 2 modules and both can be ran independently...
"""

from .controller import AsyncController, open_controller
from .launcher import lauch_tor_with_config, lauch_tor_with_context, launch_tor

__author__ = "DentorDev"
__version__ = "0.0.1"
__license__ = """LGPLv3"""
