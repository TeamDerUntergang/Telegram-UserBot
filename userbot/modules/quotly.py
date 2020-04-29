# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2020 TeamDerUntergang.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.

# @NaytSeyd tarafından portlanmıştır.

import datetime
from telethon import events
from telethon.errors.rpcerrorlist import YouBlockedUserError
from telethon.tl.functions.account import UpdateNotifySettingsRequest
from userbot import bot, CMD_HELP
from userbot.events import register

@register(outgoing=True, pattern="^.q(?: |$)(.*)")
async def _(event):
    if event.fwd_from:
        return 
    if not event.reply_to_msg_id:
       await event.edit("`Herhangi bir kullanıcı mesajına cevap verin.`")
       return
    reply_message = await event.get_reply_message() 
    if not reply_message.text:
       await event.edit("`Mesaja cevap verin.`")
       return
    chat = "@QuotLyBot"
    sender = reply_message.sender
    if reply_message.sender.bot:
       await event.edit("`Botlara cevap veremezsiniz.`")
       return
    await event.edit("`Alıntı yapılıyor...`")

    async with bot.conversation(chat, exclusive=False, replies_are_responses=True) as conv:
          response = None
          try:
              msg = await reply_message.forward_to(chat)
              response = await conv.get_response(message=msg, timeout=5)
          except YouBlockedUserError: 
              await event.edit("`Lütfen @QuotLyBot engelini kaldırın ve tekrar deneyin`")
              return
          except Exception as e:
              print(e.__class__)

          if not response:
              await event.edit("`Botdan cevap alamadım!`")
          elif response.text.startswith("Merhaba!"):
             await event.edit("`Gizlilik ayarları yüzenden alıntı yapamadım`")
          else: 
             await event.delete()
             await response.forward_to(event.chat_id)
          await conv.mark_read()
          await conv.cancel_all()

CMD_HELP.update({
    "quotly": 
    ".q \
    \n**Kullanım**: Metninizi çıkartmaya dönüştürün.\n"
})
