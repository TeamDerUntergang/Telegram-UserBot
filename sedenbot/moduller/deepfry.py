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

# Deepfry modülü kaynak kodu: https://github.com/Ovyerus/deeppyer
# @NaytSeyd tarafından portlanmıştır.

import io

from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from sedenbot import bot, CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(pattern="^.deepfry", outgoing=True) 
async def deepfryer(event):
    try:
        frycount = int(extract_args(event))
        if frycount < 1:
            raise ValueError
    except:
        frycount = 1
    
    MAX_LIMIT = 5
    if frycount > MAX_LIMIT:
        frycount = MAX_LIMIT

    if event.is_reply:
        reply_message = await event.get_reply_message()
        data = await check_media(reply_message)

        if isinstance(data, bool):
            await event.edit("`Bunu deepfry yapamam!`")
            return
    else:
        await event.edit("`Deepfry yapmam için bir resme veya çıkartmaya cevap verin!`")
        return

    # Fotoğrafı (yüksek çözünürlük) bayt dizisi olarak indir
    await event.edit("`Medya indiriliyor...`")
    image = io.BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # Resime uygula
    await event.edit("`Medyaya deepfry uygulanıyor...`")
    for _ in range(frycount):
        image = await deepfry(image)

    fried_io = io.BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    await event.reply(file=fried_io)


async def deepfry(img: Image) -> Image:
    img = img.copy().convert("RGB")

    # Resim formatı ayarla
    img = img.convert("RGB")
    width, height = img.width, img.height
    img = img.resize((int(width ** .75), int(height ** .75)), resample=Image.LANCZOS)
    img = img.resize((int(width ** .88), int(height ** .88)), resample=Image.BILINEAR)
    img = img.resize((int(width ** .9), int(height ** .9)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)
    img = ImageOps.posterize(img, 4)

    # Renk yerleşimi oluştur
    overlay = img.split()[0]
    overlay = ImageEnhance.Contrast(overlay).enhance(2)
    overlay = ImageEnhance.Brightness(overlay).enhance(1.5)

    overlay = ImageOps.colorize(overlay, Color.RED, Color.YELLOW)

    # Kırmızı ve sarıyı ana görüntüye yerleştir ve keskinleştir
    img = Image.blend(img, overlay, .75)
    img = ImageEnhance.Sharpness(img).enhance(100)

    return img


async def check_media(reply_message):
    if reply_message and reply_message.media:
        if reply_message.photo:
            data = reply_message.photo
        elif reply_message.document:
            if DocumentAttributeFilename(file_name='AnimatedSticker.tgs') in reply_message.media.document.attributes:
                return False
            if reply_message.gif or reply_message.video or reply_message.audio or reply_message.voice:
                return False
            data = reply_message.media.document
        else:
            return False
    else:
        return False

    if not data:
        return False
    else:
        return data

class Color:
    RED = (254, 0, 2)
    YELLOW = (255, 255, 15)

CMD_HELP.update({
    "deepfry":
    ".deepfry [numara 1-5]\
    \nKullanım: Belirlenen görüntüye deepfry efekti uygular."
})
