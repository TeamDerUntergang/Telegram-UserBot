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

""" Internet ile alakalı bilgileri edinmek için kullanılan UserBot modülüdür. """

import io
import speedtest

from datetime import datetime
from telethon import functions
from telethon import events

from sedenbot.moduller.upload_download import progress, humanbytes, time_formatter
from sedenbot import CMD_HELP, bot
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.speedtest")
async def _(event):
    if event.fwd_from:
        return
    input_str = extract_args(event)
    as_text = False
    as_document = True
    if input_str == "image":
        as_document = False
    elif input_str == "file":
        as_document = True
    elif input_str == "text":
        as_text = True
    await event.edit("**İnternet hızımı hesaplıyorum. Lütfen bekle!**")
    start = datetime.now()
    s = speedtest.Speedtest()
    s.get_best_server()
    s.download()
    s.upload()
    end = datetime.now()
    ms = (end - start).microseconds / 1000
    response = s.results.dict()
    download_speed = response.get("download")
    upload_speed = response.get("upload")
    ping_time = response.get("ping")
    client_infos = response.get("client")
    i_s_p = client_infos.get("isp")
    i_s_p_rating = client_infos.get("isprating")
    reply_msg_id = event.message.id
    if event.reply_to_msg_id:
        reply_msg_id = event.reply_to_msg_id
    try:
        response = s.results.share()
        speedtest_image = response
        if as_text:
            await event.edit("""**SpeedTest**, {} saniye içinde tamamlandı
İndirme Hızı: {}
Yükleme Hızı: {}
Ping: {}
İnternet Servis Sağlayıcısı: {}
ISP Rating: {}""".format(ms, convert_from_bytes(download_speed), convert_from_bytes(upload_speed), ping_time, i_s_p, i_s_p_rating))
        else:
            await bot.send_file(
                event.chat_id,
                speedtest_image,
                caption="**SpeedTest**, {} saniye içinde tamamlandı".format(ms),
                force_document=as_document,
                reply_to=reply_msg_id,
                allow_cache=False
            )
            await event.delete()
    except Exception as exc:
        await event.edit("""**SpeedTest**, {} saniye içinde tamamlandı
İndirme Hızı: {}
Yükleme Hızı: {}
Ping: {}
__With the Following ERRORs__
{}""".format(ms, convert_from_bytes(download_speed), convert_from_bytes(upload_speed), ping_time, str(exc)))


def convert_from_bytes(size):
    power = 2**10
    n = 0
    units = {
        0: "",
        1: "kilobytes",
        2: "megabytes",
        3: "gigabytes",
        4: "terabytes"
    }
    while size > power:
        size /= power
        n += 1
    return f"{round(size, 2)} {units[n]}"

@sedenify(outgoing=True, pattern="^.dc$")
async def neardc(event):
    """ .dc komutu en yakın datacenter bilgisini verir. """
    result = await event.client(functions.help.GetNearestDcRequest())
    await event.edit(f"Şehir : `{result.country}`\n"
                     f"En yakın datacenter : `{result.nearest_dc}`\n"
                     f"Şu anki datacenter : `{result.this_dc}`")

@sedenify(outgoing=True, pattern="^.ping")
async def pingme(pong):
    """ .ping komutu userbotun ping değerini herhangi bir sohbette gösterebilir.  """
    start = datetime.now()
    await pong.edit("`Pong!`")
    end = datetime.now()
    duration = (end - start).microseconds / 1000
    await pong.edit("`Pong!\n%sms`" % (duration))

CMD_HELP.update(
    {"speedtest": ".speedtest\
    \nKullanım: Bir speedtest uygular ve sonucu gösterir."})   
CMD_HELP.update(
    {"dc": ".dc\
    \nKullanım: Sunucunuza en yakın datacenter'ı gösterir."})
CMD_HELP.update(
    {"ping": ".ping\
    \nKullanım: Botun ping değerini gösterir."})
