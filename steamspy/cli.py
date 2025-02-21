from __future__ import annotations
from .cli_tools import EnhancedTyper, banner
from .request import SteamUser, SteamFriend, scrape_user
from .tor_client import launch_tor_optionally
from typing import Annotated, Union, Optional, Sequence
import asyncio
import random
import typer
from click import style
from aiohttp import ClientResponseError


async def jitter():
    return await asyncio.sleep(random.uniform(1, 3))


def color_item(name, item: str):
    print(style(f"- {name}: {item}", fg="bright_blue"))


def friends_divider():
    print(
        style(
            "------------------------------------------------------", fg="bright_yellow"
        )
    )


def print_user(user: SteamUser):
    color_item("Private", f"{user.private}")
    if not user.private:
        color_item("Online", f"{user.online}")
    color_item("Name", f"{user.name}")
    color_item("ID", f"{user.id}")
    color_item("Profile Picture", f"{user.profile_pic}")


async def handle_response(
    user: SteamUser, friends: bool = False, proxy: Optional[str] = None
):
    print_user(user)
    if friends and not user.private:
        async for friend in user.get_friends(proxy, raise_if_private=False):
            friends_divider()
            print_user(friend)


async def command(
    users: list[str],
    use_id: Annotated[
        bool, typer.Option(help="Uses /id to scrape the user down instead of /profile")
    ] = False,
    tor: bool = False,
    tor_proxy_port: int = 9050,
    tor_ctrl_port: int = 9051,
    proxy: Annotated[
        Optional[str],
        typer.Option(help="If tor is disabled use this proxy url instead"),
    ] = None,
    friends: Annotated[
        bool, typer.Option(help="Perform recursions over all the user's friends")
    ] = False,
):
    if tor:
        proxy = f"socks5://127.0.0.1:{tor_proxy_port}"
    async with launch_tor_optionally(tor, tor_proxy_port, tor_ctrl_port):
        for u in users:
            try:
                user = await scrape_user(u, use_id, proxy, raise_if_private=False)
                await handle_response(user, friends, proxy)
                await jitter()
            except ClientResponseError:
                print(f"{user} Not Found!")


def main():
    banner()
    app = EnhancedTyper(add_completion=False)
    app.async_command()(command)
    app()
