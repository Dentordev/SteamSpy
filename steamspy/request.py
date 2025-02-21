from aiohttp import request
from aiohttp.typedefs import StrOrURL
from aiohttp_socks import ProxyConnector

import re

from .user_agents import random_user_agent
from typing import Optional, Union
from yarl import URL
import aiofiles

class PrivateUser(Exception):
    """Raised if a user's profile is made private"""

    pass


# The goal is to be a minimalist. We would go out of our way and just grab an html-parser
# But it's not nessesary since we have the fastest possible methods around
# However there's probably smarter ways to harvest this info...

Name_re = re.compile(r"<span class=\"actual_persona_name\">([^<]+)</span>")
Friends_re = re.compile(r"https://steamcommunity.com/(?:profiles|id)/(?:[^\"])+")
NotOnline_re = re.compile(
    r"<div class=\"profile_in_game_header\">Currently Offline</div>"
)
Private_re = re.compile(
    r"<div class\=\"profile_private_info\">\n(?:[^\w]+)This profile is private\."
)
PFP_re = re.compile(r"avatars\.fastly\.steamstatic\.com/\w+\_full\.jpg")


def fix_shit_encodings(html: str):
    data = str()
    for h in range(len(html)):
        if ord(html[h]) >= 256:
            continue
        data += html[h]
    return data.encode("utf-8")


class SteamUser:
    def __init__(
        self,
        id: Union[int, str],
        use_id: bool,
        url: str,
        html: str,
        raise_if_private: bool = False,
    ):
        self.name = Name_re.search(html).group(1)
        self.online = NotOnline_re.search(html) is None
        self.private = Private_re.search(html) is not None
        self.url = url
        self.id = id
        self.use_id = use_id
        self.profile_pic = "https://" + PFP_re.search(html).group()
        if raise_if_private:
            self.raise_if_private()

    def raise_if_private(self):
        """raised if the user's account is labeled as private"""
        if self.private:
            raise PrivateUser(f"{self.name} is a private account")

    async def download_image(self, filename:str , proxy:Optional[str]):
        data = await get_data( self.profile_pic, proxy)
        async with aiofiles.open(filename, "wb") as wb:
            await wb.write(data)

    async def get_friends(
        self, proxy: Optional[str] = None, raise_if_private: bool = False
    ):
        """Obtains a list of friends and scrapes their steam pages as well"""
        async for friend in harvest_friends(self.id, self.use_id, proxy=proxy):
            yield await friend.resolve_info(proxy, raise_if_private=raise_if_private)


async def get_data(url: StrOrURL, proxy: Optional[str] = None):
    """Downloads data from request as bytes"""
    if proxy is not None:
        # Connector has problems if I leave it inside the connector
        async with ProxyConnector.from_url(proxy, rdns=True) as connector:
            async with request(
                "GET",
                url,
                connector=connector,
                headers={"User-Agent": random_user_agent()},
                raise_for_status=True,
            ) as resp:
                return await resp.content.read()
    else:
        async with request(
            "GET",
            url,
            headers={"User-Agent": random_user_agent()},
            raise_for_status=True,
        ) as resp:
            return await resp.content.text()

# TODO: Make "get" code smaller and more condensed
async def get(url: StrOrURL, proxy: Optional[str] = None):
    if proxy is not None:
        # Connector has problems if I leave it inside the connector
        async with ProxyConnector.from_url(proxy, rdns=True) as connector:
            async with request(
                "GET",
                url,
                connector=connector,
                headers={"User-Agent": random_user_agent()},
                raise_for_status=True,
            ) as resp:
                return await resp.text()
    else:
        async with request(
            "GET",
            url,
            headers={"User-Agent": random_user_agent()},
            raise_for_status=True,
        ) as resp:
            return await resp.text()


async def scrape_user(
    user: Union[str, int],
    use_id: bool = False,
    proxy: Optional[str] = None,
    raise_if_private: bool = True,
):
    """Scrapes for user information"""
    url = (
        URL("https://steamcommunity.com") / ("id" if use_id else "profiles") / f"{user}"
    )
    text = await get(url, proxy)
    return SteamUser(
        id=user,
        url=str(url),
        use_id=use_id,
        html=text,
        raise_if_private=raise_if_private,
    )


scrapeUser = scrape_user


class SteamFriend:
    def __init__(self, steam_url: str):
        self.url = steam_url

    async def resolve_info(
        self, proxy: Optional[str] = None, raise_if_private: bool = False
    ):
        """Resolves information about the steam user's friend"""
        text = await get(self.url, proxy)
        user = SteamUser(
            id=URL(self.url).raw_parts[-1],
            url=self.url,
            use_id=False,
            html=text,
            raise_if_private=raise_if_private,
        )
        if raise_if_private:
            user.raise_if_private()
        return user


async def harvest_friends(
    user: Union[str, int], use_id: bool = False, proxy: Optional[str] = None
):
    text = await get(
        URL("https://steamcommunity.com")
        / ("id" if use_id else "profiles")
        / f"{user}"
        / "friends",
        proxy,
    )

    for f in Friends_re.finditer(text):
        yield SteamFriend(f.group())


harvestFriends = harvest_friends
