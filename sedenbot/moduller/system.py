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

""" Sunucu hakkında bilgi veren UserBot modülüdür. """

from asyncio import create_subprocess_shell as asyncrunapp
from asyncio.subprocess import PIPE as asyncPIPE
from shutil import which
from os import remove

from sedenbot.moduller.lovers import saniye
from sedenbot.moduller.ecem import ecem
from sedenbot import CMD_HELP, ALIVE_MESAJI
from sedenbot.events import extract_args, sedenify
# ================= CONSTANT =================
KULLANICIMESAJI = ALIVE_MESAJI
# ============================================
@sedenify(outgoing=True, pattern="^.neofetch$")
async def sysdetails(sysd):
    """ .neofetch komutu neofetch kullanarak sistem bilgisini gösterir. """
    try:
        neo = "neofetch --stdout"
        fetch = await asyncrunapp(
            neo,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await fetch.communicate()
        result = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await sysd.edit("`" + result + "`")
    except FileNotFoundError:
        await sysd.edit("`Öncelikle neofetch modülünü yükleyin !!`")

@sedenify(outgoing=True, pattern="^.botver$")
async def bot_ver(event):
    """ .botver komutu bot versiyonunu gösterir. """
    if which("git") :
        invokever = "git describe --all --long"
        ver = await asyncrunapp(
            invokever,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await ver.communicate()
        verout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        invokerev = "git rev-list --all --count"
        rev = await asyncrunapp(
            invokerev,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )
        stdout, stderr = await rev.communicate()
        revout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        await event.edit("[Seden UserBot](https://telegram.dog/SedenUserBot) `Versiyonu: "
                         f"{verout} v3.5 EOL"
                         "` \n"
                         "`Toplam değişiklik: "
                         f"{revout}"
                         "`")
    else:
        await event.edit(
            "Bu arada Seden seni çok seviyor. ❤"
        )

@sedenify(outgoing=True, pattern="^.pip")
async def pipcheck(pip):
    """ .pip komutu python-pip araması yapar. """
    pipmodule = extract_args(pip)
    if len(pipmodule) > 0:
        await pip.edit("`Aranıyor . . .`")
        invokepip = f"pip3 search {pipmodule}"
        pipc = await asyncrunapp(
            invokepip,
            stdout=asyncPIPE,
            stderr=asyncPIPE,
        )

        stdout, stderr = await pipc.communicate()
        pipout = str(stdout.decode().strip()) \
            + str(stderr.decode().strip())

        if pipout:
            if len(pipout) > 4096:
                await pip.edit("`Çıktı çok büyük, dosya olarak gönderiliyor.`")
                file = open("output.txt", "w+")
                file.write(pipout)
                file.close()
                await pip.client.send_file(
                    pip.chat_id,
                    "output.txt",
                    reply_to=pip.id,
                )
                remove("output.txt")
                return
            await pip.edit("**Sorgu: **\n`"
                           f"{invokepip}"
                           "`\n**Sonuç: **\n`"
                           f"{pipout}"
                           "`")
        else:
            await pip.edit("**Sorgu: **\n`"
                           f"{invokepip}"
                           "`\n**Sonuç: **\n`Bir şey bulunamadı.`")
    else:
        await pip.edit("`Bir örnek görmek için .seden pip komutunu kullanın.`")

@sedenify(outgoing=True, pattern="^.alive$")
async def amialive(alive):
    if KULLANICIMESAJI.lower() == 'ecem':
        await ecem(alive)
        return
    elif KULLANICIMESAJI.lower() == 'saniye':
        await saniye(alive)
        return
    await alive.edit(f"`{KULLANICIMESAJI}`")
        
@sedenify(outgoing=True, pattern="^.alives")
async def alivename(kullanici):
    message = extract_args(kullanici)
    output = 'Kullanım: .alives <alive mesajı>'
    if len(message) > 0:
        global KULLANICIMESAJI
        KULLANICIMESAJI = message
        output = f'Alive mesajı, {KULLANICIMESAJI} olarak ayarlandı!'
    await kullanici.edit("`" f"{output}" "`")
    
@sedenify(outgoing=True, pattern="^.resalive$")
async def alivereset(kullanicireset):
    global KULLANICIMESAJI
    KULLANICIMESAJI = str(ALIVE_MESAJI) if ALIVE_MESAJI else kullanicireset().node
    await kullanicireset.edit("`Alive mesajı başarıyla sıfırlandı!`")

CMD_HELP.update(
    {"neofetch": ".neofetch\
    \nKullanım: Neofetch komutunu kullanarak sistem bilgisi gösterir."})
CMD_HELP.update({"botver": ".botver\
    \nKullanım: UserBot sürümünü gösterir."})
CMD_HELP.update(
    {"pip": ".pip <modül ismi>\
    \nKullanım: Pip modüllerinde arama yapar."})
CMD_HELP.update({
    "alive": ".alive\
    \nKullanım: Seden botunun çalışıp çalışmadığını kontrol etmek için kullanılır.\
    \n\n.alives <alive mesajı>\
    \nKullanım: Bu komut Seden botun alive mesajını değiştirmenize yarar.\
    \n\n.resalive\
    \nKullanım: Bu komut ayarladığınız alive mesajını varsayılan Seden olan haline döndürür."
})
