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

""" Hash ve encode/decode çözme komutlarını içeren UserBot modülü. """

import pybase64

from subprocess import PIPE
from subprocess import run as runapp

from sedenbot import CMD_HELP
from sedenbot.events import extract_args, sedenify

@sedenify(outgoing=True, pattern="^.hash")
async def gethash(hash_q):
    """ .hash komutu md5, sha1, sha256, sha512 dizelerini bulur. """
    hashtxt_ = extract_args(hash_q)
    if len(hashtxt_) < 1:
        await hash_q.edit("`Komutun yanına bir metin yazın.`")
        return
    hashtxt = open("hashdis.txt", "w+")
    hashtxt.write(hashtxt_)
    hashtxt.close()
    md5 = runapp(["md5sum", "hashdis.txt"], stdout=PIPE)
    md5 = md5.stdout.decode()
    sha1 = runapp(["sha1sum", "hashdis.txt"], stdout=PIPE)
    sha1 = sha1.stdout.decode()
    sha256 = runapp(["sha256sum", "hashdis.txt"], stdout=PIPE)
    sha256 = sha256.stdout.decode()
    sha512 = runapp(["sha512sum", "hashdis.txt"], stdout=PIPE)
    runapp(["rm", "hashdis.txt"], stdout=PIPE)
    sha512 = sha512.stdout.decode()
    
    def rem_filename(st):
        return st[:st.find(' ')]
    
    ans = (f"Text: `{hashtxt_}`"
           f"\nMD5: `{rem_filename(md5)}`"
           f"\nSHA1: `{rem_filename(sha1)}`"
           f"\nSHA256: `{rem_filename(sha256)}`"
           f"\nSHA512: `{rem_filename(sha512)}`")
    if len(ans) > 4096:
        hashfile = open("hashes.txt", "w+")
        hashfile.write(ans)
        hashfile.close()
        await hash_q.client.send_file(
            hash_q.chat_id,
            "hashes.txt",
            reply_to=hash_q.id,
            caption="`Çok büyük, bunun yerine bir metin dosyası gönderiliyor. `")
        runapp(["rm", "hashes.txt"], stdout=PIPE)
        hash_q.delete()
    else:
        await hash_q.edit(ans)

@sedenify(outgoing=True, pattern="^.base64")
async def endecrypt(query):
    """ .base64 komutu verilen dizenin base64 kodlamasını bulur. """
    argv = extract_args(query)
    args = argv.split(' ', 1)
    if len(args) < 2 or args[0] not in ['en','de']:
        await query.edit('`Komut kullanımı hatalı.`')
        return
    args[1] = args[1].replace('`','')
    if args[0] == "en":
        lething = str(pybase64.b64encode(bytes(args[1], "utf-8")))[2:]
        await query.edit(f"Input: `{args[1]}`\nEncoded: `{lething[:-1]}`")
    else:
        lething = str(pybase64.b64decode(bytes(args[1], "utf-8")))[2:]
        await query.edit(f"Input: `{args[1]}`\nDecoded: `{lething[:-1]}`")

CMD_HELP.update({"base64": "Verilen dizenin base64 kodlamasını bulun"})

CMD_HELP.update({
    "hash":
    "Bir txt dosyası yazıldığında md5, sha1, sha256, sha512 dizelerini bulun."
})
