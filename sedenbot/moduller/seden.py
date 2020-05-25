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

""" UserBot yardım komutu """

from sedenbot import CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.seden")
async def seden(event):
    """ .seden komutu için """
    args = extract_args(event).lower()
    if args:
        if args in CMD_HELP:
            await event.edit(str(CMD_HELP[args]))
        else:
            await event.edit("Lütfen bir Seden modülü adı belirtin.")
    else:
        await event.edit("Lütfen hangi Seden modülü için yardım istediğinizi belirtin !!\
            \nKullanım: .seden <modül adı>")
        string = "**[Seden UserBot](https://telegram.dog/SedenUserBot) Yüklü Modüller:**\n↓  ↓  ↓  ↓\n"
        for i in CMD_HELP:
            string += "🔸 - `" + str(i)
            string += "` \n"
        await event.reply(string)
