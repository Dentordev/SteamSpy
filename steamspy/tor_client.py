"""This is technically a forked version of torrequest but made for asyncio"""

from __future__ import annotations

from contextlib import asynccontextmanager

from .asynctor import open_controller, lauch_tor_with_context


@asynccontextmanager
async def launch_tor_optionally(
    tor: bool = False,
    proxy_port: int = 9050,
    ctrl_port: int = 9051,
    host: str = "127.0.0.1",
):
    if tor:
        async with lauch_tor_with_context(
            {"SocksPort": str(proxy_port), "ControlPort": str(ctrl_port)},
            take_ownership=True,
        ):
            async with open_controller(ctrl_port, host) as ctrl:
                yield ctrl
    else:
        yield


# NOTE: Not Required but feel free to use I wrote it by accident :)

# from typing_extensions import ParamSpec
# from typing import TypeVar, Callable, Awaitable

# P = ParamSpec("P")
# R = TypeVar("R")

# async def wrap_tor_optionally(tor:bool = False, ctrl_port: int = 9150, host: str = "127.0.0.1"):
#     """function wraps tor optionally"""
#     def wrapper(func:Callable[P, Awaitable[R]]):
#         async def decorator(*args:P.args, **kw:P.kwargs):
#             if tor:
#                 async with open_controller(ctrl_port, host):
#                     return await func(*args, **kw)
#             else:
#                 return await func(*args, **kw)
#         return decorator
#     return wrapper
