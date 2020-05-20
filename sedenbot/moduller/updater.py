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
# Credits: @NaytSeyd (for fix errors)
#
# Bu modül commit sayısına bağlı olarak botu günceller.
#

import sys
from os import execl, remove, path
import heroku3

from git import Repo
from git.exc import GitCommandError, InvalidGitRepositoryError, NoSuchPathError

from sedenbot import CMD_HELP, HEROKU_APIKEY, HEROKU_APPNAME, STRING_SESSION
from sedenbot.events import sedenify

async def gen_chlog(repo, diff):
    ch_log = ''
    d_form = "%d/%m/%y"
    for c in repo.iter_commits(diff):
        ch_log += f'•[{c.committed_datetime.strftime(d_form)}]: {c.summary} <{c.author}>\n'
    return ch_log

async def is_off_br(br):
    off_br = ['seden']
    if br in off_br:
        return 1
    return

@sedenify(outgoing=True, pattern="^.update(?: |$)(.*)")
async def upstream(ups):
    ".update komutu ile botunun güncel olup olmadığını denetleyebilirsin."
    await ups.edit("`Güncellemeler denetleniyor...`")
    conf = ups.pattern_match.group(1)
    off_repo = 'https://github.com/TeamDerUntergang/Telegram-UserBot.git'

    try:
        txt = "``Güncelleme başarısız oldu! "
        txt += "Bazı sorunlarla karşılaştık.`\n\n**LOG:**\n"
        repo = Repo()
    except NoSuchPathError as error:
        await ups.edit(f'{txt}\n`{error} klasörü bulunamadı.`')
        return
    except InvalidGitRepositoryError as error:
        await ups.edit(f"`{error} klasörü bir git reposu gibi görünmüyor.\
            \nFakat bu sorunu .update now komutuyla botu zorla güncelleyerek çözebilirsin.`")
        return
    except GitCommandError as error:
        await ups.edit(f'{txt}\n`Git hatası! {error}`')
        return

    ac_br = repo.active_branch.name
    if not await is_off_br(ac_br):
        await ups.edit(
            f'**[Güncelleyici]:**` Galiba seden botunu modifiye ettin ve kendi branşını kullanıyorsun: ({ac_br}). '
            'Bu durum güncelleyicinin kafasını karıştırıyor,'
            'Güncelleme nereden çekilecek?'
            'Lütfen seden botunu resmi repodan kullan.`')
        return

    try:
        repo.create_remote('upstream', off_repo)
    except BaseException:
        pass

    ups_rem = repo.remote('upstream')
    ups_rem.fetch(ac_br)
    changelog = await gen_chlog(repo, f'HEAD..upstream/{ac_br}')

    if not changelog:
        await ups.edit(f'\n`Botun` **tamamen güncel!** `Branch:` **{ac_br}**\n')
        return

    if conf != "now":
        changelog_str = f'**{ac_br} için yeni güncelleme mevcut!\n\nDeğişiklikler:**\n`{changelog}`'
        if len(changelog_str) > 4096:
            await ups.edit("`Değişiklik listesi çok büyük, dosya olarak görüntülemelisin.`")
            file = open("degisiklikler.txt", "w+")
            file.write(changelog_str)
            file.close()
            await ups.client.send_file(
                ups.chat_id,
                "degisiklikler.txt",
                reply_to=ups.id,
            )
            remove("degisiklikler.txt")
        else:
            await ups.edit(changelog_str)
        await ups.respond('`Güncellemeyi yapmak için \".update now\" komutunu kullan.`')
        return

    await ups.edit('`Bot güncelleştiriliyor...`')

    ups_rem.fetch(ac_br)
    repo.git.reset('--hard', 'seden')

    if HEROKU_APIKEY != None:
        heroku = heroku3.from_key(HEROKU_APIKEY)
        if HEROKU_APPNAME != None:
            try:
                heroku_app = heroku.apps()[HEROKU_APPNAME]
            except KeyError:
                await ups.edit(
                    "```HATA: HEROKU_APPNAME değişkeni hatalı! Lütfen uygulama adınızın "
                    "HEROKU_APIKEY ile doğru olduğundan emin olun.```")
                return
        else:
            await ups.edit(
                "```HATA: HEROKU_APPNAME değişkeni ayarlanmadı! Lütfen "
                "Heroku uygulama adınızı değişkene girin.```")
            return

        await ups.edit(
            "`Heroku yapılandırması bulundu! Güncelleyici Seden'i güncellemeye ve yeniden başlatmaya çalışacak."
            " Bu işlem otomatik olacaktır. İşlem bitince Seden'in çalışıp çalışmadığını kontrol etmeyi deneyin.\n"
            "\".alive\" komutu ile deneyebilirsin.`\n"
            "**BOT YENIDEN BAŞLATILIYOR..**")
        if not STRING_SESSION:
            repo.git.add('sedenbot.session', force=True)
        if path.isfile('config.env'):
            repo.git.add('config.env', force=True)
        
        repo.git.checkout("seden")
        
        repo.config_writer().set_value("user", "name",
                                       "SedenBot Updater").release()
        repo.config_writer().set_value("user", "email",
                                       "<>").release()
        repo.git.pull()
        heroku_remote_url = heroku_app.git_url.replace(
            "https://", f"https://api:{HEROKU_APIKEY}@")

        remote = None
        if 'heroku' in repo.remotes:
            remote = repo.remote('heroku')
            remote.set_url(heroku_remote_url)
        else:
            remote = repo.create_remote('heroku', heroku_remote_url)

        try:
            remote.push(refspec="HEAD:refs/heads/seden", force=True)
        except GitCommandError as e:
            await ups.edit(f'{txt}\n`Git hatası! {e}`')
            return
    else:
        await ups.edit(
            '`Güncelleme başarıyla tamamlandı!\n'
            'Seden yeniden başlatılıyor... Lütfen biraz bekleyin, ardından '
            '".alive" komutunu kullanarak SedenBotun çalışıp çalışmadığnıı kontrol edin.`')

        await ups.client.disconnect()
    execl(sys.executable, sys.executable, *sys.argv)

CMD_HELP.update({
    'update':
    ".update\
\nKullanım: Botunuza siz kurduktan sonra herhangi bir güncelleme gelip gelmediğini kontrol eder.\
\n\n.update now\
\nKullanım: Botunuzu günceller."
})
