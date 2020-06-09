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

import time
import requests

from collections import deque
from asyncio import sleep
from random import choice, getrandbits, randint
from re import sub
from telethon import events
from telethon.tl.types import ChannelParticipantsAdmins

from sedenbot.moduller.admin import get_user_from_event
from sedenbot import CMD_HELP, bot
from sedenbot.events import sedenify

@sedenify(outgoing=True, pattern="^.tagall$")
async def _(event):
    if event.fwd_from:
        return
    mentions = "@tag"
    chat = await event.get_input_chat()
    leng = 0
    async for x in bot.iter_participants(chat):
        if leng < 4092:
            mentions += f"[\u2063](tg://user?id={x.id})"
            leng += 1
    await event.reply(mentions)
    await event.delete()

@sedenify(outgoing=True, pattern="^.admin$")
async def _(event):
    if event.fwd_from:
        return
    mentions = "@admin"
    chat = await event.get_input_chat()
    async for x in bot.iter_participants(chat, filter=ChannelParticipantsAdmins):
        mentions += f"[\u2063](tg://user?id={x.id})"
    reply_message = None
    if event.reply_to_msg_id:
        reply_message = await event.get_reply_message()
        await reply_message.reply(mentions)
    else:
        await event.reply(mentions)
    await event.delete()

CMD_HELP.update({
    "tagall":
    ".tagall\
    \nKullanım: Bu komutu kullandığınızda sohbet içerisinde ki herkesi etiketler.\n\n.admin \
    \nKullanım: Bu komutu kullandığınızda sohbet içerisinde ki yöneticileri etiketler."
})
