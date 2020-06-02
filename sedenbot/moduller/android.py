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

""" Android ile ilgili komutları içeren UserBot modülü """

import re
import json

from requests import get
from bs4 import BeautifulSoup

from sedenbot import CMD_HELP
from sedenbot.events import extract_args, extract_args_arr, sedenify

GITHUB = 'https://github.com'

@sedenify(outgoing=True, pattern="^.magisk")
async def magisk(request):
    """ Güncel Magisk sürümleri """
    magisk_dict = {
        "Stable":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/master/stable.json",
        "Beta":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/master/beta.json",
        "Canary (Release)":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/canary/release.json",
        "Canary (Debug)":
        "https://raw.githubusercontent.com/topjohnwu/magisk_files/canary/debug.json"
    }
    releases = 'Güncel Magisk sürümleri:\n'
    for name, release_url in magisk_dict.items():
        data = get(release_url).json()
        releases += f'{name}: [ZIP v{data["magisk"]["version"]}]({data["magisk"]["link"]}) | ' \
                    f'[APK v{data["app"]["version"]}]({data["app"]["link"]}) | ' \
                    f'[Uninstaller]({data["uninstaller"]["link"]})\n'
    await request.edit(releases)

@sedenify(outgoing=True, pattern=r"^.device")
async def device_info(request):
    """ Kod adı ile cihaz hakkında bilgi alın """
    textx = await request.get_reply_message()
    codename = extract_args(request)
    if codename:
        pass
    elif textx:
        codename = textx.text
    else:
        await request.edit("`Kullanım: .device <kod adı> / <model>`")
        return
    data = json.loads(get("https://raw.githubusercontent.com/androidtrackers/"
                          "certified-android-devices/master/by_device.json").text)
    results = data.get(codename)
    if results:
        reply = f"**{codename} için arama sonuçları**:\n\n"
        for item in results:
            reply += f"**Marka**: {item['brand']}\n" \
                     f"**İsim**: {item['name']}\n" \
                     f"**Model**: {item['model']}\n\n"
    else:
        reply = f"`{codename} cihazı için bilgi bulanamadı!`\n"
    await request.edit(reply)

@sedenify(outgoing=True, pattern=r"^.codename")
async def codename_info(request):
    """ Cihazın kod adını bulmak için arama yapın """
    textx = await request.get_reply_message()
    arr = extract_args_arr(request)
    brand = arr[0].lower()
    device = arr[1].lower()
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(' ')[0]
        device = ' '.join(textx.text.split(' ')[1:])
    else:
        await request.edit("`Kullanım: .codename <marka> <cihaz>`")
        return
    data = json.loads(get("https://raw.githubusercontent.com/androidtrackers/"
                          "certified-android-devices/master/by_brand.json").text)
    devices_lower = {k.lower():v for k,v in data.items()} # Lower brand names in JSON
    devices = devices_lower.get(brand)
    results = [i for i in devices if i["name"].lower() == device.lower() or i["model"].lower() == device.lower()]
    if results:
        reply = f"**{brand} {device} için arama sonuçları**:\n\n"
        if len(results) > 8:
            results = results[:8]
        for item in results:
            reply += f"**Kod Adı**: {item['device']}\n" \
                     f"**İsim**: {item['name']}\n" \
                     f"**Model**: {item['model']}\n\n"
    else:
        reply = f"`{device} bulunamadı`\n"
    await request.edit(reply)

@sedenify(outgoing=True, pattern=r"^.specs")
async def devices_specifications(request):
    """ Mobil cihaz özellikleri """
    textx = await request.get_reply_message()
    arr = extract_args_arr(request)
    brand = arr[0].lower()
    device = arr[1].lower()
    if brand and device:
        pass
    elif textx:
        brand = textx.text.split(' ')[0]
        device = ' '.join(textx.text.split(' ')[1:])
    else:
        await request.edit("`Kullanım: .specs <marka> <cihaz>`")
        return
    all_brands = BeautifulSoup(
        get('https://www.devicespecifications.com/tr/brand-more').content,
        'html.parser').find('div', {
            'class': 'brand-listing-container-news'
        }).findAll('a')
    brand_page_url = None
    try:
        brand_page_url = [
            i['href'] for i in all_brands if brand == i.text.strip().lower()
        ][0]
    except IndexError:
        await request.edit(f'`{brand} bilinmeyen marka!`')
    devices = BeautifulSoup(get(brand_page_url).content, 'html.parser') \
        .findAll('div', {'class': 'model-listing-container-80'})
    device_page_url = None
    try:
        device_page_url = [
            i.a['href']
            for i in BeautifulSoup(str(devices), 'html.parser').findAll('h3')
            if device in i.text.strip().lower()
        ]
    except IndexError:
        await request.edit(f"`{device} bulunamadı!`")
    if len(device_page_url) > 2:
        device_page_url = device_page_url[:2]
    reply = ''
    for url in device_page_url:
        info = BeautifulSoup(get(url).content, 'html.parser')
        reply = '\n**' + info.title.text.split('-')[0].strip() + '**\n\n'
        info = info.find('div', {'id': 'model-brief-specifications'})
        specifications = re.findall(r'<b>.*?<br/>', str(info))
        for item in specifications:
            title = re.findall(r'<b>(.*?)</b>', item)[0].strip()
            data = re.findall(r'</b>: (.*?)<br/>', item)[0]\
                .replace('<b>', '').replace('</b>', '').strip()
            reply += f'**{title}**: {data}\n'
    await request.edit(reply)

@sedenify(outgoing=True, pattern=r"^.twrp")
async def twrp(request):
    """ Android cihazlar için TWRP """
    textx = await request.get_reply_message()
    device = extract_args(request)
    if device:
        pass
    elif textx:
        device = textx.text.split(' ')[0]
    else:
        await request.edit("`Kullanım: .twrp <kod adı>`")
        return
    url = get(f'https://dl.twrp.me/{device}/')
    if url.status_code == 404:
        reply = f"`{device} için resmi twrp bulunamadı!`\n"
        await request.edit(reply)
        return
    page = BeautifulSoup(url.content, 'html.parser')
    download = page.find('table').find('tr').find('a')
    dl_link = f"https://dl.twrp.me{download['href']}"
    dl_file = download.text
    size = page.find("span", {"class": "filesize"}).text
    date = page.find("em").text.strip()
    reply = f'**{device} için güncel twrp:**\n' \
        f'[{dl_file}]({dl_link}) - __{size}__\n' \
        f'**Güncelleme tarihi:** __{date}__\n'
    await request.edit(reply)

CMD_HELP.update({
    "android":
    ".magisk\
\nGüncel Magisk sürümleri\
\n\n.device <kod adı>\
\nKullanım: Android cihazı hakkında bilgi\
\n\n.codename <marka> <cihaz>\
\nKullanım: Android cihaz kod adlarını arayın.\
\n\n.specs <marka> <cihaz>\
\nKullanım: Cihaz özellikleri hakkında bilgi alın.\
\n\n.twrp <kod adı>\
\nKullanım: Hedeflenen cihaz için resmi olan güncel twrp sürümlerini alın."
})
