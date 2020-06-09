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

from math import sqrt
from emoji import emojize
from datetime import datetime
from re import search

from telethon.utils import get_input_location
from telethon.tl.functions.channels import GetFullChannelRequest, GetParticipantsRequest
from telethon.tl.functions.messages import GetHistoryRequest, CheckChatInviteRequest, GetFullChatRequest
from telethon.tl.types import MessageActionChannelMigrateFrom, ChannelParticipantsAdmins, MessageEntityMentionName
from telethon.errors import (ChannelInvalidError, ChannelPrivateError, 
                             ChannelPublicGroupNaError, InviteHashEmptyError, 
                             InviteHashExpiredError, InviteHashInvalidError)

from sedenbot import CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(pattern="^.chatinfo", outgoing=True)
async def info(event):
    await event.edit("`Grup analiz ediliyor...`")
    chat = await get_chatinfo(event)
    if not chat:
        return
    caption = await fetch_info(chat, event)
    try:
        await event.edit(caption, parse_mode="html")
    except Exception as e:
        print("Exception:", e)
        await event.edit("`Beklenmeyen bir hata oluştu.`")
    return

async def get_chatinfo(event):
    chat = extract_args(event)
    chat_info = None
    if len(chat) > 0 and search('^-?\d+$', chat):
        chat = int(chat)
    elif event.reply_to_msg_id:
        replied_msg = await event.get_reply_message()
        if replied_msg.fwd_from and replied_msg.fwd_from.channel_id :
            chat = replied_msg.fwd_from.channel_id
    elif event.message.entities:
        entity = event.message.entities[0]
        if isinstance(entity, MessageEntityMentionName):
            chat = entity.user_id
    else:
        chat = event.chat_id

    try:
        chat_info = await event.client(GetFullChatRequest(chat))
    except:
        try:
            chat_info = await event.client(GetFullChannelRequest(chat))
        except ChannelInvalidError:
            await event.edit("`Geçersiz kanal/grup`")
            return None
        except ChannelPrivateError:
            await event.edit("`Bu özel bir kanal/grup veya oradan yasaklandım`")
            return None
        except ChannelPublicGroupNaError:
            await event.edit("`Kanal veya süpergrup mevcut değil`")
            return None
        except (TypeError, ValueError) as err:
            await event.edit("`Baktığım şey bir kanal/grup olmayabilir`")
            return None
    return chat_info

async def fetch_info(chat, event):
    chat_obj_info = await event.client.get_entity(chat.full_chat.id)
    broadcast = chat_obj_info.broadcast if hasattr(chat_obj_info, "broadcast") else False
    chat_type = "Kanal" if broadcast else "Grup"
    chat_title = chat_obj_info.title
    warn_emoji = emojize(":warning:")
    try:
        msg_info = await event.client(GetHistoryRequest(peer=chat_obj_info.id, offset_id=0, offset_date=datetime(2010, 1, 1), 
                                                        add_offset=-1, limit=1, max_id=0, min_id=0, hash=0))
    except Exception as e:
        msg_info = None
        print("Exception:", e)
    first_msg_valid = True if msg_info and msg_info.messages and msg_info.messages[0].id == 1 else False
    creator_valid = True if first_msg_valid and msg_info.users else False
    creator_id = msg_info.users[0].id if creator_valid else None
    creator_firstname = msg_info.users[0].first_name if creator_valid and msg_info.users[0].first_name  else "Deleted Account"
    creator_username = msg_info.users[0].username if creator_valid and msg_info.users[0].username  else None
    created = msg_info.messages[0].date if first_msg_valid else None
    former_title = msg_info.messages[0].action.title if first_msg_valid and type(msg_info.messages[0].action) is MessageActionChannelMigrateFrom and msg_info.messages[0].action.title != chat_title else None
    try:
        dc_id, location = get_input_location(chat.full_chat.chat_photo)
    except Exception as e:
        dc_id = "Unknown"
        location = str(e)

    description = chat.full_chat.about
    members = chat.full_chat.participants_count if hasattr(chat.full_chat, "participants_count") else chat_obj_info.participants_count
    admins = chat.full_chat.admins_count if hasattr(chat.full_chat, "admins_count") else None
    banned_users = chat.full_chat.kicked_count if hasattr(chat.full_chat, "kicked_count") else None
    restrcited_users = chat.full_chat.banned_count if hasattr(chat.full_chat, "banned_count") else None
    members_online = chat.full_chat.online_count if hasattr(chat.full_chat, "online_count") else 0
    group_stickers = chat.full_chat.stickerset.title if hasattr(chat.full_chat, "stickerset") and chat.full_chat.stickerset else None
    messages_viewable = msg_info.count if msg_info else None
    messages_sent = chat.full_chat.read_inbox_max_id if hasattr(chat.full_chat, "read_inbox_max_id") else None
    messages_sent_alt = chat.full_chat.read_outbox_max_id if hasattr(chat.full_chat, "read_outbox_max_id") else None
    exp_count = chat.full_chat.pts if hasattr(chat.full_chat, "pts") else None
    username = chat_obj_info.username if hasattr(chat_obj_info, "username") else None
    bots_list = chat.full_chat.bot_info  # this is a list
    bots = 0
    supergroup = "<b>Evet</b>" if hasattr(chat_obj_info, "megagroup") and chat_obj_info.megagroup else "Hayır"
    slowmode = "<b>Evet</b>" if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else "Hayır"
    slowmode_time = chat.full_chat.slowmode_seconds if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled else None
    restricted = "<b>Evet</b>" if hasattr(chat_obj_info, "restricted") and chat_obj_info.restricted else "Hayır"
    verified = "<b>Evet</b>" if hasattr(chat_obj_info, "verified") and chat_obj_info.verified else "Hayır"
    username = "@{}".format(username) if username else None
    creator_username = "@{}".format(creator_username) if creator_username else None

    if not admins:
        try:
            participants_admins = await event.client(GetParticipantsRequest(channel=chat.full_chat.id, filter=ChannelParticipantsAdmins(),
                                                                            offset=0, limit=0, hash=0))
            admins = participants_admins.count if participants_admins else None
        except Exception as e:
            print("Exception:", e)
    if bots_list:
        for bot in bots_list:
            bots += 1

    caption = "<b>GRUP BILGISI:</b>\n"
    caption += f"ID: <code>{chat_obj_info.id}</code>\n"
    if chat_title :
        caption += f"{chat_type} ismi: {chat_title}\n"
    if former_title :
        caption += f"Eski grup: {former_title}\n"
    if username :
        caption += f"{chat_type} tipi: Herkese açık\n"
        caption += f"Link: {username}\n"
    else:
        caption += f"{chat_type} tipi: Gizli\n"
    if creator_username :
        caption += f"Oluşturan kişi: {creator_username}\n"
    elif creator_valid:
        caption += f"Oluşturan kişi: <a href=\"tg://user?id={creator_id}\">{creator_firstname}</a>\n"
    if created :
        caption += f"Oluşturulma tarihi: <code>{created.date().strftime('%b %d, %Y')} - {created.time()}</code>\n"
    else:
        caption += f"Oluşturulma tarihi: <code>{chat_obj_info.date.date().strftime('%b %d, %Y')} - {chat_obj_info.date.time()}</code> {warn_emoji}\n"
    caption += f"Veri merkezi ID: {dc_id}\n"
    if exp_count :
        chat_level = int((1+sqrt(1+7*exp_count/14))/2)
        caption += f"{chat_type} seviyesi: <code>{chat_level}</code>\n"
    if messages_viewable :
        caption += f"Görüntülenebilir mesajlar: <code>{messages_viewable}</code>\n"
    if messages_sent:
        caption += f"Gönderilen mesajlar: <code>{messages_sent}</code>\n"
    elif messages_sent_alt:
        caption += f"Gönderilen mesajlar: <code>{messages_sent_alt}</code> {warn_emoji}\n"
    if members :
        caption += f"Üye sayısı: <code>{members}</code>\n"
    if admins :
        caption += f"Yönetici sayısı: <code>{admins}</code>\n"
    if bots_list:
        caption += f"Bot sayısı: <code>{bots}</code>\n"
    if members_online:
        caption += f"Çevrimiçi kişi sayısı: <code>{members_online}</code>\n"
    if restrcited_users :
        caption += f"Kısıtlı kullanıcı sayısı: <code>{restrcited_users}</code>\n"
    if banned_users :
        caption += f"Yasaklanmış kullanıcı sayısı: <code>{banned_users}</code>\n"
    if group_stickers :
        caption += f"{chat_type} çıkartma paketi: <a href=\"t.me/addstickers/{chat.full_chat.stickerset.short_name}\">{group_stickers}</a>\n"
    caption += "\n"
    if not broadcast:
        caption += f"Yavaş mod: {slowmode}"
        if hasattr(chat_obj_info, "slowmode_enabled") and chat_obj_info.slowmode_enabled:
            caption += f", <code>{slowmode_time}s</code>\n\n"
        else:
            caption += "\n\n"
    if not broadcast:
        caption += f"Süper grup mu: {supergroup}\n\n"
    if hasattr(chat_obj_info, "restricted"):
        caption += f"Kısıtlı mı: {restricted}\n"
        if chat_obj_info.restricted:
            caption += f"> Platform: {chat_obj_info.restriction_reason[0].platform}\n"
            caption += f"> Nedeni: {chat_obj_info.restriction_reason[0].reason}\n"
            caption += f"> Metin: {chat_obj_info.restriction_reason[0].text}\n\n"
        else:
            caption += "\n"
    if hasattr(chat_obj_info, "scam") and chat_obj_info.scam:
    	caption += "Scam: <b>Evet</b>\n\n"
    if hasattr(chat_obj_info, "verified"):
        caption += f"Telegram tarafından doğrulandı mı: {verified}\n\n"
    if description:
        caption += f"Grup açıklaması: \n<code>{description}</code>\n"
    return caption

CMD_HELP.update({
    "chatinfo":
    ".chatinfo [isteğe bağlı: <grup id/grup linki (@ ile)>] \
    \nKullanım: Bir grup hakkında bilgi alır. Bazı bilgiler eksik izinler nedeniyle sınırlı olabilir."
})
