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

""" Filtre komutlarını içeren UserBot modülüdür. """

from asyncio import sleep
from re import fullmatch, IGNORECASE, escape

from sedenbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(incoming=True, disable_edited=True, disable_errors=True)
async def filter_incoming_handler(handler):
    """ Gelen mesajın filtre tetikleyicisi içerip içermediğini kontrol eder """
    if not (await handler.get_sender()).bot:
        try:
            from sedenbot.moduller.sql_helper.filter_sql import get_filters
        except:
            return
        name = handler.raw_text
        filters = get_filters(handler.chat_id)
        if not filters:
            return
        for trigger in filters:
            pro = fullmatch(trigger.keyword, name, flags=IGNORECASE)
            if pro and trigger.f_mesg_id:
                msg_o = await handler.client.get_messages(
                    entity=BOTLOG_CHATID, ids=int(trigger.f_mesg_id))
                await handler.reply(msg_o.message, file=msg_o.media)
            elif pro and trigger.reply:
                await handler.reply(trigger.reply)

@sedenify(outgoing=True, pattern="^.addfilter")
async def add_new_filter(new_handler):
    """ .filter komutu bir sohbete yeni filtreler eklemeye izin verir """
    try:
        from sedenbot.moduller.sql_helper.filter_sql import add_filter
    except:
        await new_handler.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    args = extract_args(new_handler)
    if len(args) < 1:
        await new_handler.edit("`Komut kullanımı hatalı.`")
        return
    arr = args.split(' ', 1)
    keyword = arr[0]
    string = None if len(arr) < 2 else arr[1]
    msg = await new_handler.get_reply_message()
    msg_id = None
    if msg:
        if msg.media:
            if BOTLOG_CHATID:
                await new_handler.client.send_message(
                    BOTLOG_CHATID, f"#FILTER\
                \nGrup ID: {new_handler.chat_id}\
                \nFiltre: {keyword}\
                \n\nBu mesaj filtrenin cevaplanması için kaydedildi, lütfen bu mesajı silmeyin!"
                )
                msg_o = await new_handler.client.forward_messages(
                    entity=BOTLOG_CHATID,
                    messages=msg,
                    from_peer=new_handler.chat_id,
                    silent=True)
                msg_id = msg_o.id
            else:
                await new_handler.edit(
                    "`Bir medyanın filtreye karşılık olarak kaydedilebilmesi için BOTLOG_CHATID değerinin ayarlanması gerekli.`"
                )
                return
        else:
            rep_msg = await new_handler.get_reply_message()
            string = rep_msg.text
    elif not string:
        await new_handler.edit("`Komut kullanımı hatalı.`")
        return
    success = " **{}** `filtresi {}`"
    if add_filter(str(new_handler.chat_id), keyword, string, msg_id):
        await new_handler.edit(success.format(keyword, 'eklendi'))
    else:
        await new_handler.edit(success.format(keyword, 'güncellendi'))

@sedenify(outgoing=True, pattern="^.stop")
async def remove_a_filter(r_handler):
    """ .stop komutu bir filtreyi durdurmanızı sağlar. """
    try:
        from sedenbot.moduller.sql_helper.filter_sql import remove_filter
    except:
        await r_handler.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    filt = extract_args(r_handler)
    if not remove_filter(r_handler.chat_id, filt):
        await r_handler.edit(" **{}** `filtresi mevcut değil.`".format(filt))
    else:
        await r_handler.edit(
            "**{}** `filtresi başarıyla silindi`".format(filt))

@sedenify(outgoing=True, pattern="^.rmbotfilters")
async def kick_marie_filter(event):
    """ .rmfilters komutu Marie'de (ya da onun tabanındaki botlarda) \
        kayıtlı olan notları silmeye yarar. """
    bot_type = extract_args(event).lower()
    if bot_type not in ["marie", "rose"]:
        await event.edit("`Bu bot henüz desteklenmiyor.`")
        return
    await event.edit("```Tüm filtreler temizleniyor...```")
    await sleep(3)
    resp = await event.get_reply_message()
    if not resp:
        await event.edit("`Komut kullanımı hatalı.`")
        return
    filters = resp.text.split("-")[1:]
    for i in filters:
        if bot_type.lower() == "marie":
            await event.reply("/stop %s" % (i.strip()))
        elif bot_type.lower() == "rose":
            i = i.replace('`', '')
            await event.reply("/stop %s" % (i.strip()))
        await sleep(0.3)
    await event.respond(
        "```Botlardaki filtreler başarıyla temizlendi.```")
    if BOTLOG:
        await event.client.send_message(
            BOTLOG_CHATID, "Şu sohbetteki tüm filtreleri temizledim: " + str(event.chat_id))

@sedenify(outgoing=True, pattern="^.filters$")
async def filters_active(event):
    """ .filters komutu bir sohbetteki tüm aktif filtreleri gösterir. """
    try:
        from sedenbot.moduller.sql_helper.filter_sql import get_filters
    except:
        await event.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    transact = "`Bu sohbette hiç filtre yok.`"
    filters = get_filters(event.chat_id)
    for filt in filters:
        if transact == "`Bu sohbette hiç filtre yok.`":
            transact = "Sohbetteki filtreler:\n"
            transact += "`{}`\n".format(filt.keyword)
        else:
            transact += "`{}`\n".format(filt.keyword)

    await event.edit(transact)

CMD_HELP.update({
    "filter":
    ".filters\
    \nKullanım: Bir sohbetteki tüm userbot filtrelerini listeler.\
    \n\n.addfilter <filtrelenecek kelime> <cevaplanacak metin> ya da bir mesajı .filter <filtrelenecek kelime>\
    \nKullanım: 'filtrelenecek kelime' olarak istenilen şeyi kaydeder.\
    \nBot her 'filtrelenecek kelime' yi algıladığında o mesaja cevap verecektir.\
    \nDosyalardan çıkartmalara her türlü şeyle çalışır.\
    \n\n.stop <filtre>\
    \nKullanım: Seçilen filtreyi durdurur.\
    \n\n.rmbotfilters <marie/rose>\
    \nKullanım: Grup yönetimi botlarındaki tüm filtreleri temizler. (Şu anlık Rose, Marie ve Marie klonları destekleniyor.)"
})
