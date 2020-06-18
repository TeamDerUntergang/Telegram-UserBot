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

""" Telegram'dan kod ve terminal komutlarını yürütmek için UserBot modülü. """

from asyncio import create_subprocess_shell
from asyncio.subprocess import PIPE

from getpass import getuser
from os import remove
from sys import executable

from sedenbot import CMD_HELP, BOTLOG, BOTLOG_CHATID
from sedenbot.events import extract_args, sedenify
import ast
import operator as op

@sedenify(outgoing=True, pattern="^.eval")
async def evaluate(query):
    """ .eval komutu verilen Python ifadesini değerlendirir. """
    args = extract_args(query)
    if len(args) < 1:
        await query.edit("``` Değerlendirmek için bir ifade verin. ```")
        return

    try:
        evaluation = safe_eval(args)
        if evaluation:
            if isinstance(evaluation, str):
                if len(evaluation) >= 4096:
                    file = open("output.txt", "w+")
                    file.write(evaluation)
                    file.close()
                    await query.client.send_file(
                        query.chat_id,
                        "output.txt",
                        reply_to=query.id,
                        caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
                    )
                    remove("output.txt")
                    return
                await query.edit("**Sorgu: **\n`"
                                 f"{args}"
                                 "`\n**Sonuç: **\n`"
                                 f"{evaluation}"
                                 "`")
        else:
            await query.edit("**Sorgu: **\n`"
                             f"{args}"
                             "`\n**Sonuç: **\n`Sonuç döndürülemedi / Yanlış`")
    except Exception as err:
        await query.edit("**Sorgu: **\n`"
                         f"{args}"
                         "`\n**İstisna: **\n"
                         f"`{err}`")

    if BOTLOG:
        await query.client.send_message(
            BOTLOG_CHATID,
            f"Eval sorgusu {args} başarıyla yürütüldü")

@sedenify(outgoing=True, pattern="^.term")
async def terminal_runner(term):
    """ .term komutu sunucunuzda bash komutlarını ve komut dosyalarını çalıştırır. """
    curruser = getuser()
    command = extract_args(term)
    try:
        from os import geteuid
        uid = geteuid()
    except ImportError:
        uid = "Bu değil şef!"

    if term.is_channel and not term.is_group:
        await term.edit("`Term komutlarına kanallarda izin verilmiyor`")
        return

    if not command:
        await term.edit("``` Yardım almak için .seden term yazarak \
            örneğe bakabilirsin.```")
        return

    if command in ("sedenbot.session", "config.env"):
        await term.edit("`Bu tehlikeli bir operasyon! İzin verilemedi!`")
        return

    process = await create_subprocess_shell(
        command,
        stdout=PIPE,
        stderr=PIPE)
    stdout, stderr = await process.communicate()
    result = str(stdout.decode().strip()) \
        + str(stderr.decode().strip())

    if len(result) > 4096:
        output = open("output.txt", "w+")
        output.write(result)
        output.close()
        await term.client.send_file(
            term.chat_id,
            "output.txt",
            reply_to=term.id,
            caption="`Çıktı çok büyük, dosya olarak gönderiliyor`",
        )
        remove("output.txt")
        return

    if uid == 0:
        await term.edit("`" f"{curruser}:~# {command}" f"\n{result}" "`")
    else:
        await term.edit("`" f"{curruser}:~$ {command}" f"\n{result}" "`")

    if BOTLOG:
        await term.client.send_message(
            BOTLOG_CHATID,
            "Terminal Komutu " + command + " başarıyla yürütüldü",
        )

operators = {ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
			ast.Div: op.truediv, ast.Pow: op.pow, ast.BitXor: op.xor,
			ast.USub: op.neg}

def safe_eval(expr):
    expr = expr.lower().replace("x","*").replace(" ","")
    return str(_eval(ast.parse(expr, mode='eval').body))

def _eval(node):
    if isinstance(node, ast.Num):
        return node.n
    elif isinstance(node, ast.BinOp):
        return operators[type(node.op)](_eval(node.left), _eval(node.right))
    elif isinstance(node, ast.UnaryOp):
        return operators[type(node.op)](_eval(node.operand))
    else:
        raise TypeError("Bu güvenli bir eval sorgusu olmayabilir.")

CMD_HELP.update({"eval": ".eval 2 + 3\nKullanım: Mini ifadeleri değerlendirin."})
CMD_HELP.update(
    {"term": ".term ls\nKullanım: Sunucunuzda bash komutlarını ve komut dosyalarını çalıştırın."})
