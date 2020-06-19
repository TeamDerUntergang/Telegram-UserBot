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

""" UserBot hazırlanışı. """
from sys import version_info
if version_info[0] < 3 or version_info[1] < 8:
    LOGS.info("En az python 3.8 sürümüne sahip olmanız gerekir. "
              "Birden fazla özellik buna bağlıdır. Bot kapatılıyor.")
    quit(1)

from os import environ
from re import compile as recomp
from re import search as resr

from logging import basicConfig, getLogger, INFO, DEBUG
from distutils.util import strtobool as sb
from math import ceil

from pylast import LastFMNetwork, md5
from dotenv import load_dotenv
from telethon.sync import TelegramClient, custom, events
from telethon.sessions import StringSession
load_dotenv("config.env")

# Bot günlükleri kurulumu:
CONSOLE_LOGGER_VERBOSE = sb(environ.get("CONSOLE_LOGGER_VERBOSE", "False"))

ASYNC_POOL = []
VALID_PROXY_URL = []
basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=DEBUG if CONSOLE_LOGGER_VERBOSE else INFO,
)
LOGS = getLogger(__name__)

# Yapılandırmanın önceden kullanılan değişkeni kullanarak düzenlenip düzenlenmediğini kontrol edin.
# Temel olarak, yapılandırma dosyası için kontrol.
CONFIG_CHECK = environ.get(
    "___________LUTFEN_______BU_____SATIRI_____SILIN__________", None)

if CONFIG_CHECK:
    LOGS.info(
        "Lütfen ilk hashtag'de belirtilen satırı config.env dosyasından kaldırın"
    )
    quit(1)

# Telegram API KEY ve HASH
API_KEY = environ.get("API_KEY", None)
API_HASH = environ.get("API_HASH", None)

# UserBot Session String
STRING_SESSION = environ.get("STRING_SESSION", None)

# Kanal / Grup ID yapılandırmasını günlüğe kaydetme.
BOTLOG_CHATID = environ.get("BOTLOG_CHATID", None)
BOTLOG_CHATID = int(BOTLOG_CHATID) if BOTLOG_CHATID and resr('^-?\d+$', BOTLOG_CHATID) else None

# Alive Mesajını değiştirme.
ALIVE_MESAJI = environ.get("ALIVE_MESAJI", "Merhaba Seden! Seni Seviyorum ❤️")

# UserBot günlükleme özelliği.
BOTLOG = sb(environ.get("BOTLOG", "False"))
LOGSPAMMER = sb(environ.get("LOGSPAMMER", "False"))

# Hey! Bu bir bot. Endişelenme ;)
PM_AUTO_BAN = sb(environ.get("PM_AUTO_BAN", "False"))

# Güncelleyici için Heroku hesap bilgileri.
HEROKU_APPNAME = environ.get("HEROKU_APPNAME", None)
HEROKU_APIKEY = environ.get("HEROKU_APIKEY", None)

# Güncelleyici için özel (fork) repo linki.
UPSTREAM_REPO_URL = environ.get(
    "UPSTREAM_REPO_URL",
    "https://github.com/TeamDerUntergang/Telegram-UserBot.git")

# Ayrıntılı konsol günlügü
CONSOLE_LOGGER_VERBOSE = sb(environ.get("CONSOLE_LOGGER_VERBOSE", "False"))

# SQL Veritabanı
DB_URI = environ.get("DATABASE_URL", None)

# OCR API key
OCR_SPACE_API_KEY = environ.get("OCR_SPACE_API_KEY", None)

# remove.bg API key
REM_BG_API_KEY = environ.get("REM_BG_API_KEY", None)

# AUTO PP
AUTO_PP = environ.get("AUTO_PP", None)

# Chrome sürücüsü ve Google Chrome dosyaları
CHROME_DRIVER = environ.get("CHROME_DRIVER", None)

# Hava durumu varsayılan şehir
WEATHER_DEFCITY = environ.get("WEATHER_DEFCITY", None)

# Lydia API
LYDIA_API_KEY = environ.get("LYDIA_API_KEY", None)

# Anti Spambot
ANTI_SPAMBOT = sb(environ.get("ANTI_SPAMBOT", "False"))
ANTI_SPAMBOT_SHOUT = sb(environ.get("ANTI_SPAMBOT_SHOUT", "False"))

# Youtube API key
YOUTUBE_API_KEY = environ.get("YOUTUBE_API_KEY", None)

# Saat & Tarih - Ülke ve Saat Dilimi
COUNTRY = str(environ.get("COUNTRY", ""))
TZ_NUMBER = int(environ.get("TZ_NUMBER", 3))

# Temiz Karşılama
CLEAN_WELCOME = sb(environ.get("CLEAN_WELCOME", "True"))

# Last.fm modülü
BIO_PREFIX = environ.get("BIO_PREFIX", None)
DEFAULT_BIO = environ.get("DEFAULT_BIO", None)

LASTFM_API = environ.get("LASTFM_API", None)
LASTFM_SECRET = environ.get("LASTFM_SECRET", None)
LASTFM_USERNAME = environ.get("LASTFM_USERNAME", None)
LASTFM_PASSWORD_PLAIN = environ.get("LASTFM_PASSWORD", None)
LASTFM_PASS = md5(LASTFM_PASSWORD_PLAIN)
if LASTFM_API and LASTFM_SECRET and LASTFM_USERNAME and LASTFM_PASS:
    lastfm = LastFMNetwork(api_key=LASTFM_API,
                           api_secret=LASTFM_SECRET,
                           username=LASTFM_USERNAME,
                           password_hash=LASTFM_PASS)
else:
    lastfm = None

# Google Drive Modülü
G_DRIVE_CLIENT_ID = environ.get("G_DRIVE_CLIENT_ID", None)
G_DRIVE_CLIENT_SECRET = environ.get("G_DRIVE_CLIENT_SECRET", None)
G_DRIVE_AUTH_TOKEN_DATA = environ.get("G_DRIVE_AUTH_TOKEN_DATA", None)
GDRIVE_FOLDER_ID = environ.get("GDRIVE_FOLDER_ID", None)
TEMP_DOWNLOAD_DIRECTORY = environ.get("TMP_DOWNLOAD_DIRECTORY",
                                         "./downloads")

# Inline bot çalışması için
BOT_TOKEN = environ.get("BOT_TOKEN", None)
BOT_USERNAME = environ.get("BOT_USERNAME", None)

# Genius modülünün çalışması için buradan değeri alın https://genius.com/developers her ikisi de aynı değerlere sahiptir
GENIUS_API_TOKEN = environ.get("GENIUS_API_TOKEN", None)

# Ayarlanabilir PM izin verilmedi mesajı
PM_UNAPPROVED = environ.get("PM_UNAPPROVED", None)

CMD_HELP = {}

"""

"""

# 'bot' değişkeni
bot = TelegramClient(StringSession(STRING_SESSION if STRING_SESSION else "sedenbot"), API_KEY, API_HASH)

async def check_botlog_chatid():
    if not BOTLOG_CHATID and LOGSPAMMER:
        LOGS.info(
            "HATA: LOGSPAMMER çalışması için BOTLOG_CHATID değişkenini ayarlamanız gerekir. "
            "Bot kapatılıyor..."
            )
        quit(1)

    elif not BOTLOG_CHATID and BOTLOG:
        LOGS.info(
            "Günlüğe kaydetme özelliğinin çalışması için BOTLOG_CHATID değişkenini ayarlamanız gerekir."
            "Bot Kapatılıyor..."
            )
        quit(1)

    elif not BOTLOG or not LOGSPAMMER:
        return

    entity = await bot.get_entity(BOTLOG_CHATID)
    if entity.default_banned_rights.send_messages:
        LOGS.info(
            "Hesabınızın BOTLOG_CHATID grubuna mesaj gönderme yetkisi yoktur. "
            "Grup ID'sini doğru yazıp yazmadığınızı kontrol edin.")
        quit(1)

with bot:
    me = bot.get_me()
    uid = me.id
    try:
        bot.loop.run_until_complete(check_botlog_chatid())
    except:
        LOGS.info(
            "HATA: Girilen BOTLOG_CHATID değişkeni geçerli değildir. "
            "Lütfen girdiğiniz değeri kontrol edin. "
            "Bot kapatılıyor.."
        )
        quit(1)

    try:
        if not BOT_TOKEN:
            raise Exception()

        tgbot = TelegramClient(
            "TG_BOT_TOKEN",
            api_id=API_KEY,
            api_hash=API_HASH
        ).start(bot_token=BOT_TOKEN)

        dugmeler = CMD_HELP

        def paginate_help(page_number, loaded_modules, prefix):
            number_of_rows = 5
            number_of_cols = 2
            helpable_modules = []
            for p in loaded_modules:
                if not p.startswith("_"):
                    helpable_modules.append(p)
            helpable_modules = sorted(helpable_modules)
            modules = [custom.Button.inline(
                "{} {}".format("🔸", x),
                data="ub_modul_{}".format(x))
                for x in helpable_modules]
            pairs = list(zip(modules[::number_of_cols], modules[1::number_of_cols]))
            if len(modules) % number_of_cols == 1:
                pairs.append((modules[-1],))
            max_num_pages = ceil(len(pairs) / number_of_rows)
            modulo_page = page_number % max_num_pages
            if len(pairs) > number_of_rows:
                pairs = pairs[modulo_page * number_of_rows:number_of_rows * (modulo_page + 1)] + \
                [
                    (custom.Button.inline("⬅️ Geri", data=f"{prefix}_prev({modulo_page})"),
                     custom.Button.inline("İleri ➡️", data=f"{prefix}_next({modulo_page})"))
                ]
            return pairs

        @tgbot.on(events.NewMessage(pattern='/start'))
        async def handler(event):
            if not event.message.from_id == uid:
                await event.reply(f'`Merhaba ben` @SedenUserBot`! Ben sahibime (`@{me.username}`) yardımcı olmak için varım, yaani sana yardımcı olamam :/ Ama sen de bir Seden açabilirsin; Kanala bak` @SedenUserBot')
            else:
                await event.reply(f'`Senin için çalışıyorum :) Seni seviyorum. ❤️`')

        @tgbot.on(events.InlineQuery)  # pylint:disable=E0602
        async def inline_handler(event):
            builder = event.builder
            result = None
            query = event.text
            if event.query.user_id == uid and query.startswith("@SedenUserBot"):
                buttons = paginate_help(0, dugmeler, "helpme")
                result = builder.article(
                    f"Lütfen Sadece .yardım Komutu İle Kullanın",
                    text="{}\nYüklenen Modül Sayısı: {}".format(
                        "Merhaba! Ben @SedenUserBot kullanıyorum!\n\nhttps://github.com/TeamDerUntergang/Telegram-UserBot", len(dugmeler)),
                    buttons=buttons,
                    link_preview=False
                )
            elif query.startswith("tb_btn"):
                result = builder.article(
                    "© @SedenUserBot",
                    text=f"@SedenUserBot ile güçlendirildi",
                    buttons=[],
                    link_preview=True
                )
            else:
                result = builder.article(
                    "© @SedenUserBot",
                    text="""@SedenUserBot'u kullanmayı deneyin!
Hesabınızı bot'a çevirebilirsiniz ve bunları kullanabilirsiniz. Unutmayın, siz başkasının botunu yönetemezsiniz! Alttaki GitHub adresinden tüm kurulum detayları anlatılmıştır.""",
                    buttons=[
                        [custom.Button.url("Kanala Katıl", "https://t.me/SedenUserBot"), custom.custom.Button.url(
                            "Gruba Katıl", "https://t.me/SedenUserBotSupport")],
                        [custom.Button.url(
                            "GitHub", "https://github.com/TeamDerUntergang/Telegram-UserBot")]
                    ],
                    link_preview=False
                )
            await event.answer([result] if result else None)

        @tgbot.on(events.callbackquery.CallbackQuery(  # pylint:disable=E0602
            data=recomp(b"helpme_next\((.+?)\)")
        ))
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                current_page_number = int(
                    event.data_match.group(1).decode("UTF-8"))
                buttons = paginate_help(
                    current_page_number + 1, dugmeler, "helpme")
                # https://t.me/TelethonChat/115200
                await event.edit(buttons=buttons)
            else:
                reply_pop_up_alert = "Lütfen kendine bir @SedenUserBot aç, benim mesajlarımı düzenlemeye çalışma!"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)

        @tgbot.on(events.callbackquery.CallbackQuery(  # pylint:disable=E0602
            data=recomp(b"helpme_prev\((.+?)\)")
        ))
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                current_page_number = int(
                    event.data_match.group(1).decode("UTF-8"))
                buttons = paginate_help(
                    current_page_number - 1,
                    dugmeler,  # pylint:disable=E0602
                    "helpme"
                )
                # https://t.me/TelethonChat/115200
                await event.edit(buttons=buttons)
            else:
                reply_pop_up_alert = "Lütfen kendine bir @SedenUserBot aç, benim mesajlarımı düzenlemeye çalışma!"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)

        @tgbot.on(events.callbackquery.CallbackQuery(  # pylint:disable=E0602
            data=recomp(b"ub_modul_(.*)")
        ))
        async def on_plug_in_callback_query_handler(event):
            if event.query.user_id == uid:  # pylint:disable=E0602
                modul_name = event.data_match.group(1).decode("UTF-8")

                cmdhel = str(CMD_HELP[modul_name])
                if len(cmdhel) > 90:
                    help_string = str(CMD_HELP[modul_name])[
                        :90] + "\n\nDevamı için .seden " + modul_name + " yazın."
                else:
                    help_string = str(CMD_HELP[modul_name])

                reply_pop_up_alert = help_string if help_string  else \
                    "{} modülü için herhangi bir döküman yazılmamış.".format(
                        modul_name)
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)
            else:
                reply_pop_up_alert = "Lütfen kendine bir @SedenUserBot aç, benim mesajlarımı düzenlemeye çalışma!"
                await event.answer(reply_pop_up_alert, cache_time=0, alert=True)
    except:
        LOGS.info(
            "Botunuzda inline desteği devre dışı bırakıldı. "
            "Etkinleştirmek için bir bot token tanımlayın ve botunuzda inline modunu etkinleştirin. "
            "Eğer bunun dışında bir sorun olduğunu düşünüyorsanız bize ulaşın."
        )


# Küresel Değişkenler
COUNT_MSG = 0
USERS = {}
BRAIN_CHECKER = []
BLACKLIST = []
COUNT_PM = {}
LASTMSG = {}
ENABLE_KILLME = True
ISAFK = False
AFKREASON = None
