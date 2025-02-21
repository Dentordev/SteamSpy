from __future__ import annotations

import sys
import typer
import asyncio
from functools import wraps
import colorama

from typing import Union, Coroutine, Any, Awaitable, TypeVar, Callable, Optional

if sys.version_info < (3, 10):
    from typing_extensions import ParamSpec
else:
    from typing import ParamSpec

P = ParamSpec("P")
T = TypeVar("T")


def color_text(text, start, end, start_bg=None, end_bg=None):
    """Beautifies a title-screen on Windows & Linux"""
    ct = ""
    text = text.replace("\t", "    ")
    for i, char in enumerate(text):
        r = int(start[0] + (end[0] - start[0]) * (i / len(text)))
        g = int(start[1] + (end[1] - start[1]) * (i / len(text)))
        b = int(start[2] + (end[2] - start[2]) * (i / len(text)))
        if start_bg is not None and end_bg is not None:
            br = int(start_bg[0] + (end_bg[0] - start_bg[0]) * (i / len(text)))
            bg = int(start_bg[1] + (end_bg[1] - start_bg[1]) * (i / len(text)))
            bb = int(start_bg[2] + (end_bg[2] - start_bg[2]) * (i / len(text)))
            ct += f"\033[48;2;{br};{bg};{bb}m"
        else:
            ct += "\033[49m"
        ct += f"\033[38;2;{r};{g};{b}m{char}"
    return ct + "\033[0m"


def system_is_windows():
    return sys.platform in ["win32", "cygwin", "msys"]


def enhanced_run(
    main: Union[Coroutine[Any, Any, T], Awaitable[T]], debug: Optional[bool] = None
) -> T:
    """Runs an enhanced eventloop if one is discovered"""
    try:
        if system_is_windows():
            import winloop  # type: ignore

            return winloop.run(main, debug=debug)
        else:
            import uvloop  # type: ignore

            return uvloop.run(main, debug=debug)
    except ModuleNotFoundError:
        return asyncio.run(main, debug=debug)


# Forked from async_typer and gave it my own flare...
class EnhancedTyper(typer.Typer):
    """An Enhanced version of async_typer meant to provide uvloop/winloop at runtime"""

    def async_command(self, *args, **kwargs):
        def decorator(async_func: Callable[P, Awaitable[T]]):
            @wraps(async_func)
            def sync_func(*args: P.args, **kwargs: P.kwargs):
                return enhanced_run(async_func(*args, **kwargs))

            self.command(*args, **kwargs)(sync_func)
            return async_func

        return decorator


def banner():
    colorama.init(True)
    print(
        color_text(
            """
    =========    DentorDev 2025          Version 0.0.1          =========
                                                                         
    ███████ ████████ ███████  █████  ███    ███ ███████ ██████  ██    ██ 
    ██         ██    ██      ██   ██ ████  ████ ██      ██   ██  ██  ██  
    ███████    ██    █████   ███████ ██ ████ ██ ███████ ██████    ████   
         ██    ██    ██      ██   ██ ██  ██  ██      ██ ██         ██    
    ███████    ██    ███████ ██   ██ ██      ██ ███████ ██         ██    
                                                                         
    =========          Active Reacon & User Osint               ======== 
""",
            start=(0xBA, 0xBA, 0xFF),
            end=(0x10, 0x10, 0xAA),
            start_bg=(0x3A, 0x3A, 0x3A),
            end_bg=(0x11, 0x11, 0x11),
        )
    )
