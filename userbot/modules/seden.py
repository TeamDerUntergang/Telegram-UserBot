# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2020 TeamDerUntergang.
# s
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

""" UserBot yardım komutu """

from userbot import CMD_HELP
from userbot.events import register


@register(outgoing=True, pattern="^.seden(?: |$)(.*)")
async def seden(event):
    """ .seden komutu için """
    args = event.pattern_match.group(1).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Lütfen bir Seden modülü adı belirtin.")
    else:
        await event.edit("Lütfen hangi Seden modülü için yardım istediğinizi belirtin !!\
            \nKullanım: .seden <modül adı>")
        string = ""
        for i in CMD_HELP:
            string += "`" + str(i)
            string += "`\n"
        await event.reply(string)
