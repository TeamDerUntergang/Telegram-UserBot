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
# @NaytSeyd tarafından portlanmıştır
#

import os

from telethon import events
from PIL import Image, ImageColor

from sedenbot import CMD_HELP, bot
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.color")
async def _(event):
    if event.fwd_from:
        return
    input_str = extract_args(event)
    message_id = event.message.id
    if event.reply_to_msg_id:
        message_id = event.reply_to_msg_id
    if input_str.startswith("#"):
        try:
            usercolor = ImageColor.getrgb(input_str)
        except Exception as e:
            await event.edit(str(e))
            return False
        else:
            im = Image.new(mode="RGB", size=(1280, 720), color=usercolor)
            im.save("sedencik.png", "PNG")
            input_str = input_str.replace("#", "#RENK_")
            await bot.send_file(
                event.chat_id,
                "sedencik.png",
                force_document=False,
                caption=input_str,
                reply_to=message_id
            )
            os.remove("sedencik.png")
            await event.delete()
    else:
        await event.edit("Belki burayı okuyarak bir şeyler öğrenebilirsin.. \
                         `.color <renk kodu>`")

CMD_HELP.update({
    'color': ".color <renk kodu> \
\nKullanım: Belirttiğniz renk kodunun çıktısını alın. \
\nÖrnek: .color #330066"
})
