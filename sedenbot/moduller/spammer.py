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

import time
import threading

from re import sub

from asyncio import wait, sleep

from sedenbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from sedenbot.events import extract_args, extract_args_arr, sedenify

@sedenify(outgoing=True, pattern="^.tspam")
async def tmeme(e):
    message = extract_args(e)
    if len(message) < 1:
        await e.edit("`Bir şeyler eksik/yanlış gibi görünüyor.`")
        return
    await e.delete()
    for letter in message.replace(' ',''):
        await e.respond(letter)
    if BOTLOG:
            await e.client.send_message(
                BOTLOG_CHATID,
                "#TSPAM \n\n"
                "TSpam başarıyla gerçekleştirildi"
                )

@sedenify(outgoing=True, pattern="^.spam")
async def bigspam(e):
    message = extract_args(e)
    if len(message) < 1:
        await e.edit("`Bir şeyler eksik/yanlış gibi görünüyor.`")
        return
    arr = message.split()
    if not arr[0].isdigit():
        await e.edit("`Bir şeyler eksik/yanlış gibi görünüyor.`")
        return
    await e.delete()
    counter = int(arr[0])
    spam_message = message.replace(arr[0],'').strip()
    for i in range(0, counter):
        await e.respond(spam_message)
    if BOTLOG:
         await e.client.send_message(
             BOTLOG_CHATID,
             "#BIGSPAM \n\n"
             "Bigspam başarıyla gerçekleştirildi"
            )

@sedenify(outgoing=True, pattern="^.picspam")
async def tiny_pic_spam(e):
    arr = extract_args_arr(e)
    if len(arr) < 2 or not arr[0].isdigit():
        await e.edit("`Bir şeyler eksik/yanlış gibi görünüyor.`")
        return
    await e.delete()
    counter = int(arr[0])
    link = arr[1]
    for i in range(0, counter):
        await e.client.send_file(e.chat_id, link)
    if BOTLOG:
        await e.client.send_message(
            BOTLOG_CHATID,
            "#PICSPAM \n\n"
            "PicSpam başarıyla gerçekleştirildi"
            )

@sedenify(outgoing=True, pattern="^.delayspam")
async def delayspammer(e):
    # Teşekkürler @ReversedPosix
    message = extract_args(e)
    arr = message.split()
    if len(arr) < 3 or not arr[0].isdigit() or not arr[1].isdigit():
        await e.edit("`Bir şeyler eksik/yanlış gibi görünüyor.`")
        return
    spam_delay = int(arr[0])
    counter = int(arr[1])
    spam_message = sub(f'{arr[0]}|{arr[1]}', '', message).strip()
    await e.delete()
    delaySpamEvent = threading.Event()
    for i in range(0, counter):
        await e.respond(spam_message)
        delaySpamEvent.wait(spam_delay)
    if BOTLOG:
        await e.client.send_message(
            BOTLOG_CHATID,
            "#DelaySPAM \n\n"
            "DelaySpam başarıyla gerçekleştirildi"
            )
                               
CMD_HELP.update({
    "spammer": ".tspam <metin>\
\nKullanım: Verilen mesajı tek tek göndererek spam yapar\
\n\n.spam <miktar> <metin>\
\nKullanım: Verilen miktarda spam gönderir\
\n\n.picspam <miktar> <link>\
\nKullanım: Verilen miktarda resimli spam gönderir\
\n\n.delayspam <gecikme> <miktar> <metin>\
\nKullanım: Verilen miktar ve verilen gecikme ile gecikmeli spam yapar\
\n\n\nNOT : Sorumluluk size aittir!!"
})
