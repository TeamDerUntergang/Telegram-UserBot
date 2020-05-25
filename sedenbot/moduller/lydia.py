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

import asyncio

from coffeehouse.lydia import LydiaAI
from coffeehouse.api import API

from sedenbot.events import extract_args, sedenify
from sedenbot import CMD_HELP, LOGS, LYDIA_API_KEY

async def lydia_init():
    try:
        from sedenbot.moduller.sql_helper.lydia_sql import get_s, get_all_s, add_s, remove_s
    except:
        LOGS.warn("Lydia veritabanı bağlantısı başarısız oldu")

asyncio.run(lydia_init())

# SQL dışı mod
ACC_LYDIA = {}

if LYDIA_API_KEY:
    api_key = LYDIA_API_KEY
    api_client = API(api_key)
    lydia = LydiaAI(api_client)

@sedenify(outgoing=True, pattern="^.repcf")
async def repcf(event):
    if event.fwd_from:
        return
    await event.edit("İşleniyor...")
    try:
        session = lydia.create_session()
        reply = await event.get_reply_message()
        msg = reply.text
        text_rep = session.think_thought(msg)
        await event.edit("**Lydia diyor ki**: {0}".format(text_rep))
    except Exception as e:
        await event.edit(str(e))

@sedenify(outgoing=True, pattern="^.addcf")
async def addcf(event):
    if event.fwd_from:
        return
    await event.edit("Şimdilik SQL dışı modda çalışıyor...")
    await asyncio.sleep(3)
    await event.edit("İşleniyor...")
    reply_msg = await event.get_reply_message()
    if reply_msg:
        session = lydia.create_session()
        session_id = session.id
        if not reply_msg.from_id:
            return await event.edit("Geçersiz kullanıcı türü.")
        ACC_LYDIA.update({(event.chat_id & reply_msg.from_id): session})
        await event.edit("Lydia, {} kullanıcısı için {} sohbetinde başarıyla etkinleştirildi!".format(str(reply_msg.from_id), str(event.chat_id)))
    else:
        await event.edit("Lydia AI'yı etkinleştirmek için bir kullanıcıyı yanıtlayın")

@sedenify(outgoing=True, pattern="^.remcf")
async def remcf(event):
    if event.fwd_from:
        return
    await event.edit("Şimdilik SQL dışı modda çalışıyor...")
    await asyncio.sleep(3)
    await event.edit("İşleniyor...")
    reply_msg = await event.get_reply_message()
    try:
        del ACC_LYDIA[event.chat_id & reply_msg.from_id]
        await event.edit("Lydia, {} kullanıcısı için {} sohbetinde başarıyla devre dışı bırakıldı!".format(str(reply_msg.from_id), str(event.chat_id)))
    except Exception:
        await event.edit("Bu kullanıcıda Lydia aktif değil.")

@sedenify(incoming=True, disable_edited=True)
async def user(event):
    user_text = event.text
    try:
        session = ACC_LYDIA[event.chat_id & event.from_id]
        msg = event.text
        async with event.client.action(event.chat_id, "typing"):
            text_rep = session.think_thought(msg)
            wait_time = 0
            for i in range(len(text_rep)):
                wait_time = wait_time + 0.1
            await asyncio.sleep(wait_time)
            await event.reply(text_rep)
    except (KeyError, TypeError):
        return

CMD_HELP.update({
    "lydia":
    ".addcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetini etkinleştirir. \
\n\n.remcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetini devre dışı bırakır. \
\n\n.repcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetiini belli bir kişi için etkinleştirir."
})
