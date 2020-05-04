# Copyright (C) 2020 TeamDerUntergang.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

import os
import lyricsgenius
import random

from userbot.events import register
from userbot import CMD_HELP, LOGS, GENIUS

@register(outgoing=True, pattern="^.lyrics(?: |$)(.*)")
async def lyrics(lyric):
    if r"-" in lyric.text:
        pass
    else:
        await lyric.edit("`Hata: lütfen <sanatçı> ve <şarkı> için bölücü olarak '-' kullanın`\n"
                         "Örnek: `Stabil - Reenkarne`")
        return

    if GENIUS is None:
        await lyric.edit(
            "`Lütfen Genius tokeni ayarlayınız. Teşekkürler!`")
    else:
        genius = lyricsgenius.Genius(GENIUS)
        try:
            args = lyric.text.split('.lyrics')[1].split('-')
            artist = args[0].strip(' ')
            song = args[1].strip(' ')
        except:
            await lyric.edit("`Lütfen sanatçı ve şarkı ismini veriniz`")
            return

    if len(args) < 1:
        await lyric.edit("`Lütfen sanatçı ve şarkı ismini veriniz`")
        return

    await lyric.edit(f"`{artist} - {song} için şarkı sözleri aranıyor...`")

    try:
        songs = genius.search_song(song, artist)
    except TypeError:
        songs = None

    if songs is None:
        await lyric.edit(f"Şarkı **{artist} - {song}** bulunamadı!")
        return
    if len(songs.lyrics) > 4096:
        await lyric.edit("`Şarkı sözleri çok uzun, görmek için dosyayı görüntüleyin.`")
        with open("lyrics.txt", "w+") as f:
            f.write(f"Arama sorgusu: \n{artist} - {song}\n\n{songs.lyrics}")
        await lyric.client.send_file(
            lyric.chat_id,
            "lyrics.txt",
            reply_to=lyric.id,
        )
        os.remove("lyrics.txt")
    else:
        await lyric.edit(f"**Arama sorgusu**: \n`{artist} - {song}`\n\n```{songs.lyrics}```")
    return

CMD_HELP.update({
    "lyrics":
    "Kullanım: .`lyrics <sanatçı adı> - <şarkı ismi>`\n"
    "NOT: ""-"" ayracı önemli!"
})
