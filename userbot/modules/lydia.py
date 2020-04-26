# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2020 TeamDerUntergang.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

"""
Bir grubu yönetmenize yardım eden UserBot modülüdür.
"""

import coffeehouse
import asyncio
from userbot import LYDIA_API_KEY
from userbot.events import register
from telethon import events

# SQL dışı mod
ACC_LYDIA = {}
SESSION_ID = {}

if LYDIA_API_KEY:
    api_key = LYDIA_API_KEY
    api_client = coffeehouse.API(api_key)

@register(outgoing=True, pattern="^.repcf$")
async def repcf(event):
    if event.fwd_from:
        return
    await event.edit("İşleniyor...")
    try:
        session = api_client.create_session()
        session_id = session.id
        reply = await event.get_reply_message()
        msg = reply.text
        text_rep = session.think_thought((session_id, msg))
        await event.edit("**Lydia diyor ki**: {0}".format(text_rep))
    except Exception as e:
        await event.edit(str(e))

@register(outgoing=True, pattern="^.addcf$")
async def addcf(event):
    if event.fwd_from:
        return
    await event.edit("Şu anlık SQL modunda çalışıyor...")
    await asyncio.sleep(4)
    await event.edit("İşleniyor...")
    reply_msg = await event.get_reply_message()
    if reply_msg:
        session = api_client.create_session()
        session_id = session.id
        ACC_LYDIA.update({str(event.chat_id) + " " + str(reply_msg.from_id): session})
        SESSION_ID.update({str(event.chat_id) + " " + str(reply_msg.from_id): session_id})
        await event.edit("Lydia şu kullanıcı için başarıyla etkinleştirildi: {} şu sohbette: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    else:
        await event.edit("Bir kullanıcıda Lydia'yı etkinleştirmek için onu yanıtlayın.")

@register(outgoing=True, pattern="^.remcf$")
async def remcf(event):
    if event.fwd_from:
        return
    await event.edit("Şu anlık SQL modunda çalışıyor...")
    await asyncio.sleep(4)
    await event.edit("İşleniyor...")
    reply_msg = await event.get_reply_message()
    try:
        del ACC_LYDIA[str(event.chat_id) + " " + str(reply_msg.from_id)]
        del SESSION_ID[str(event.chat_id) + " " + str(reply_msg.from_id)]
        await event.edit("Lydia şu kullanıcı için başarıyla devre dışı bırakıldı: {} şu sohbette: {}".format(str(reply_msg.from_id), str(event.chat_id)))
    except KeyError:
        await event.edit("Bu kullanıcıda Lydia aktif değil.")

@register(incoming=True, disable_edited=True)
async def user(event):
    user_text = event.text
    try:
        session = ACC_LYDIA[str(event.chat_id) + " " + str(event.from_id)]
        session_id = SESSION_ID[str(event.chat_id) + " " + str(event.from_id)]
        msg = event.text
        async with event.client.action(event.chat_id, "typing"):
            text_rep = session.think_thought((session_id, msg))
            wait_time = 0
            for i in range(len(text_rep)):
                wait_time = wait_time + 0.1
            await asyncio.sleep(wait_time)
            await event.reply(text_rep)
    except KeyError:
        return

    
"""CMD_HELP.update({
    "lydia":
    ".addcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetini etkinleştirir. \
\n\n.remcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetini devre dışı bırakır. \
\n\n.repcf <kullanıcı adı/yanıtlayarak>\
\nKullanım: Lydia'nın otomatik sohbetiini belli bir kişi için etkinleştirir."
})
"""
