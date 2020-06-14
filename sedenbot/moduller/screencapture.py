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

from io import BytesIO

from base64 import b64decode
from re import match
from selenium.webdriver import Chrome
from asyncio import sleep
from selenium.webdriver.chrome.options import Options
from os.path import exists

from sedenbot import CHROME_DRIVER, CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(pattern=r"^.ss", outgoing=True)
async def capture(url):
    """ .ss komutu, belirttiğin herhangi bir siteden ekran görüntüsü alır ve sohbete gönderir. """
    await url.edit("`İşleniyor...`")
    input_str = extract_args(url)
    link_match = match(r'\bhttp(.*)?://.*\.\S+', input_str)
    if link_match:
        link = link_match.group()
    else:
        await url.edit("`Ekran görüntüsü alabilmem için geçerli bir bağlantı vermelisin.`")
        return
    chrome_options = Options()
    CHROME_BINARY = "/usr/bin/chromium-browser"
    if exists("/usr/bin/chromium"):
        CHROME_BINARY = "/usr/bin/chromium"
    chrome_options.add_argument("--headless")
    chrome_options.binary_location = CHROME_BINARY
    chrome_options.add_argument("--window-size=1920x1080")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")
    driver = Chrome(executable_path=CHROME_DRIVER, options=chrome_options)
    driver.get(link)
    height = driver.execute_script(
        "return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);"
    )
    width = driver.execute_script(
        "return Math.max(document.body.scrollWidth, document.body.offsetWidth, document.documentElement.clientWidth, document.documentElement.scrollWidth, document.documentElement.offsetWidth);"
    )
    driver.set_window_size(width + 125, height + 125)
    wait_for = int(height / 1000)
    await url.edit(f"`Sayfanın ekran görüntüsü oluşturuluyor...`\
    \n`Sayfanın yüksekliği: {height} piksel`\
    \n`Sayfanın genişliği: {width} piksel`\
    \n`Sayfanın yüklenmesi için {wait_for} saniye beklendi.`")
    await sleep(wait_for)
    im_png = driver.get_screenshot_as_base64()
    # Sayfanın ekran görüntüsü kaydedilir.
    driver.close()
    message_id = url.message.id
    if url.reply_to_msg_id:
        message_id = url.reply_to_msg_id
    with BytesIO(b64decode(im_png)) as out_file:
        out_file.name = "ekran_goruntusu.png"
        await url.edit("`Ekran görüntüsü karşıya yükleniyor...`")
        await url.client.send_file(url.chat_id,
                                   out_file,
                                   caption=input_str,
                                   force_document=True,
                                   reply_to=message_id)

CMD_HELP.update({
    "ss":
    ".ss <url>\
    \nKullanım: Belirtilen web sitesinden bir ekran görüntüsü alır ve gönderir.\
    \nGeçerli bir site bağlantısı örneği: `https://devotag.com`"
})
