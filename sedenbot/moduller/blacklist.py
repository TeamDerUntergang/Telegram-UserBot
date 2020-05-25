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

import io
import re
import asyncio

from telethon import events, utils
from telethon.tl import types, functions

from sedenbot import CMD_HELP, bot, LOGS
from sedenbot.events import extract_args, sedenify

from importlib import import_module

async def blacklist_init():
    try:
        global sql
        sql = import_module("sedenbot.moduller.sql_helper.blacklist_sql")
    except:
        sql = None
        LOGS.warn('Karaliste özelliği çalıştırılamıyor, SQL bağlantısı bulunamadı')

asyncio.run(blacklist_init())

@sedenify(incoming=True, disable_edited=True, disable_errors=True)
async def on_new_message(event):
    if not sql:
        return
    name = event.raw_text
    snips = sql.get_chat_blacklist(event.chat_id)
    for snip in snips:
        pattern = r"( |^|[^\w])" + re.escape(snip) + r"( |$|[^\w])"
        if re.search(pattern, name, flags=re.IGNORECASE):
            try:
                await event.delete()
            except Exception as e:
                await event.reply("I do not have DELETE permission in this chat")
                sql.rm_from_blacklist(event.chat_id, snip.lower())
            break
        pass

@sedenify(outgoing=True, pattern="^.addblacklist")
async def on_add_black_list(addbl):
    if not sql:
        await addbl.edit("`SQL dışı modda çalışıyorum, bunu gerçekleştiremem`")
        return
    text = extract_args(addbl)
    to_blacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))
    for trigger in to_blacklist:
        sql.add_to_blacklist(addbl.chat_id, trigger.lower())
    await addbl.edit("{} **adet kelime bu sohbet için karalisteye alındı.**".format(len(to_blacklist)))

@sedenify(outgoing=True, pattern="^.showblacklist")
async def on_view_blacklist(listbl):
    if not sql:
        await listbl.edit("`SQL dışı modda çalışıyorum, bunu gerçekleştiremem`")
        return
    all_blacklisted = sql.get_chat_blacklist(listbl.chat_id)
    OUT_STR = "**Bu grup için ayarlanan karaliste:**\n"
    if len(all_blacklisted) > 0:
        for trigger in all_blacklisted:
            OUT_STR += f"`{trigger}`\n"
    else:
        OUT_STR = "**Karalisteye eklenmiş kelime bulunamadı..** `.addblacklist` **komutu ile ekleyebilirsin.**"
    if len(OUT_STR) > 4096:
        with io.BytesIO(str.encode(OUT_STR)) as out_file:
            out_file.name = "blacklist.text"
            await listbl.client.send_file(
                listbl.chat_id,
                out_file,
                force_document=True,
                allow_cache=False,
                caption="**Bu grup için ayarlanan karaliste:**",
                reply_to=listbl
            )
            await listbl.delete()
    else:
        await listbl.edit(OUT_STR)

@sedenify(outgoing=True, pattern="^.rmblacklist")
async def on_delete_blacklist(rmbl):
    if not sql:
        await rmbl.edit("`SQL dışı modda çalışıyorum, bunu gerçekleştiremem`")
        return
    text = extract_args(rmbl)
    to_unblacklist = list(set(trigger.strip() for trigger in text.split("\n") if trigger.strip()))
    successful = 0
    for trigger in to_unblacklist:
        if sql.rm_from_blacklist(rmbl.chat_id, trigger.lower()):
            successful += 1
    await rmbl.edit(f"**Kelime karalisteden kaldırıldı.**")
    
CMD_HELP.update({
    "blacklist":
    ".showblacklist\
    \nKullanım: Bir sohbetteki etkin kara listeyi listeler.\
    \n\n.addblacklist <kelime>\
    \nKullanım: İletiyi 'kara liste anahtar kelimesine' kaydeder.\
    \n'Kara liste anahtar kelimesinden' bahsedildiğinde bot iletiyi siler.\
    \n\n.rmblacklist <kelime>\
    \nKullanım: Belirtilen kara listeyi durdurur.\
    \nBu arada bu işlemleri gerçekleştirmek için yönetici olmalı ve **Mesaj Silme** yetkiniz olmalı."
})
