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

"""
Grup yönetmenize yardımcı olacak UserBot modülü
"""

from asyncio import sleep
from os import remove

from telethon.errors import (BadRequestError, ChatAdminRequiredError,
                             ImageProcessFailedError, PhotoCropSizeSmallError,
                             UserAdminInvalidError)
from telethon.errors.rpcerrorlist import (UserIdInvalidError,
                                          MessageTooLongError)
from telethon.tl.functions.channels import (EditAdminRequest,
                                            EditBannedRequest,
                                            EditPhotoRequest)
from telethon.tl.functions.messages import UpdatePinnedMessageRequest
from telethon.tl.types import (PeerChannel, ChannelParticipantsAdmins,
                               ChatAdminRights, ChatBannedRights,
                               MessageEntityMentionName, MessageMediaPhoto,
                               ChannelParticipantsBots)

from sedenbot import BOTLOG, BOTLOG_CHATID, BRAIN_CHECKER, CMD_HELP, bot
from sedenbot.events import extract_args, sedenify

# =================== CONSTANT ===================
PP_TOO_SMOL = "`Görüntü çok küçük`"
PP_ERROR = "`Görüntü işleme sırasında hata oluştu`"
NO_ADMIN = "`Yönetici değilim!`"
NO_PERM = "`Yeterli iznim yok!`"
NO_SQL = "`SQL dışı modda çalışıyor!`"

CHAT_PP_CHANGED = "`Grup resmi değiştirildi`"
CHAT_PP_ERROR = "`Resmi güncellerken bazı sorunlar oluştu.`" \
                "`Belki de bir yönetici değilim`" \
                "`ya da yeterli haklara sahip değilim.`"
INVALID_MEDIA = "`Geçersiz uzantı`"

BANNED_RIGHTS = ChatBannedRights(
    until_date=None,
    view_messages=True,
    send_messages=True,
    send_media=True,
    send_stickers=True,
    send_gifs=True,
    send_games=True,
    send_inline=True,
    embed_links=True,
)

UNBAN_RIGHTS = ChatBannedRights(
    until_date=None,
    send_messages=None,
    send_media=None,
    send_stickers=None,
    send_gifs=None,
    send_games=None,
    send_inline=None,
    embed_links=None,
)

MUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=True)

UNMUTE_RIGHTS = ChatBannedRights(until_date=None, send_messages=False)
# ================================================
@sedenify(outgoing=True, pattern="^.setgpic")
async def set_group_photo(gpic):
    """ .setgpic komutu ile grubunuzun fotoğrafını değiştirebilirsiniz """
    if not gpic.is_group:
        await gpic.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    replymsg = await gpic.get_reply_message()
    chat = await gpic.get_chat()
    admin = chat.admin_rights
    creator = chat.creator
    photo = None

    if not admin and not creator:
        await gpic.edit(NO_ADMIN)
        return

    if replymsg and replymsg.media:
        if isinstance(replymsg.media, MessageMediaPhoto):
            if not replymsg.sticker:
                photo = await gpic.client.download_media(message=replymsg.photo)
        elif "image" in replymsg.media.document.mime_type.split('/'):
            photo = await gpic.client.download_file(replymsg.media.document)

    if photo:
        try:
            await gpic.client(
                EditPhotoRequest(gpic.chat_id, await
                                 gpic.client.upload_file(photo)))
            await gpic.edit(CHAT_PP_CHANGED)

        except PhotoCropSizeSmallError:
            await gpic.edit(PP_TOO_SMOL)
        except ImageProcessFailedError:
            await gpic.edit(PP_ERROR)
        except:
            await gpic.edit(INVALID_MEDIA)
    else:
        await gpic.edit(INVALID_MEDIA)

@sedenify(outgoing=True, pattern="^.promote")
@sedenify(incoming=True, from_users=BRAIN_CHECKER, pattern="^.promote")
async def promote(promt):
    """ .promote komutu ile belirlenen kişiyi yönetici yapar """
    if not promt.is_group:
        await promt.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Hedef sohbeti almak
    chat = await promt.get_chat()
    # Yetkiyi sorgula
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değilse geri dön
    if not admin and not creator:
        await promt.edit(NO_ADMIN)
        return

    new_rights = ChatAdminRights(add_admins=True,
                                 invite_users=True,
                                 change_info=True,
                                 ban_users=True,
                                 delete_messages=True,
                                 pin_messages=True)

    await promt.edit("`Yetkilendiriliyor...`")
    user, rank = await get_user_from_event(promt)
    if not rank:
        rank = "Yönetici"  # Her ihtimale karşı.
    if user:
        pass
    else:
        return

    # Geçerli kullanıcı yönetici veya sahip ise tanıtmaya çalışalım
    try:
        await promt.client(
            EditAdminRequest(promt.chat_id, user.id, new_rights, rank))
        await promt.edit(f"[{user.first_name}](tg://user?id={user.id}) `başarıyla yetkilendirildi!`")

    # Telethon BadRequestError hatası verirse
    # yönetici yapma yetkimiz yoktur
    except:
        await promt.edit(NO_PERM)
        return

    # Yetkilendirme işi başarılı olursa günlüğe belirtelim
    if BOTLOG:
        await promt.client.send_message(
            BOTLOG_CHATID, "#YETKILENDIRME\n"
            f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {promt.chat.title}(`{promt.chat_id}`)")

@sedenify(outgoing=True, pattern="^.demote")
async def demote(dmod):
    """ .demote komutu belirlenen kişiyi yöneticilikten çıkarır """
    if not dmod.is_group:
        await dmod.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await dmod.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await dmod.edit(NO_ADMIN)
        return

    # Eğer başarılı olursa, yetki düşürüleceğini beyan edelim
    await dmod.edit("`Yetki düşürülüyor...`")
    rank = "admeme"  # Burayı öylesine yazdım
    user = await get_user_from_event(dmod)
    user = user[0]
    if user:
        pass
    else:
        return

    # Yetki düşürme sonrası yeni izinler
    newrights = ChatAdminRights(add_admins=None,
                                invite_users=None,
                                change_info=None,
                                ban_users=None,
                                delete_messages=None,
                                pin_messages=None)
    # Yönetici iznini düzenle
    try:
        await dmod.client(
            EditAdminRequest(dmod.chat_id, user.id, newrights, rank))

    # Telethon BadRequestError hatası verirse
    # gerekli yetkimiz yoktur
    except:
        await dmod.edit(NO_PERM)
        return
    await dmod.edit("`Yetki başarıyla düşürüldü!`")

    # Yetki düşürme işi başarılı olursa günlüğe belirtelim
    if BOTLOG:
        await dmod.client.send_message(
            BOTLOG_CHATID, "#YETKIDUSURME\n"
            f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {dmod.chat.title}(`{dmod.chat_id}`)")

@sedenify(outgoing=True, pattern="^.ban")
async def ban(bon):
    """ .ban komutu belirlenen kişiyi gruptan yasaklar """
    if not bon.is_group:
        await bon.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await bon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await bon.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(bon)
    if user:
        pass
    else:
        return

    # Eğer kullanıcı sudo ise
    if user.id in BRAIN_CHECKER:
        await bon.edit(
            f"`Ban Hatası!` [{user.first_name}](tg://user?id={user.id}) `bir Seden yetkilisi.. Yani onu yasaklayamam.`"
        )
        return

    # Hedefi yasaklayacağınızı duyurun
    await bon.edit("`Düşman vuruldu!`")

    try:
        await bon.client(EditBannedRequest(bon.chat_id, user.id,
                                           BANNED_RIGHTS))
    except:
        await bon.edit(NO_PERM)
        return
    # Spamcılar için
    try:
        reply = await bon.get_reply_message()
        if reply:
            await reply.delete()
    except:
        await bon.edit(
            "`Mesaj atma hakkım yok! Ama yine de kullanıcı yasaklandı!`")
        return
    # Mesajı silin ve ardından komutun
    # incelikle yapıldığını söyleyin
    if reason:
        await bon.edit(f"[{user.first_name}](tg://user?id={user.id}) (`{str(user.id)}`) `yasaklandı !!`\nNedeni: {reason}")
    else:
        await bon.edit(f"[{user.first_name}](tg://user?id={user.id}) (`{str(user.id)}`) `yasaklandı !!`")
    # Yasaklama işlemini günlüğe belirtelim
    if BOTLOG:
        await bon.client.send_message(
            BOTLOG_CHATID, "#BAN\n"
            f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {bon.chat.title}(`{bon.chat_id}`)")

@sedenify(outgoing=True, pattern="^.unban")
async def nothanos(unbon):
    """ .unban komutu belirlenen kişinin yasağını kaldırır """
    if not unbon.is_group:
        await unbon.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await unbon.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await unbon.edit(NO_ADMIN)
        return

    # Her şey yolunda giderse...
    await unbon.edit("`Yasak kaldırılıyor...`")

    user = await get_user_from_event(unbon)
    user = user[0]
    if user:
        pass
    else:
        return

    try:
        await unbon.client(
            EditBannedRequest(unbon.chat_id, user.id, UNBAN_RIGHTS))
        await unbon.edit(f"[{user.first_name}](tg://user?id={user.id}) `için yasaklama başarıyla kaldırıldı`")

        if BOTLOG:
            await unbon.client.send_message(
                BOTLOG_CHATID, "#UNBAN\n"
                f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
                f"GRUP: {unbon.chat.title}(`{unbon.chat_id}`)")
    except:
        await unbon.edit("`Sanırım bu kişi yasaklama mantığım ile uyuşmuyor`")

@sedenify(outgoing=True, pattern="^.mute")
async def spider(spdr):
    """
    Bu fonksiyon temelde susturmaya yarar
    """
    if not spdr.is_group:
        await spdr.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Fonksiyonun SQL modu altında çalışıp çalışmadığını kontrol et
    try:
        from sedenbot.moduller.sql_helper.spam_mute_sql import mute
    except:
        await spdr.edit(NO_SQL)
        return

    # Yetki kontrolü
    chat = await spdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await spdr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(spdr)
    if user:
        pass
    else:
        return

    # Eğer kullanıcı sudo ise
    if user.id in BRAIN_CHECKER:
        await spdr.edit(
            f"`Mute Hatası!` [{user.first_name}](tg://user?id={user.id}) `bir Seden yetkilisi.. Yani onu susturamam.`"
        )
        return

    self_user = await spdr.client.get_me()

    if user.id == self_user.id:
        await spdr.edit(
            "`Üzgünüm ama kendimi sessize alamam...\n(ヘ･_･)ヘ┳━┳`")
        return

    # Hedefi sustaracağınızı duyurun
    await spdr.edit("`Sessize alınıyor...`")
    if mute(spdr.chat_id, user.id) is False:
        return await spdr.edit('`Hata! Kullanıcı zaten sessize alındı.`')
    else:
        try:
            await spdr.client(
                EditBannedRequest(spdr.chat_id, user.id, MUTE_RIGHTS))

            await mutmsg(spdr, user, reason)
        except UserAdminInvalidError:
            await mutmsg(spdr, user, reason)
        except:
            return await spdr.edit("`Sanırım bu kişi sessize alma mantığım ile uyuşmuyor`")


async def mutmsg(spdr, user, reason):
    # Fonksiyonun yapıldığını duyurun
    if reason:
        await spdr.edit(f"[{user.first_name}](tg://user?id={user.id}) `susturuldu !!`\nNedeni: {reason}")
    else:
        await spdr.edit(f"[{user.first_name}](tg://user?id={user.id}) `susturuldu !!`")

    # Susturma işlemini günlüğe belirtelim
    if BOTLOG:
        await spdr.client.send_message(
            BOTLOG_CHATID, "#MUTE\n"
            f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {spdr.chat.title}(`{spdr.chat_id}`)")

@sedenify(outgoing=True, pattern="^.unmute")
async def unmoot(unmot):
    """ .unmute komutu belirlenin kişinin sesini açar (yani grupta tekrardan konuşabilir) """
    if not unmot.is_group:
        await unmot.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await unmot.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await unmot.edit(NO_ADMIN)
        return

    # Fonksiyonun SQL modu altında çalışıp çalışmadığını kontrol et
    try:
        from sedenbot.moduller.sql_helper.spam_mute_sql import unmute
    except:
        await unmot.edit(NO_SQL)
        return

    await unmot.edit('```Sessizden çıkarılıyor...```')
    user = await get_user_from_event(unmot)
    user = user[0]
    if user:
        pass
    else:
        return

    if unmute(unmot.chat_id, user.id) is False:
        return await unmot.edit("`Hata! Kullanıcı zaten sessizden çıkarıldı.`")
    else:

        try:
            await unmot.client(
                EditBannedRequest(unmot.chat_id, user.id, UNBAN_RIGHTS))
            await unmot.edit(f"[{user.first_name}](tg://user?id={user.id}) `tekrardan konuşabilir!`")
        except UserAdminInvalidError:
            await unmot.edit(f"[{user.first_name}](tg://user?id={user.id}) `tekrardan konuşabilir!`")
        except:
            await unmot.edit("`Sanırım bu kişi sessizden çıkarma mantığım ile uyuşmuyor`")
            return

        if BOTLOG:
            await unmot.client.send_message(
                BOTLOG_CHATID, "#UNMUTE\n"
                f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
                f"GRUP: {unmot.chat.title}(`{unmot.chat_id}`)")

@sedenify(incoming=True)
async def muter(moot):
    """ Sessize alınan kullanıcıların mesajlarını silmek için kullanılır """
    if not moot.is_group:
        await moot.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    try:
        from sedenbot.moduller.sql_helper.spam_mute_sql import is_muted
        from sedenbot.moduller.sql_helper.gmute_sql import is_gmuted
    except:
        return
    muted = is_muted(moot.chat_id)
    gmuted = is_gmuted(moot.sender_id)
    rights = ChatBannedRights(
        until_date=None,
        send_messages=True,
        send_media=True,
        send_stickers=True,
        send_gifs=True,
        send_games=True,
        send_inline=True,
        embed_links=True,
    )
    if muted:
        for i in muted:
            if str(i.sender) == str(moot.sender_id):
                await moot.delete()
                try:
                    await moot.client(
                        EditBannedRequest(moot.chat_id, moot.sender_id, rights))
                except:
                    pass
    for i in gmuted:
        if i.sender == str(moot.sender_id):
            await moot.delete()

@sedenify(outgoing=True, pattern="^.ungmute")
async def ungmoot(un_gmute):
    """ .ungmute komutu belirlenen kişinin küresel susturulmasını kaldırır """
    if not un_gmute.is_group:
        await un_gmute.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await un_gmute.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await un_gmute.edit(NO_ADMIN)
        return

    # Fonksiyonun SQL modu altında çalışıp çalışmadığını kontrol et
    try:
        from sedenbot.moduller.sql_helper.gmute_sql import ungmute
    except:
        await un_gmute.edit(NO_SQL)
        return

    user = await get_user_from_event(un_gmute)
    user = user[0]
    if user:
        pass
    else:
        return

    await un_gmute.edit('```Küresel susturma kaldırılıyor...```')

    if ungmute(user.id) is False:
        await un_gmute.edit("`Hata! Muhtemelen kullanıcının kısıtlanması yok.`")
    else:
        # Başarı olursa bilgi ver
        await un_gmute.edit(f"[{user.first_name}](tg://user?id={user.id}) `tekradan konuşabilir.`")

        if BOTLOG:
            await un_gmute.client.send_message(
                BOTLOG_CHATID, "#UNGMUTE\n"
                f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
                f"GRUP: {un_gmute.chat.title}(`{un_gmute.chat_id}`)")

@sedenify(outgoing=True, pattern="^.gmute")
async def gspider(gspdr):
    """ .gmute komutu belirlenen kişiyi küresel olarak susturur """
    if not gspdr.is_group:
        await gspdr.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await gspdr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await gspdr.edit(NO_ADMIN)
        return

    # Fonksiyonun SQL modu altında çalışıp çalışmadığını kontrol et
    try:
        from sedenbot.moduller.sql_helper.gmute_sql import gmute
    except:
        await gspdr.edit(NO_SQL)
        return

    user, reason = await get_user_from_event(gspdr)
    if user:
        pass
    else:
        return

    # Eğer kullanıcı sudo ise
    if user.id in BRAIN_CHECKER:
        await gspdr.edit(f"`Gmute Hatası!` [{user.first_name}](tg://user?id={user.id}) `bir Seden yetkilisi.. Yani onu susturamam.`")
        return

    # Başarı olursa bilgi ver
    await gspdr.edit("`Susturuluyor...`")
    if gmute(user.id) is False:
        await gspdr.edit(
            '`Hata! Kullanıcı zaten küresel olarak susturuldu.`')
    else:
        if reason:
            await gspdr.edit(f"[{user.first_name}](tg://user?id={user.id}) `küresel olarak susturuldu!`\nNedeni: {reason}")
        else:
            await gspdr.edit(f"[{user.first_name}](tg://user?id={user.id}) `küresel olarak susturuldu!`")

        if BOTLOG:
            await gspdr.client.send_message(
                BOTLOG_CHATID, "#GMUTE\n"
                f"USER: [{user.first_name}](tg://user?id={user.id})\n"
                f"CHAT: {gspdr.chat.title}(`{gspdr.chat_id}`)")

@sedenify(outgoing=True, pattern="^.zombies", groups_only=False)
async def rm_deletedacc(show):
    """ .zombies komutu bir sohbette tüm hayalet / silinmiş / zombi hesaplarını listeler. """
    if not show.is_group:
        await show.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    con = extract_args(show).lower()
    del_u = 0
    del_status = "`Silinmiş hesap bulunamadı, grup temiz`"

    if con != "clean":
        await show.edit("`hayalet / silinmiş / zombi hesaplar aranıyor...`")
        async for user in show.client.iter_participants(show.chat_id):

            if user.deleted:
                del_u += 1
                await sleep(1)
        if del_u > 0:
            del_status = f"**`Bu grupta` **{del_u}** `tane hayalet / silinmiş / zombi hesap bulundu,\
            \ntemizlemek için --.zombies clean-- komutunu kullanın`"
        await show.edit(del_status)
        return

    # Yetki kontrolü
    chat = await show.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    if not admin and not creator:
        await show.edit("`Yönetici değilim!`")
        return

    await show.edit("`Silinmiş hesaplar çıkarılıyor...`")
    del_u = 0
    del_a = 0

    async for user in show.client.iter_participants(show.chat_id):
        if user.deleted:
            try:
                await show.client(
                    EditBannedRequest(show.chat_id, user.id, BANNED_RIGHTS))
            except UserAdminInvalidError:
                del_u -= 1
                del_a += 1
            except:
                await show.edit("`Bu grupta ban yetkim bulunmamakta`")
                return
            await show.client(
                EditBannedRequest(show.chat_id, user.id, UNBAN_RIGHTS))
            del_u += 1

    if del_u > 0:
        del_status = f"**{del_u}** tane silinmiş hesap gruptan çıkarıldı"

    if del_a > 0:
        del_status = f"**{del_u}** tane silinmiş hesap gruptan çıkarıldı \
        \n**{del_a}** tane silinmiş olan yönetici hesapları çıkartılamadı"

    await show.edit(del_status)
    await sleep(2)
    await show.delete()

    if BOTLOG:
        await show.client.send_message(
            BOTLOG_CHATID, "#TEMIZLIK\n"
            f"**{del_u}** tane silinmiş hesap çıkartıldı !!\
            \nGRUP: {show.chat.title}(`{show.chat_id}`)")

@sedenify(outgoing=True, pattern="^.pin$")
async def pin(msg):
    """ .pin komutu verildiği grupta ki yazıyı & medyayı sabitler """
    if not msg.is_group:
        await msg.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yönetici kontrolü
    chat = await msg.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await msg.edit(NO_ADMIN)
        return

    to_pin = msg.reply_to_msg_id

    if not to_pin:
        await msg.edit("`Sabitlemek için herhangi bir mesaja yanıt verin`")
        return

    options = extract_args(msg)

    is_silent = True

    if options.lower() == "loud":
        is_silent = False

    try:
        await msg.client(
            UpdatePinnedMessageRequest(msg.to_id, to_pin, is_silent))
    except:
        await msg.edit(NO_PERM)
        return

    await msg.edit("`Başarıyla sabitlendi!`")

    user = await get_user_from_id(msg.from_id, msg)

    if BOTLOG:
        await msg.client.send_message(
            BOTLOG_CHATID, "#PIN\n"
            f"ADMIN: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {msg.chat.title}(`{msg.chat_id}`)\n"
            f"LOUD: {not is_silent}")

@sedenify(outgoing=True, pattern="^.kick")
async def kick(usr):
    """ .kick komutu belirlenen kişiyi gruptan çıkartır """
    if not usr.is_group:
        await usr.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    # Yetki kontrolü
    chat = await usr.get_chat()
    admin = chat.admin_rights
    creator = chat.creator

    # Yönetici değil ise geri dön
    if not admin and not creator:
        await usr.edit(NO_ADMIN)
        return

    user, reason = await get_user_from_event(usr)
    if not user:
        await usr.edit("`Kullanıcı bulunamadı.`")
        return

    # Eğer kullanıcı sudo ise
    if user.id in BRAIN_CHECKER:
        await usr.edit(
            f"`Kick Hatası!` [{user.first_name}](tg://user?id={user.id}) `bir Seden yetkilisi.. Yani onu gruptan çıkartamam.`"
        )
        return

    await usr.edit("`Çıkartılıyor...`")

    try:
        await usr.client.kick_participant(usr.chat_id, user.id)
        await sleep(.5)
    except Exception as e:
        await usr.edit(NO_PERM + f"\n{str(e)}")
        return

    if reason:
        await usr.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `gruptan atıldı !`\nNedeni: {reason}"
        )
    else:
        await usr.edit(
            f"[{user.first_name}](tg://user?id={user.id}) `gruptan atıldı !`")

    if BOTLOG:
        await usr.client.send_message(
            BOTLOG_CHATID, "#KICK\n"
            f"KULLANICI: [{user.first_name}](tg://user?id={user.id})\n"
            f"GRUP: {usr.chat.title}(`{usr.chat_id}`)\n")

@sedenify(outgoing=True, pattern="^.(admins|bots|user(s|sdel))")
async def get_users(show):
    """ .users komutu girilen gruba ait kişileri listeler """
    if not show.is_group:
        await show.edit("`Bunun bir grup olduğunu sanmıyorum.`")
        return
    cmd = show.text.split(' ', 1)
    users = cmd[0][1:5] == 'user'
    showdel = users and cmd[0][-3:] == 'del'
    bots = not users and cmd[0][1:5] == 'bots'
    admins = not bots and cmd[0][1:7] == 'admins'
    info = await show.client.get_entity(show.chat_id)
    title = info.title if info.title else "Bu sohbet"

    mentions = ''
    filtr = None
    if users:
        mentions = f'{title} içinde bulunan{" silinmiş" if showdel else ""} kişiler: \n'
    elif admins:
        mentions = f'{title} içinde bulunan yöneticiler: \n'
        filtr = ChannelParticipantsAdmins
    elif bots:
        mentions = f'{title} içinde bulunan botlar: \n'
        filtr = ChannelParticipantsBots

    try:
        searchq = cmd[1] if users and len(cmd) > 1 else ''
        async for user in show.client.iter_participants(
                show.chat_id,
                search=f'{searchq if len(searchq) > 0 else ""}',
                filter=filtr):
            if not user.deleted and showdel:
                continue
            mentions += f"\n[{'Silinmiş hesap' if user.deleted else user.first_name}](tg://user?id={user.id}) `{user.id}`"
    except Exception as err:
        mentions += " " + str(err) + "\n"
    try:
        await show.edit(mentions)
    except MessageTooLongError:
        await show.edit(
             "Lanet olsun, bu büyük bir grup. "
            f"{'Silinmiş k' if showdel else 'K'}ullanıcı listesini dosya olarak gönderiyorum.")
        file = open("userslist.txt", "w+")
        file.write(mentions)
        file.close()
        await show.client.send_file(
            show.chat_id,
            "userslist.txt",
            caption=f"{title} grubundaki{' silinmiş' if showdel else ''} kişiler",
            reply_to=show.id,
        )
        remove("userslist.txt")

async def get_user_from_event(event):
    """ Kullanıcıyı argümandan veya yanıtlanan mesajdan alın. """
    msg = extract_args(event)
    args = msg.split(' ', 1)
    extra = None
    if event.reply_to_msg_id and not len(args) == 2:
        previous_message = await event.get_reply_message()
        user_obj = await event.client.get_entity(previous_message.from_id)
        extra = msg
    elif args:
        user = args[0]
        if len(args) == 2:
            extra = args[1]

        if user.isnumeric():
            user = int(user)

        if not user:
            await event.edit("`Kişinin kullanıcı adını, ID'sini veya yanıtını iletin!`")
            return user, extra

        if event.message.entities :
            probable_user_mention_entity = event.message.entities[0]

            if isinstance(probable_user_mention_entity,
                          MessageEntityMentionName):
                user_id = probable_user_mention_entity.user_id
                user_obj = await event.client.get_entity(user_id)
                return user_obj, extra
        try:
            user_obj = await event.client.get_entity(user)
        except Exception as err:
            await event.edit(str(err))
            return None

    return user_obj, extra


async def get_user_from_id(user, event):
    if isinstance(user, str):
        user = int(user)

    try:
        user_obj = await event.client.get_entity(user)
    except Exception as err:
        await event.edit(str(err))
        return None

    return user_obj

CMD_HELP.update({
    "admin":
    ".promote <kullanıcı adı/yanıtlama> <özel isim (isteğe bağlı)>\
\nKullanım: Sohbetteki kişiye yönetici hakları sağlar.\
\n\n.demote <kullanıcı adı/yanıtlama>\
\nKullanım: Sohbetteki kişinin yönetici izinlerini iptal eder.\
\n\n.ban <kullanıcı adı/yanıtlama> <nedeni (isteğe bağlı)>\
\nKullanım: Sohbetteki kişiyi gruptan yasaklar.\
\n\n.unban <kullanıcı adı/yanıtlama>\
\nKullanım: Sohbetteki kişinin yasağını kaldırır.\
\n\n.mute <kullanıcı adı/yanıtlama> <nedeni (isteğe bağlı)>\
\nKullanım: Sohbetteki kişiyi susturur, yöneticilerde de çalışır.\
\n\n.unmute <kullanıcı adı/yanıtlama>\
\nKullanım: Kişiyi sessize alınanlar listesinden kaldırır.\
\n\n.gmute <kullanıcı adı/yanıtlama> <nedeni (isteğe bağlı)>\
\nKullanım: Kişiyi yönetici olduğunuz tüm gruplarda susturur.\
\n\n.ungmute <kullanıcı adı/yanıtlama>\
\nKullanım: Kişiyi küresel olarak sessize alınanlar listesinden kaldırır.\
\n\n.zombies\
\nKullanım: Bir gruptaki silinmiş hesapları arar. Gruptan silinen hesapları kaldırmak için --.zombies clean-- komutunu kullanın.\
\n\n.admins\
\nKullanım: Sohbet yöneticilerinin listesini alır.\
\n\n.bots\
\nKullanım: Sohbet içinde bulunan botların listesini alır.\
\n\n.users veya .users <kullanıcı adı>\
\nKullanım: Sohbetteki tüm (veya sorgulanan) kullanıcıları alır.\
\n\n.setgppic <yanıtlanan resim>\
\nKullanım: Grubun resmini değiştirir."
})
