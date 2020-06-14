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

""" Diğer kategorilere uymayan fazlalık komutların yer aldığı modül. """

import os
import re
import time
import asyncio
import shutil
import wikipedia

from io import BytesIO
from base64 import b64decode
from bs4 import BeautifulSoup
from time import sleep
from html import unescape
from re import findall
from selenium.webdriver import Chrome
from urllib.parse import quote_plus
from urllib.error import HTTPError
from selenium.webdriver.support.ui import Select
from selenium.webdriver.chrome.options import Options
from wikipedia import summary
from wikipedia.exceptions import DisambiguationError, PageError
from urbandict import define
from requests import get
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from googletrans import LANGUAGES, Translator
from gtts import gTTS
from gtts.lang import tts_langs
from emoji import get_emoji_regexp
from youtube_dl import YoutubeDL
from youtube_dl.utils import (DownloadError, ContentTooShortError,
                              ExtractorError, GeoRestrictedError,
                              MaxDownloadsReached, PostProcessingError,
                              UnavailableVideoError, XAttrMetadataError)
from asyncio import sleep
from telethon.tl.types import DocumentAttributeAudio

from sedenbot.moduller.upload_download import progress, humanbytes, time_formatter
from sedenbot import CMD_HELP, BOTLOG, BOTLOG_CHATID, YOUTUBE_API_KEY, CHROME_DRIVER
from sedenbot.events import extract_args, sedenify

CARBONLANG = "auto"
TTS_LANG = "tr"
TRT_LANG = "tr"

@sedenify(outgoing=True, pattern="^.crblang")
async def setlang(prog):
    global CARBONLANG
    CARBONLANG = extract_args(prog)
    await prog.edit(f"Karbon modülü için varsayılan dil {CARBONLANG} olarak ayarlandı.")

@sedenify(outgoing=True, pattern="^.carbon")
async def carbon_api(e):
    """ carbon.now.sh için bir çeşit wrapper """
    await e.edit("`İşleniyor...`")
    CARBON = 'https://carbon.now.sh/?l={lang}&code={code}'
    global CARBONLANG
    textx = await e.get_reply_message()
    pcode = e.text
    if pcode[8:]:
        pcode = str(pcode[8:])
    elif textx:
        pcode = str(textx.message)  # Girilen metin, modüle aktarılıyor.
    code = quote_plus(pcode)  # Çözülmüş url'ye dönüştürülüyor.
    await e.edit("`İşleniyor...\nTamamlanma Oranı: 25%`")
    if os.path.isfile("./carbon.png"):
        os.remove("./carbon.png")
    url = CARBON.format(code=code, lang=CARBONLANG)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    prefs = {'download.default_directory': './'}
    chrome_options.add_experimental_option('prefs', prefs)
    driver = Chrome(executable_path=CHROME_DRIVER,
                              options=chrome_options)
    driver.get(url)
    await e.edit("`İşleniyor...\nTamamlanma Oranı: 50%`")
    download_path = './'
    driver.command_executor._commands["send_command"] = (
        "POST", '/session/$sessionId/chromium/send_command')
    params = {
        'cmd': 'Page.setDownloadBehavior',
        'params': {
            'behavior': 'allow',
            'downloadPath': download_path
        }
    }
    command_result = driver.execute("send_command", params)
    driver.find_element_by_xpath("//button[contains(text(),'Export')]").click()
    await e.edit("`İşleniyor...\nTamamlanma Oranı: 75%`")
    # İndirme için bekleniyor
    while not os.path.isfile("./carbon.png"):
        await sleep(0.5)
    await e.edit("`İşleniyor...\nTamamlanma Oranı: 100%`")
    file = './carbon.png'
    await e.edit("`Resim karşıya yükleniyor...`")
    await e.client.send_file(
        e.chat_id,
        file,
        caption="Bu resim [Carbon](https://carbon.now.sh/about/) kullanılarak yapıldı,\
        \nbir [Dawn Labs](https://dawnlabs.io/) projesi.",
        force_document=True,
        reply_to=e.message.reply_to_msg_id,
    )

    os.remove('./carbon.png')
    driver.quit()
    # Karşıya yüklemenin ardından carbon.png kaldırılıyor
    await e.delete()  # Mesaj siliniyor

# @frknkrc44 tarafından baştan yazıldı
@sedenify(outgoing=True, pattern="^.img")
async def img_sampler(event):
    """ .img komutu Google'da resim araması yapar. """
    query = extract_args(event)
    lim = findall(r"lim=\d+", query)
    try:
        lim = lim[0]
        lim = lim.replace("lim=", "")
        query = query.replace("lim=" + lim[0], "")
        lim = int(lim)
    except IndexError:
        lim = 5

    if len(query) < 1:
        await event.edit('`Bir arama terimi girmelisiniz.`')
        return
    await event.edit("`İşleniyor...`")
    
    url = f'https://www.google.com/search?tbm=isch&q={query}&gbv=2&sa=X&biw=1920&bih=1080'
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = Chrome(executable_path=CHROME_DRIVER,
                              options=chrome_options)
    driver.get(url)
    count = 1
    files = []
    for i in driver.find_elements_by_xpath('//div[contains(@class,"isv-r PNCib MSM1fd BUooTd")]'):
        i.click()
        try_count = 0
        while len(element := driver.find_elements_by_xpath('//img[contains(@class,"n3VNCb") and contains(@src,"http")]')) < 1 and try_count < 20:
            try_count += 1
            asyncio.sleep(.1)
        if len(element) < 1:
            continue
        link = element[0].get_attribute('src')
        temp_file = BytesIO(get(link).content)
        temp_file.name = f'result_{count}.jpeg'
        files.append(temp_file)
        asyncio.sleep(1)
        driver.find_elements_by_xpath('//a[contains(@class,"hm60ue")]')[0].click()
        count += 1
        if lim < count:
            break
        asyncio.sleep(1)
    
    driver.quit()
    
    await event.client.send_file(
        await event.client.get_input_entity(event.chat_id), files)
    await event.delete()

@sedenify(outgoing=True, pattern="^.currency (.*)")
async def moni(event):
    input_str = extract_args(event)
    input_sgra = input_str.split(" ")
    if len(input_sgra) == 3:
        try:
            number = float(input_sgra[0])
            currency_from = input_sgra[1].upper()
            currency_to = input_sgra[2].upper()
            request_url = "https://api.exchangeratesapi.io/latest?base={}".format(
                currency_from)
            current_response = get(request_url).json()
            if currency_to in current_response["rates"]:
                current_rate = float(current_response["rates"][currency_to])
                rebmun = round(number * current_rate, 2)
                await event.edit("{} {} = {} {}".format(
                    number, currency_from, rebmun, currency_to))
            else:
                await event.edit(
                    "`Yazdığın şey uzaylıların kullandığı bir para birimine benziyor, bu yüzden dönüştüremiyorum.`"
                )
        except Exception as e:
            await event.edit(str(e))
    else:
        await event.edit("`Sözdizimi hatası.`")
        return

@sedenify(outgoing=True, pattern=r"^.google")
async def gsearch(q_event):
    """ .google komutu ile basit Google aramaları gerçekleştirilebilir """
    match = extract_args(q_event)
    if len(match) < 1:
        await q_event.edit('`Komut kullanımı hatalı.`')
        return
    page = findall(r"page=\d+", match)
    try:
        page = page[0]
        page = page.replace("page=", "")
        match = match.replace("page=" + page[0], "")
        page = int(page)
    except:
        page = 1
    msg = await do_gsearch(match, page)
    await q_event.edit(f"**Arama Sorgusu:**\n`{match}`\n\n**Sonuçlar:**\n{msg}",
                       link_preview=False)

    if BOTLOG:
        await q_event.client.send_message(
            BOTLOG_CHATID,
            match + " `sözcüğü başarıyla Google'da aratıldı!`",
        )

async def do_gsearch(query, page):

    def find_page(num):
        return (num - 1) * 10;

    def parse_key(keywords):
        return keywords.replace(' ','+')
        
    def get_result(res):
        link = res.find('a')['href']
        title = res.find('h3').text
        desc = res.find('span', {'class':['st']}).text
        if len(desc.strip()) < 1:
            desc = 'Açıklama bulunamadı.'
        return f'[{title}]({link})\n`{desc}`'

    query = parse_key(query)
    page = find_page(page)
    req = get(f'https://www.google.com/search?q={query}&start={find_page(page)}',
            headers={
                    'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36',
                    'Content-Type': 'text/html'
                }
          )
    soup = BeautifulSoup(req.text, 'html.parser')
    res1 = soup.findAll('div', {'class':['rc']})
    out = ""
    for i in range(0, len(res1)):
        res = res1[i]
        out += f"{i+1}-{get_result(res)}\n\n"
    return out

@sedenify(outgoing=True, pattern=r"^.wiki")
async def wiki(wiki_q):
    """ .wiki komutu Vikipedi üzerinden bilgi çeker. """
    wikipedia.set_lang("tr")
    match = extract_args(wiki_q)
    try:
        summary(match)
    except DisambiguationError as error:
        await wiki_q.edit(f"Belirsiz bir sayfa bulundu.\n\n{error}")
        return
    except PageError as pageerror:
        await wiki_q.edit(f"Aradığınız sayfa bulunamadı.\n\n{pageerror}")
        return
    result = summary(match)
    if len(result) >= 4096:
        file = open("wiki.txt", "w+")
        file.write(result)
        file.close()
        await wiki_q.client.send_file(
            wiki_q.chat_id,
            "wiki.txt",
            reply_to=wiki_q.id,
            caption="`Sonuç çok uzun, dosya yoluyla gönderiliyor...`",
        )
        if os.path.exists("wiki.txt"):
            os.remove("wiki.txt")
        return
    await wiki_q.edit("**Arama:**\n`" + match + "`\n\n**Sonuç:**\n" + result)
    if BOTLOG:
        await wiki_q.client.send_message(
            BOTLOG_CHATID, f"{match}` teriminin Wikipedia sorgusu başarıyla gerçekleştirildi!`")

@sedenify(outgoing=True, pattern="^.ud")
async def urban_dict(ud_e):
    """ .ud komutu Urban Dictionary'den bilgi çeker. """
    await ud_e.edit("İşleniyor...")
    query = extract_args(ud_e)
    try:
        define(query)
    except HTTPError:
        await ud_e.edit(f"Üzgünüm, **{query}** için hiçbir sonuç bulunamadı.")
        return
    mean = define(query)
    deflen = sum(len(i) for i in mean[0]["def"])
    exalen = sum(len(i) for i in mean[0]["example"])
    meanlen = deflen + exalen
    if int(meanlen) >= 0:
        if int(meanlen) >= 4096:
            await ud_e.edit("`Sonuç çok uzun, dosya yoluyla gönderiliyor...`")
            file = open("urbandictionary.txt", "w+")
            file.write("Sorgu: " + query + "\n\nAnlamı: " + mean[0]["def"] +
                       "\n\n" + "Örnek: \n" + mean[0]["example"])
            file.close()
            await ud_e.client.send_file(
                ud_e.chat_id,
                "urbandictionary.txt",
                caption="`Sonuç çok uzun, dosya yoluyla gönderiliyor...`")
            if os.path.exists("urbandictionary.txt"):
                os.remove("urbandictionary.txt")
            await ud_e.delete()
            return
        await ud_e.edit("Sorgu: **" + query + "**\n\nAnlamı: **" +
                        mean[0]["def"] + "**\n\n" + "Örnek: \n__" +
                        mean[0]["example"] + "__")
        if BOTLOG:
            await ud_e.client.send_message(
                BOTLOG_CHATID,
                query + " `sözcüğünün UrbanDictionary sorgusu başarıyla gerçekleştirildi!`")
    else:
        await ud_e.edit(query + " **için hiçbir sonuç bulunamadı**")

@sedenify(outgoing=True, pattern=r"^.tts")
async def text_to_speech(query):
    """ .tts komutu ile Google'ın metinden yazıya dönüştürme servisi kullanılabilir. """
    textx = await query.get_reply_message()
    message = extract_args(query)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await query.edit(
            "`Yazıdan sese çevirmek için bir metin gir.`")
        return

    try:
        gTTS(message, lang=TTS_LANG)
    except AssertionError:
        await query.edit(
            'Metin boş.\n'
            'Ön işleme, tokenizasyon ve temizlikten sonra konuşacak hiçbir şey kalmadı.'
        )
        return
    except ValueError:
        await query.edit('Bu dil henüz desteklenmiyor.')
        return
    except RuntimeError:
        await query.edit('Dilin sözlüğünü görüntülemede bir hata gerçekleşti.')
        return
    tts = gTTS(message, lang=TTS_LANG)
    tts.save("h.mp3")
    with open("h.mp3", "rb") as audio:
        linelist = list(audio)
        linecount = len(linelist)
    if linecount == 1:
        tts = gTTS(message, lang=TTS_LANG)
        tts.save("h.mp3")
    with open("h.mp3", "r"):
        await query.client.send_file(query.chat_id, "h.mp3", voice_note=True)
        os.remove("h.mp3")
        if BOTLOG:
            await query.client.send_message(
                BOTLOG_CHATID, "Metin başarıyla sese dönüştürüldü!")
        await query.delete()

@sedenify(outgoing=True, pattern="^.imdb")
async def imdb(e):
    try:
        movie_name = extract_args(e)
        remove_space = movie_name.split(' ')
        final_name = '+'.join(remove_space)
        page = get("https://www.imdb.com/find?ref_=nv_sr_fn&q=" + final_name +
                   "&s=all")
        lnk = str(page.status_code)
        soup = BeautifulSoup(page.content, 'html.parser')
        odds = soup.findAll("tr", "odd")
        mov_title = odds[0].findNext('td').findNext('td').text
        mov_link = "http://www.imdb.com/" + \
            odds[0].findNext('td').findNext('td').a['href']
        page1 = get(mov_link)
        soup = BeautifulSoup(page1.content, 'html.parser')
        if soup.find('div', 'poster'):
            poster = soup.find('div', 'poster').img['src']
        else:
            poster = ''
        if soup.find('div', 'title_wrapper'):
            pg = soup.find('div', 'title_wrapper').findNext('div').text
            mov_details = re.sub(r'\s+', ' ', pg)
        else:
            mov_details = ''
        credits = soup.findAll('div', 'credit_summary_item')
        if len(credits) == 1:
            director = credits[0].a.text
            writer = 'Not available'
            stars = 'Not available'
        elif len(credits) > 2:
            director = credits[0].a.text
            writer = credits[1].a.text
            actors = []
            for x in credits[2].findAll('a'):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + ',' + actors[1] + ',' + actors[2]
        else:
            director = credits[0].a.text
            writer = 'Not available'
            actors = []
            for x in credits[1].findAll('a'):
                actors.append(x.text)
            actors.pop()
            stars = actors[0] + ',' + actors[1] + ',' + actors[2]
        if soup.find('div', "inline canwrap"):
            story_line = soup.find('div',
                                   "inline canwrap").findAll('p')[0].text
        else:
            story_line = 'Not available'
        info = soup.findAll('div', "txt-block")
        if info:
            mov_country = []
            mov_language = []
            for node in info:
                a = node.findAll('a')
                for i in a:
                    if "country_of_origin" in i['href']:
                        mov_country.append(i.text)
                    elif "primary_language" in i['href']:
                        mov_language.append(i.text)
        if soup.findAll('div', "ratingValue"):
            for r in soup.findAll('div', "ratingValue"):
                mov_rating = r.strong['title']
        else:
            mov_rating = 'Not available'
        await e.edit('<a href=' + poster + '>&#8203;</a>'
                     '<b>Başlık : </b><code>' + mov_title + '</code>\n<code>' +
                     mov_details + '</code>\n<b>Reyting : </b><code>' +
                     mov_rating + '</code>\n<b>Ülke : </b><code>' +
                     mov_country[0] + '</code>\n<b>Dil : </b><code>' +
                     mov_language[0] + '</code>\n<b>Yönetmen : </b><code>' +
                     director + '</code>\n<b>Yazar : </b><code>' + writer +
                     '</code>\n<b>Yıldızlar : </b><code>' + stars +
                     '</code>\n<b>IMDB Url : </b>' + mov_link +
                     '\n<b>Konusu : </b>' + story_line,
                     link_preview=True,
                     parse_mode='HTML')
    except IndexError:
        await e.edit("Geçerli bir film ismi gir.")

@sedenify(outgoing=True, pattern=r"^.trt")
async def translateme(trans):
    """ .trt komutu verilen metni Google Çeviri kullanarak çevirir. """
    translator = Translator()
    textx = await trans.get_reply_message()
    message = extract_args(trans)
    if message:
        pass
    elif textx:
        message = textx.text
    else:
        await trans.edit("`Bana çevirilecek bir metin wer!`")
        return

    try:
        reply_text = translator.translate(deEmojify(message), dest=TRT_LANG)
    except ValueError:
        await trans.edit("Ayarlanan hedef dil geçersiz.")
        return

    source_lan = LANGUAGES[f'{reply_text.src.lower()}']
    transl_lan = LANGUAGES[f'{reply_text.dest.lower()}']
    reply_text = f"Şu dilden: **{source_lan.title()}**\nŞu dile: **{transl_lan.title()}:**\n\n{reply_text.text}"

    await trans.edit(reply_text)
    if BOTLOG:
        await trans.client.send_message(
            BOTLOG_CHATID,
            f"Birkaç {source_lan.title()} kelime az önce {transl_lan.title()} diline çevirildi.",
        )

@sedenify(pattern="^.lang", outgoing=True)
async def lang(value):
    """ .lang komutu birkaç modül için varsayılan dili değiştirir. """
    arr = extract_args(value).split(' ', 1)
    util = arr[0].lower()
    arg = arr[1].lower()
    if util == "trt":
        scraper = "Translator"
        global TRT_LANG
        if arg in LANGUAGES:
            TRT_LANG = arg
            LANG = LANGUAGES[arg]
        else:
            await value.edit(
                f"`Geçersiz dil kodu!`\n`Geçerli dil kodları`:\n\n`{LANGUAGES}`"
            )
            return
    elif util == "tts":
        scraper = "Yazıdan Sese"
        global TTS_LANG
        if arg in tts_langs():
            TTS_LANG = arg
            LANG = tts_langs()[arg]
        else:
            await value.edit(
                f"`Geçersiz dil kodu!`\n`Geçerli dil kodları`:\n\n`{LANGUAGES}`"
            )
            return
    await value.edit(f"`{scraper} modülü için varsayılan dil {LANG.title()} diline çevirildi.`")
    if BOTLOG:
        await value.client.send_message(
            BOTLOG_CHATID,
            f"`{scraper} modülü için varsayılan dil {LANG.title()} diline çevirildi.`")

@sedenify(outgoing=True, pattern="^.yt")
async def yt_search(video_q):
    """ .yt komutu YouTube üzerinde arama yapar. """
    query = extract_args(video_q)
    result = ''

    if not YOUTUBE_API_KEY:
        await video_q.edit(
            "`Hata: YouTube API anahtarı tanımlanmamış!`"
        )
        return

    await video_q.edit("```İşleniyor...```")

    full_response = await youtube_search(query)
    videos_json = full_response[1]

    for video in videos_json:
        title = f"{unescape(video['snippet']['title'])}"
        link = f"https://youtu.be/{video['id']['videoId']}"
        result += f"{title}\n{link}\n\n"

    reply_text = f"**Arama Sorgusu:**\n`{query}`\n\n**Sonuçlar:**\n\n{result}"

    await video_q.edit(reply_text)


async def youtube_search(query,
                         order="relevance",
                         token=None,
                         location=None,
                         location_radius=None):
    """ Bir YouTube araması yap. """
    youtube = build('youtube',
                    'v3',
                    developerKey=YOUTUBE_API_KEY,
                    cache_discovery=False)
    search_response = youtube.search().list(
        q=query,
        type="video",
        pageToken=token,
        order=order,
        part="id,snippet",
        maxResults=10,
        location=location,
        locationRadius=location_radius).execute()

    videos = []

    for search_result in search_response.get("items", []):
        if search_result["id"]["kind"] == "youtube#video":
            videos.append(search_result)
    try:
        nexttok = search_response["nextPageToken"]
        return (nexttok, videos)
    except HttpError:
        nexttok = "last_page"
        return (nexttok, videos)
    except KeyError:
        nexttok = "API anahtarı hatası, lütfen yeniden dene."
        return (nexttok, videos)

@sedenify(outgoing=True, pattern=r"^.rip")
async def download_video(v_url):
    """ .rip komutu ile YouTube ve birkaç farklı siteden medya çekebilirsin. """
    arr = v_url.text.split(' ', 1)
    arr[0] = arr[0][4:].lower()
    if len(arr) < 2 or arr[0] not in ['audio','video']:
        await v_url.edit("`Komut kullanımı hatalı.`")
        return
    url = arr[1]
    type = arr[0]

    await v_url.edit("`İndirmeye hazırlanıyor...`")

    if type == "audio":
        opts = {
            'format':
            'bestaudio',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'writethumbnail':
            True,
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '320',
            }],
            'outtmpl':
            '%(id)s.mp3',
            'quiet':
            True,
            'logtostderr':
            False
        }
        video = False
        song = True

    elif type == "video":
        opts = {
            'format':
            'best',
            'addmetadata':
            True,
            'key':
            'FFmpegMetadata',
            'prefer_ffmpeg':
            True,
            'geo_bypass':
            True,
            'nocheckcertificate':
            True,
            'postprocessors': [{
                'key': 'FFmpegVideoConvertor',
                'preferedformat': 'mp4'
            }],
            'outtmpl':
            '%(id)s.mp4',
            'logtostderr':
            False,
            'quiet':
            True
        }
        song = False
        video = True

    try:
        await v_url.edit("`Veri çekiliyor, lütfen bekleyin...`")
        with YoutubeDL(opts) as rip:
            rip_data = rip.extract_info(url)
    except DownloadError as DE:
        await v_url.edit(f"`{str(DE)}`")
        return
    except ContentTooShortError:
        await v_url.edit("`İndirilecek içerik fazla kısa.`")
        return
    except GeoRestrictedError:
        await v_url.edit(
            "`Maalesef coğrafi kısıtlamalar sebebiyle bu videoyla işlem yapamazsın.`")
        return
    except MaxDownloadsReached:
        await v_url.edit("`Maksimum indirme limitini aştın.`")
        return
    except PostProcessingError:
        await v_url.edit("`İstek işlenirken bir hata oluştu.`")
        return
    except UnavailableVideoError:
        await v_url.edit("`Medya belirtilen dosya formatında mevcut değil.`")
        return
    except XAttrMetadataError as XAME:
        await v_url.edit(f"`{XAME.code}: {XAME.msg}\n{XAME.reason}`")
        return
    except ExtractorError:
        await v_url.edit("`Bilgi çıkarılırken bir hata gerçekleşti.`")
        return
    except Exception as e:
        await v_url.edit(f"{str(type(e)): {str(e)}}")
        return
    c_time = time.time()
    if song:
        await v_url.edit(f"`Şarkı yüklenmeye hazırlanıyor:`\
        \n**{rip_data['title']}**\
        \nby *{rip_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp3",
            supports_streaming=True,
            attributes=[
                DocumentAttributeAudio(duration=int(rip_data['duration']),
                                       title=str(rip_data['title']),
                                       performer=str(rip_data['uploader']))
            ],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Karşıya yükleniyor...",
                         f"{rip_data['title']}.mp3")))
        os.remove(f"{rip_data['id']}.mp3")
        await v_url.delete()
    elif video:
        await v_url.edit(f"`Şarkı yüklenmeye hazırlanıyor:`\
        \n**{rip_data['title']}**\
        \nby *{rip_data['uploader']}*")
        await v_url.client.send_file(
            v_url.chat_id,
            f"{rip_data['id']}.mp4",
            supports_streaming=True,
            caption=rip_data['title'],
            progress_callback=lambda d, t: asyncio.get_event_loop(
            ).create_task(
                progress(d, t, v_url, c_time, "Karşıya yükleniyor...",
                         f"{rip_data['title']}.mp4")))
        os.remove(f"{rip_data['id']}.mp4")
        await v_url.delete()

def deEmojify(inputString):
    """ Emojileri ve diğer güvenli olmayan karakterleri metinden kaldırır. """
    return get_emoji_regexp().sub(u'', inputString)

CMD_HELP.update({
    'img':
    '.img <kelime>\
        \nKullanım: Google üzerinde hızlı bir resim araması yapar ve ilk 5 resmi gösterir.'
})
CMD_HELP.update({
    'currency':
    '.currency <miktar> <dönüştürülecek birim> <dönüşecek birim>\
        \nKullanım: Yusufun Türk Lirası Botu gibi, ama boş kaldığında kızlara yazmıyor.'
})
CMD_HELP.update({
    'carbon':
    '.carbon <metin>\
        \nKullanım: carbon.now.sh sitesini kullanarak yazdıklarının aşşşşşşırı şekil görünmesini sağlar.\n.crblang <dil> komutuyla varsayılan dilini ayarlayabilirsin.'
})
CMD_HELP.update(
    {'google': '.google <kelime>\
        \nKullanım: Hızlı bir Google araması yapar.'})
CMD_HELP.update(
    {'wiki': '.wiki <terim>\
        \nKullanım: Bir Vikipedi araması gerçekleştirir.'})
CMD_HELP.update(
    {'ud': '.ud <terim>\
        \nKullanım: Urban Dictionary araması yapmanın kolay yolu?'})
CMD_HELP.update({
    'tts':
    '.tts <metin>\
        \nKullanım: Metni sese dönüştürür.\n.lang tts komutuyla varsayılan dili ayarlayabilirsin. (Türkçe ayarlı geliyor merak etme.)'
})
CMD_HELP.update({
    'trt':
    '.trt <metin>\
        \nKullanım: Basit bir çeviri modülü.\n.lang trt komutuyla varsayılan dili ayarlayabilirsin. (Türkçe ayarlı geliyor merak etme.)'
})
CMD_HELP.update({'yt': '.yt <metin>\
        \nKullanım: YouTube üzerinde bir arama yapar.'})
CMD_HELP.update(
    {"imdb": ".imdb <film>\nKullanım: Film hakkında bilgi verir."})
CMD_HELP.update({
    'rip':
    '.ripaudio <bağlantı> veya .ripvideo <bağlantı>\
        \nKullanım: YouTube üzerinden (veya [başka sitelerden](https://ytdl-org.github.io/youtube-dl/supportedsites.html)) video veya ses indirir.'
})
