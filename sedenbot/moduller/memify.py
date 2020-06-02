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
#

import os
import math
import time
import zipfile
import asyncio
import datetime
import requests

from PIL import Image
from io import BytesIO
from datetime import datetime
from hachoir.metadata import extractMetadata
from hachoir.parser import createParser
from collections import defaultdict

from telethon.tl.types import DocumentAttributeVideo
from telethon.errors.rpcerrorlist import StickersetInvalidError
from telethon.errors import MessageNotModifiedError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from telethon.tl.functions.messages import GetStickerSetRequest
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon import events
from telethon.tl.types import (
DocumentAttributeFilename,
DocumentAttributeSticker,
InputMediaUploadedDocument,
InputPeerNotifySettings,
InputStickerSetID,
InputStickerSetShortName,
MessageMediaPhoto
)

from sedenbot.moduller.upload_download import progress, humanbytes
from sedenbot import CMD_HELP, bot, TEMP_DOWNLOAD_DIRECTORY
from sedenbot.events import extract_args, sedenify

thumb_image_path = TEMP_DOWNLOAD_DIRECTORY + "/thumb_image.jpg"

@sedenify(outgoing=True, pattern="^.mem")
async def _(event):
    if event.fwd_from:
        return 
    if not event.reply_to_msg_id:
       await event.edit("`Kullanım: Bir fotoğrafa yanıt vererek .mem 'üst kısmın metni' ; 'alt kısmın metni'`")
       return
    reply_message = await event.get_reply_message() 
    if not reply_message.media:
       await event.edit("```Bir resme cevap verin.```")
       return
    chat = "@MemeAutobot"
    sender = reply_message.sender
    file_ext_ns_ion = "@sedenmemes.png"
    file = await bot.download_file(reply_message.media)
    uploaded_gif = None
    if reply_message.sender.bot:
       await event.edit("```Botlara cevap veremezsiniz.```")
       return
    else:
     await event.edit("`İşleniyor...`")
    
    async with bot.conversation("@MemeAutobot") as bot_conv:
          memeVar = extract_args(event)
          try:
            await silently_send_message(bot_conv, "/start")
            await asyncio.sleep(1)
            await silently_send_message(bot_conv, memeVar)
            await bot.send_file(chat, reply_message.media)
            response = await bot_conv.get_response()
          except YouBlockedUserError: 
              await event.reply("`Lütfen @MemeAutobot engelini kaldırın ve tekrar deneyin`")
              return
          if response.text.startswith("Forward"):
              await event.edit("`Gizlilik ayarları yüzenden alıntı yapamadım`")
          if "Okay..." in response.text:
            await event.edit("`Bu bir resim değil bu yüzden işlem iptal ediliyor...`")
            thumb = None
            if os.path.exists(thumb_image_path):
                thumb = thumb_image_path
            input_str = memeVar
            if not os.path.isdir(TMP_DOWNLOAD_DIRECTORY):
                os.makedirs(TMP_DOWNLOAD_DIRECTORY)
            if event.reply_to_msg_id:
                file_name = "sedenmemes.png"
                reply_message = await event.get_reply_message()
                to_download_directory = TMP_DOWNLOAD_DIRECTORY
                downloaded_file_name = os.path.join(to_download_directory, file_name)
                downloaded_file_name = await bot.download_media(
                    reply_message,
                    downloaded_file_name,
                    )
                if os.path.exists(downloaded_file_name):
                    await bot.send_file(
                        chat,
                        downloaded_file_name,
                        force_document=False,
                        supports_streaming=False,
                        allow_cache=False,
                        thumb=thumb,
                        )
                    os.remove(downloaded_file_name)
                else:
                    await event.edit("Dosya bulunamadı {}".format(input_str))
            response = await bot_conv.get_response()
            the_download_directory = TMP_DOWNLOAD_DIRECTORY
            files_name = "sedenmemes.webp"
            download_file_name = os.path.join(the_download_directory, files_name)
            await bot.download_media(
                response.media,
                download_file_name,
                )
            requires_file_name = (TMP_DOWNLOAD_DIRECTORY 
                + ('/' if TMP_DOWNLOAD_DIRECTORY[-1:] != '/' else '') 
                    + files_name)
            await bot.send_file(  # pylint:disable=E0602
                event.chat_id,
                requires_file_name,
                supports_streaming=False,
                caption="SedenBot: @NaytSeyd tarafından güçlendirildi.",
            )
            await event.delete()
            await bot.send_message(event.chat_id, "`İşlem başarılı!`")
          elif not is_message_image(reply_message):
            await event.edit("`Geçersiz mesaj türü. Lütfen doğru mesaj türünü seçin.`")
            return
          else: 
               await bot.send_file(event.chat_id, response.media)

def is_message_image(message):
    if message.media:
        if isinstance(message.media, MessageMediaPhoto):
            return True
        if message.media.document:
            if message.media.document.mime_type.split("/")[0] == "image":
                return True
        return False
    return False
    
async def silently_send_message(conv, text):
    await conv.send_message(text)
    response = await conv.get_response()
    await conv.mark_read(message=response)
    return response
    
CMD_HELP.update({
    'mem': ".mem \
\nKullanım: Bir fotoğrafa yanıt vererek .mem 'üst kısmın metni' ; 'alt kısmın metni' \
\nÖrnek: (Bir fotoğrafa yanıt vererek) .mem sedenbot ; en iyi bot"
})
