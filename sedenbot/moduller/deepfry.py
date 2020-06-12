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

from io import BytesIO

from random import randint, uniform
from PIL import Image, ImageEnhance, ImageOps
from telethon.tl.types import DocumentAttributeFilename

from sedenbot import bot, CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(pattern="^.(deepf|f)ry", outgoing=True) 
async def deepfryer(event):

    text = event.text.split(' ', 1)
    fry = text[0][1:4] == 'fry'

    try:
        frycount = int(text[1])
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
    image = BytesIO()
    await event.client.download_media(data, image)
    image = Image.open(image)

    # Resime uygula
    await event.edit("`Medyaya deepfry uygulanıyor...`")
    for _ in range(frycount):
        image = await deepfry(image, fry)

    fried_io = BytesIO()
    fried_io.name = "image.jpeg"
    image.save(fried_io, "JPEG")
    fried_io.seek(0)

    await event.reply(file=fried_io)


async def deepfry(img: Image, fry: bool) -> Image:
    colors = None
    if fry:
        colors = (
            (randint(50, 200), randint(40, 170), randint(40, 190)),
            (randint(190, 255), randint(170, 240), randint(180, 250))
        )

    # Resim formatı ayarla
    img = img.copy().convert("RGB")
    width, height = img.width, img.height

    temp_num = uniform(.8, .9) if fry else .75
    img = img.resize((int(width ** temp_num), int(height ** temp_num)), resample=Image.LANCZOS)

    temp_num = uniform(.85, .95) if fry else .88
    img = img.resize((int(width ** temp_num), int(height ** temp_num)), resample=Image.BILINEAR)

    temp_num = uniform(.89, .98) if fry else .9
    img = img.resize((int(width ** temp_num), int(height ** temp_num)), resample=Image.BICUBIC)
    img = img.resize((width, height), resample=Image.BICUBIC)

    temp_num = randint(3, 7) if fry else 4
    img = ImageOps.posterize(img, temp_num)

    # Renk yerleşimi oluştur
    overlay = img.split()[0]

    temp_num = uniform(1.0, 2.0) if fry else 2
    overlay = ImageEnhance.Contrast(overlay).enhance(temp_num)

    temp_num = uniform(1.0, 2.0) if fry else 1.5
    overlay = ImageEnhance.Brightness(overlay).enhance(temp_num)

    overlay = ImageOps.colorize(
        overlay, 
        colors[0] if fry else (254, 0, 2), 
        colors[1] if fry else (255, 255, 15)
    )

    # Kırmızı ve sarıyı ana görüntüye yerleştir ve keskinleştir
    temp_num = uniform(0.1, 0.4) if fry else .75
    img = Image.blend(img, overlay, temp_num)

    temp_num = randint(5, 300) if fry else 100
    img = ImageEnhance.Sharpness(img).enhance(temp_num)

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

CMD_HELP.update({
    "deepfry":
    ".deepfry veya .fry [numara 1-5]\
    \nKullanım: Belirlenen görüntüye deepfry efekti uygular."
})
