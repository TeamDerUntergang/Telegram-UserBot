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

"""Bir bölgenin hava durumunu gösterir."""

import json

from requests import get

from sedenbot import CMD_HELP, WEATHER_DEFCITY
from sedenbot.events import extract_args, sedenify
# ===== CONSTANT =====
if WEATHER_DEFCITY:
    DEFCITY = WEATHER_DEFCITY
else:
    DEFCITY = None
# ====================
@sedenify(outgoing=True, pattern="^.havadurumu")
async def get_wttr(weather):
    """ .havadurumu komutu bir bölgenin konumunu wttr üzerinden alır. """
    
    args = extract_args(weather)

    if len(args) < 1:
        CITY = DEFCITY
        if not CITY:
            await weather.edit(
                "`WEATHER_DEFCITY değişkeniyle bir şehri varsayılan olarak belirt, ya da komutu yazarken hangi şehrin hava durumunu istediğini de belirt!`"
            )
            return
    else:
        CITY = args
    
    if ',' in CITY:
        CITY = CITY[:CITY.find(',')].strip()
    
    try:
        req = get(f'http://wttr.in/{CITY}?mqT0', 
                  headers = {'User-Agent':'curl/7.66.0', 'Accept-Language':'tr'})
        data = req.text
        if '===' in data:
            raise Exception
        await weather.edit(f'```{data}```')
    except:
        await weather.edit('`Hava durumu bilgisi alınamadı.`')

CMD_HELP.update({
    "havadurumu":
    "Kullanım: .havadurumu şehir adı veya .havadurumu şehir adı\
    \nBir bölgenin hava durumunu verir."
})
