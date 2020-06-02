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
# @NaytSeyd tarafından portlanmıştır.
# @frknkrc44 tarafından düzenlenmiştir.
#

import os
import asyncio
import random

from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from requests import get
from telethon.tl import functions
from telethon.tl.types import InputMessagesFilterDocument

from sedenbot import bot, CMD_HELP, AUTO_PP, ASYNC_POOL, LOGS, me
from sedenbot.events import extract_args, sedenify

KEY_AUTOPP = 'autopic'

@sedenify(outgoing=True, pattern="^.autopp")
async def autopic(event):
    args = extract_args(event)
    if len(args) > 0 and args != 'disable':
        await event.edit('`Kullanım: .autopp / .autopp disable`')
        return

    if KEY_AUTOPP in ASYNC_POOL and len(args) < 1:
        await event.edit("`Görünüşe göre profil fotoğrafınız zaten otomatik olarak değişiyor.`")
        return

    if args == 'disable':
        if KEY_AUTOPP in ASYNC_POOL:
            ASYNC_POOL.remove(KEY_AUTOPP)
            await event.edit('`Profil fotoğrafınız artık otomatik olarak değişmeyecek.`')
            return
        else:
            await event.edit("`Görünüşe göre profil fotoğrafınız zaten otomatik olarak değişmiyor.`")
            return

    await event.edit("`Profil fotoğrafınız ayarlanıyor ...`")

    FONT_FILE_TO_USE = await get_font_file(event.client, "@FontDunyasi")

    downloaded_file_name = "eskipp.png"
    photo = "yenipp.png"
    if os.path.exists(downloaded_file_name):
        LOGS.info('[AUTOPP] Dosya zaten mevcut, indirme atlanıyor ...')
    else:
        if AUTO_PP and len(AUTO_PP) > 0:
            with open(downloaded_file_name, 'wb') as load:
                load.write(get(AUTO_PP).content)
        else:
            try:
                await event.client.download_profile_photo(me.id, 
                        downloaded_file_name, 
                        download_big=True)
            except:
                await event.edit('`Lütfen AUTO_PP değişkeninizi ayarlayın veya bir profil fotoğrafı koyun.`')
                return

    await event.edit("`Profil fotoğrafınız ayarlandı :)`")

    ASYNC_POOL.append(KEY_AUTOPP)

    while KEY_AUTOPP in ASYNC_POOL:
        current_time = datetime.now().strftime("%H:%M")
        img = Image.open(downloaded_file_name)
        drawn_text = ImageDraw.Draw(img)
        fnt = ImageFont.truetype(FONT_FILE_TO_USE, 70)
        size = drawn_text.multiline_textsize(current_time, font=fnt)
        drawn_text.text(((img.width - size[0]) / 2, (img.height - size[1])),
                       current_time, font=fnt, fill=(255, 255, 255))
        img.save(photo)
        file = await event.client.upload_file(photo)  # pylint:disable=E0602
        try:
            await event.client(functions.photos.UploadProfilePhotoRequest(  # pylint:disable=E0602
                file
            ))
            os.remove(photo)
            await asyncio.sleep(60)
        except:
            return

async def get_font_file(client, channel_id):
    # Önce yazı tipi mesajlarını al
    font_file_message_s = await client.get_messages(
        entity=channel_id,
        filter=InputMessagesFilterDocument,
        # Bu işlem çok fazla kullanıldığında
        # "FLOOD_WAIT" yapmaya neden olabilir
        limit=None
    )
    # Yazı tipi listesinden rastgele yazı tipi al
    # https://docs.python.org/3/library/random.html#random.choice
    font_file_message = random.choice(font_file_message_s)
    # Dosya yolunu indir ve geri dön
    return await client.download_media(font_file_message)

CMD_HELP.update({
    "autopp": 
    ".autopp <disable>\
    \nKullanım: Bu komut belirlediğiniz fotoğrafı profil resmi yapar \
    \nve bir saat ekler. Bu saat her dakika değişir. \
    \nAçmak için .autopp, kapatmak için .autopp disable yazın. \
    \nNOT: Küçük bir ihtimal bile olsa ban yeme riskiniz var. Bu yüzden dikkatli kullanın."
})
