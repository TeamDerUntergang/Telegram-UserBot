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

""" UserBot başlangıç noktası """

from importlib import import_module
from sqlite3 import connect
from sys import argv

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from . import BRAIN_CHECKER, BLACKLIST, LOGS, bot
from .moduller import ALL_MODULES

DB = connect("learning-data-root.check")
CURSOR = DB.cursor()
CURSOR.execute("""SELECT * FROM BRAIN1""")
ALL_ROWS = CURSOR.fetchall()
INVALID_PH = '\nHATA: Girilen telefon numarası geçersiz' \
             '\n  Ipucu: Ülke kodunu kullanarak numaranı gir' \
             '\n       Telefon numaranızı tekrar kontrol edin'

for i in ALL_ROWS:
    BRAIN_CHECKER.append(i[0])
DB.close()
try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)
    
DB = connect("blacklist.check")
CURSOR = DB.cursor()
CURSOR.execute("""SELECT * FROM RETARDS""")
ALL_ROWS = CURSOR.fetchall()

for i in ALL_ROWS:
    BLACKLIST.append(i[0])
DB.close()

for module_name in ALL_MODULES:
    import_module("sedenbot.moduller." + module_name)

LOGS.info("Botunuz çalışıyor! Herhangi bir sohbete .alive yazarak Test edin."
          " Yardıma ihtiyacınız varsa, Destek grubumuza gelin t.me/SedenUserBotSupport")
LOGS.info("Bot sürümünüz Seden v3.0")

"""
if len(argv) not in (1, 3, 4):
    bot.disconnect()
else:
"""
bot.run_until_disconnected()
