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

""" Not tutma komutlarını içeren UserBot modülüdür. """

from asyncio import sleep

from sedenbot import BOTLOG, BOTLOG_CHATID, CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.notes$")
async def notes_active(svd):
    """ .notes komutu sohbette kaydedilmiş tüm notları listeler. """
    try:
        from sedenbot.moduller.sql_helper.notes_sql import get_notes
    except AttributeError:
        await svd.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    message = "`Bu sohbette kaydedilmiş not bulunamadı`"
    notes = get_notes(svd.chat_id)
    for note in notes:
        if message == "`Bu sohbette kaydedilmiş not bulunamadı`":
            message = "Bu sohbette kayıtlı notlar:\n"
            message += "`#{}`\n".format(note.keyword)
        else:
            message += "`#{}`\n".format(note.keyword)
    await svd.edit(message)

@sedenify(outgoing=True, pattern=r"^.clear")
async def remove_notes(clr):
    """ .clear komutu istenilen notu siler. """
    try:
        from sedenbot.moduller.sql_helper.notes_sql import rm_note
    except AttributeError:
        await clr.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    notename = extract_args(clr)
    if rm_note(clr.chat_id, notename) is False:
        return await clr.edit(" **{}** `notu bulunamadı`".format(notename))
    else:
        return await clr.edit(
            "**{}** `notu başarıyla silindi`".format(notename))

@sedenify(outgoing=True, pattern=r"^.save(.*)")
async def add_note(fltr):
    """ .save komutu bir sohbette not kaydeder. """
    try:
        from sedenbot.moduller.sql_helper.notes_sql import add_note
    except AttributeError:
        await fltr.edit("`Bot Non-SQL modunda çalışıyor!!`")
        return
    args = extract_args(fltr).split(' ', 1)
    if len(args) < 2:
        await fltr.edit("`Komut kullanımı hatalı.`")
        return
    keyword = args[0]
    string = args[1]
    msg = await fltr.get_reply_message()
    msg_id = None
    if msg and msg.media and not string:
        if BOTLOG_CHATID:
            await fltr.client.send_message(
                BOTLOG_CHATID, f"#NOTE\
            \nGrup ID: {fltr.chat_id}\
            \nAnahtar kelime: {keyword}\
            \n\nBu mesaj sohbette notu cevaplamak için kaydedildi, lütfen bu mesajı silmeyin!"
            )
            msg_o = await fltr.client.forward_messages(entity=BOTLOG_CHATID,
                                                       messages=msg,
                                                       from_peer=fltr.chat_id,
                                                       silent=True)
            msg_id = msg_o.id
        else:
            await fltr.edit(
                "`Bir medyayı not olarak kaydetmek için BOTLOG_CHATID değerinin ayarlanmış olması gereklidir.`"
            )
            return
    elif fltr.reply_to_msg_id and not string:
        rep_msg = await fltr.get_reply_message()
        string = rep_msg.text
    success = "`Not başarıyla {}. ` #{} `komutuyla notu çağırabilirsiniz`"
    if add_note(str(fltr.chat_id), keyword, string, msg_id) is False:
        return await fltr.edit(success.format('güncellendi', keyword))
    else:
        return await fltr.edit(success.format('eklendi', keyword))

@sedenify(pattern=r"#\w*",
          disable_edited=True,
          disable_errors=True,
          ignore_unsafe=True)
async def incom_note(getnt):
    """ Notların mantığı. """
    try:
        if not (await getnt.get_sender()).bot:
            try:
                from sedenbot.moduller.sql_helper.notes_sql import get_note
            except AttributeError:
                return
            notename = getnt.text[1:]
            note = get_note(getnt.chat_id, notename)
            message_id_to_reply = getnt.message.reply_to_msg_id
            if not message_id_to_reply:
                message_id_to_reply = None
            if note and note.f_mesg_id:
                msg_o = await getnt.client.get_messages(entity=BOTLOG_CHATID,
                                                        ids=int(
                                                            note.f_mesg_id))
                await getnt.client.send_message(getnt.chat_id,
                                                msg_o.mesage,
                                                reply_to=message_id_to_reply,
                                                file=msg_o.media)
            elif note and note.reply:
                await getnt.client.send_message(getnt.chat_id,
                                                note.reply,
                                                reply_to=message_id_to_reply)
    except AttributeError:
        pass

@sedenify(outgoing=True, pattern="^.rmbotnotes")
async def kick_marie_notes(kick):
    """ .rmbotnotes komutu Marie'de (ya da onun tabanındaki botlarda) \
        kayıtlı olan notları silmeye yarar. """
    bot_type = extract_args(kick).lower()
    if bot_type not in ["marie", "rose"]:
        await kick.edit("`Bu bot henüz desteklenmiyor.`")
        return
    await kick.edit("```Tüm notlar temizleniyor...```")
    await sleep(3)
    resp = await kick.get_reply_message()
    if not resp:
        await kick.edit("`Komut kullanımı hatalı.`")
        return
    filters = resp.text.split("-")[1:]
    for i in filters:
        if bot_type == "marie":
            await kick.reply("/clear %s" % (i.strip()))
        if bot_type == "rose":
            i = i.replace('`', '')
            await kick.reply("/clear %s" % (i.strip()))
        await sleep(0.3)
    await kick.respond(
        "```Botlardaki notlar başarıyla temizlendi.```")
    if BOTLOG:
        await kick.client.send_message(
            BOTLOG_CHATID, "Şu sohbetteki tüm notları temizledim: " + str(kick.chat_id))

CMD_HELP.update({
    "notes":
    "\
#<notismi>\
\nKullanım: Belirtilen notu çağırır.\
\n\n.save <not adı> <not olarak kaydedilecek şey> ya da bir mesajı .save <not adı> şeklinde yanıtlayarak kullanılır. \
\nKullanım: Yanıtlanan mesajı ismiyle birlikte bir not olarak kaydeder. (Resimler, belgeler ve çıkartmalarda da çalışır.)\
\n\n.notes\
\nKullanım: Bir sohbetteki tüm notları çağırır.\
\n\n.clear <not adı>\
\nKullanım: Belirtilen notu siler.\
\n\n.rmbotnotes <marie/rose>\
\nKullanım: Grup yönetimi botlarındaki tüm notları temizler. (Şu anlık Rose, Marie ve Marie klonları destekleniyor.)"
})
