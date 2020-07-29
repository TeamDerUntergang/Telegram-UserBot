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
from asyncio import run as runas
from requests import get
from os import path, remove

from telethon.errors.rpcerrorlist import PhoneNumberInvalidError
from . import BRAIN_CHECKER, BLACKLIST, LOGS, bot, CONSOLE_LOGGER_VERBOSE
from .moduller import ALL_MODULES

INVALID_PH = '\nHATA: Girilen telefon numarası geçersiz' \
             '\n  Ipucu: Ülke kodunu kullanarak numaranı gir' \
             '\n       Telefon numaranızı tekrar kontrol edin'

async def load_brain():
    if path.exists("learning-data-root.check"):
        remove("learning-data-root.check")
    URL = 'https://raw.githubusercontent.com/NaytSeyd/databasescape/master/learning-data-root.check'
    with open('learning-data-root.check', 'wb') as load:
        load.write(get(URL).content)
    DB = connect("learning-data-root.check")
    CURSOR = DB.cursor()
    CURSOR.execute("""SELECT * FROM BRAIN1""")
    ALL_ROWS = CURSOR.fetchall()
    for i in ALL_ROWS:
        BRAIN_CHECKER.append(i[0])
    DB.close()

async def load_bl():
    if path.exists("blacklist.check"):
        remove("blacklist.check")
    URL = 'https://raw.githubusercontent.com/NaytSeyd/databaseblacklist/master/blacklist.check'
    with open('blacklist.check', 'wb') as load:
        load.write(get(URL).content)    
    DB = connect("blacklist.check")
    CURSOR = DB.cursor()
    CURSOR.execute("SELECT * FROM RETARDS")
    ALL_ROWS = CURSOR.fetchall()
    for i in ALL_ROWS:
        BLACKLIST.append(i[0])
    DB.close()

runas(load_brain())
runas(load_bl())

try:
    bot.start()
except PhoneNumberInvalidError:
    print(INVALID_PH)
    exit(1)

for module_name in ALL_MODULES:
    try:
        LOGS.info(f'{module_name} yükleniyor ...')
        import_module("sedenbot.moduller." + module_name)
    except Exception as e:
        if CONSOLE_LOGGER_VERBOSE:
            raise e
        LOGS.warn(f"{module_name} modülü yüklenirken bir hata oluştu.")

LOGS.info("Botunuz çalışıyor! Herhangi bir sohbete .alive yazarak Test edin."
          " Yardıma ihtiyacınız varsa, Destek grubumuza gelin https://telegram.me/SedenUserBotSupport")
LOGS.info("Bot sürümünüz Seden v3.5 EOL")

bot.run_until_disconnected()
