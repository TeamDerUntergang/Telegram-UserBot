# Copyright (C) 2020 TeamDerUntergang.
#
# SedenUserBot is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# SedenUserBot is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

from asyncio import sleep
from json import loads
from json.decoder import JSONDecodeError
from os import environ
from sys import setrecursionlimit

import spotify_token as st
from requests import get
from telethon.errors import AboutTooLongError
from telethon.tl.functions.account import UpdateProfileRequest

from sedenbot import (BIO_PREFIX, BOTLOG, BOTLOG_CHATID, CMD_HELP, DEFAULT_BIO,
                     SPOTIFY_PASS, SPOTIFY_USERNAME, bot)
from sedenbot.events import sedenify

# =================== CONSTANT ===================
SPO_BIO_ENABLED = "`Spotify oynatılan müziği biyografiye ekleme etkinleştirildi.`"
SPO_BIO_DISABLED = "`Spotify oynatılan müziği biyografiye ekleme devre dışı bırakıldı. "
SPO_BIO_DISABLED += "Biyografi varsayılan ayara geri döndürüldü.`"
SPO_BIO_RUNNING = "`Spotify oynatılan müziği biyografiye ekleme zaten çalışıyor.`"
ERROR_MSG = "`Spotify modülü durduruldu, beklenmedik bir hata aldı.`"

USERNAME = SPOTIFY_USERNAME
PASSWORD = SPOTIFY_PASS

ARTIST = 0
SONG = 0

BIOPREFIX = BIO_PREFIX

SPOTIFYCHECK = False
RUNNING = False
OLDEXCEPT = False
PARSE = False
# ================================================
async def get_spotify_token():
    sptoken = st.start_session(USERNAME, PASSWORD)
    access_token = sptoken[0]
    environ["spftoken"] = access_token

async def update_spotify_info():
    global ARTIST
    global SONG
    global PARSE
    global SPOTIFYCHECK
    global RUNNING
    global OLDEXCEPT
    oldartist = ""
    oldsong = ""
    while SPOTIFYCHECK:
        try:
            RUNNING = True
            spftoken = environ.get("spftoken", None)
            hed = {'Authorization': 'Bearer ' + spftoken}
            url = 'https://api.spotify.com/v1/me/player/currently-playing'
            response = get(url, headers=hed)
            data = loads(response.content)
            artist = data['item']['album']['artists'][0]['name']
            song = data['item']['name']
            OLDEXCEPT = False
            oldsong = environ.get("oldsong", None)
            if song != oldsong and artist != oldartist:
                oldartist = artist
                environ["oldsong"] = song
                spobio = BIOPREFIX + " 🎧: " + artist + " - " + song
                try:
                    await bot(UpdateProfileRequest(about=spobio))
                except AboutTooLongError:
                    short_bio = "🎧: " + song
                    await bot(UpdateProfileRequest(about=short_bio))
                environ["errorcheck"] = "0"
        except KeyError:
            errorcheck = environ.get("errorcheck", None)
            if errorcheck == 0:
                await update_token()
            elif errorcheck == 1:
                SPOTIFYCHECK = False
                await bot(UpdateProfileRequest(about=DEFAULT_BIO))
                print(ERROR_MSG)
                if BOTLOG:
                    await bot.send_message(BOTLOG_CHATID, ERROR_MSG)
        except JSONDecodeError:
            OLDEXCEPT = True
            await sleep(6)
            await bot(UpdateProfileRequest(about=DEFAULT_BIO))
        except TypeError:
            await dirtyfix()
        SPOTIFYCHECK = False
        await sleep(2)
        await dirtyfix()
    RUNNING = False

async def update_token():
    sptoken = st.start_session(USERNAME, PASSWORD)
    access_token = sptoken[0]
    environ["spftoken"] = access_token
    environ["errorcheck"] = "1"
    await update_spotify_info()

async def dirtyfix():
    global SPOTIFYCHECK
    SPOTIFYCHECK = True
    await sleep(4)
    await update_spotify_info()

@sedenify(outgoing=True, pattern="^.enablespotify$")
async def set_biostgraph(setstbio):
    setrecursionlimit(700000)
    if not SPOTIFYCHECK:
        environ["errorcheck"] = "0"
        await setstbio.edit(SPO_BIO_ENABLED)
        await get_spotify_token()
        await dirtyfix()
    else:
        await setstbio.edit(SPO_BIO_RUNNING)

@sedenify(outgoing=True, pattern="^.disablespotify$")
async def set_biodgraph(setdbio):
    global SPOTIFYCHECK
    global RUNNING
    SPOTIFYCHECK = False
    RUNNING = False
    await bot(UpdateProfileRequest(about=DEFAULT_BIO))
    await setdbio.edit(SPO_BIO_DISABLED)

CMD_HELP.update({
    "spotify":
    ".enablespotify \
    \nKullanım: Spotify biyografi güncellemesini etkinleştir. \
    \n.disablespotify \
    \nKullanım: Spotify biyografi güncellemesini (açıksa) devre dışı bırakır."
})
