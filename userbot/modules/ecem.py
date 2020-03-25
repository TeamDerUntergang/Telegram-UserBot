# Copyright (C) 2020 TeamDerUntergang
#
# Licensed under the TeamDerUntergang Public License;
# you may not use this file except in compliance with the License.
""" Ecem module for having some fun with people. """
""" Made love by Sedenogen """
""" Powered by NaytSeyd """

from asyncio import sleep
from random import choice, getrandbits, randint
from re import sub
import time

from collections import deque

import requests

from userbot import CMD_HELP
from userbot.events import register
from userbot.modules.admin import get_user_from_event

# ================= CONSTANT =================
ECEM_STRINGS = [
    "Çocukluk aşkımsın"
    "Erkek arkadaşlarımın arkadaşlarının adlarını bilmem normal bir şey.",
    "Şu an acele işim var, daha sonra çekilsek olmaz mı? Zaten yine geleceğim.",
    "Yok, kızmadım.",
    "Bunun farkına vardıysan benim için artık problem yok.",
    "Bundan sonra artık hayatında Ecem diye biri yok!",
    "Yağmurlu havada sweatini veren arkadaşlarınız olsun. :p",
    "Yalnız çiçek açar mısın? Yalnız, çiçek.",
    "Affetmiyorum, annemi çağıracağım. O gereğini yapacak.",
    "Saçımla oynama.",
    "Saçımla oynamamanı söylediğim halde oynuyorsun. Arkamdan git lütfen.",
    "Ben gelmiyorum bedene falan, kenarda ölmeyi bekleyeceğim.",
    "Düşman değiliz, sadece onun olduğu yerde rahat edemem.",
    "Git arkamdan, istemiyorum seni!",
    "Murat Boz şarkıları beni hiç eğlendirmiyor.",
    "Tövbe tövbe kapatın şunu çarpılacağız.",
    "Üç kızım olsun istiyorum.",
    "Eğer onunla evlenirsem nikah şahidim sen ol.",
    "Ehehehe çok komik, hadi defolun gidin.",
    "Gidip onunla konuşsana?",
    "Ne oldu sana? Anlatmak ister misin?",
    "Lütfen anlat işte. Çok mu özel ki?",
    "Hadi gel erkeklerin yanına geçelim.",
    "İyi misin?",
    "Teşekkür ederim :)))",
    "Daha sonra yine geleceğim, o zaman çekiliriz, olmaz mı?",
    "Grubu dağıtıyoruz gençler.",
    "Grubu dağıtıyoruz gençler??? Ne ara dedim onu ya ben?",
    "Allah belanı vermesin.",
    "Hadi yönetici sensin, dağıt grubu.",
    "İyi akşamlar.",
    "Her şeyi ben söylüyorum, biraz da siz söyleyin.",
    "Ben onu esprisine demiştim diyette değilim.",
    "Sizde var mı bilmiyorum sorim dedim birkaç kişiye daha sordum, çıktı alabilme şansın var mı?",
    "Üçgende çıkmış sorular, 3. site.",
    "Eğer olmadıysa gerek kalmadı.",
    "Yok yani, ben buldum birinden.",
    "Evet evet hallettim ben sağol.",
    "Atim sen de kontrol et bir, o mu diye.",
    "Neyse sen çıkarttığını da getirirsin olmadı.",
    "Kim ne dedi sana?",
    "Onlar benim kardeşim gibi olduğu için sahipleniyorlar.",
    "Kötü bir durum yok.",
    "Bir anda yapınca rahatsız oldum ama sonra sana zaten sorun yok dedim.",
    "Onlar da biliyor, ondan tepki vermiştir.",
    "Sorun yok yani.",
    "Rica ederim.",
    "Teşekkür ederim kusura bakma telefonum bozuktu yeni görebildim :)",
    "Evet. Yalan borcum mu var size? Evet, yalan borcum mu var? Yalan borcum mu var?",
    "Ne malsın ya.",
    "Testleri bitirmeyin Allah aşkına.",
    "Sen mesajı silsen de bildirimde gözüküyor.",
    "O ne demişti ki?",
    "Ben birine bir şey yazmştım, sonra sildim. Ne yazdın dedi, söylemedim. Sonra bildirimden açıp bana yazdı, yazdığım şeyi.",
    "Mzkddkslslldldldldld",
    "Toplu olarak yapıyoruz değil mi, hiç hoş olmayan şeyler çıkmasın sonra.",
    "Lan sen konuşma.",
    "Abi yalan değil ki, yetişmiyor.",
    "Ya hep mi korktuğum başıma gelir ya?",
    "Bende şans olsa zaten.",
    "Ben oyuna falan katılamam.",
    "Tövbe, hep olmaması gereken sınıfları söylüyorsun.",
    "Neyse ben konuşmuyorum sizinle zaten.",
    "Ne uzattınız ya, değişmiş işte.",
    "Sen sus, seninle konuşan yok.",
    "Çok özledim :( ♥️",
    "Saygı, minnet ve özlemle.",
    "Canım, dayım, her şeyim yolun açık olsun askerim ♥️",
    "#NoFilter",
    "Yorgunum ve ağrılar",
    "Sıkıldım ya, konuşun. Söz valla terslemeyeceğim.",
    "Çok kaptırmış kendini o.",
    "Okul mal o zaman, o kadar yanlışla on birinci olduysam.",
    "Kime diyorsunuz, ben bir şey anlamadım.",
    "Sen hani hastaydın Lan",
    "Sen ne diyon ya sksödödödöföfçgçgçhçhş",
    "Hiç bu kadar güldüğümü hatırlamıyorum.",
    "Kaç dakika uğraştın, gerizekalı ya.",
    "Lan sus sende sabahtan beri Ecem Ecem dmdkdmdmdmföfögö",
    "Evde gerizekalı gibi gülüyorum susun artık.",
    "Tövbe yarabbim",
    "Üstüme gitmeyin şu saatlerde benim.",
    "Sakn ol raki",
    "5 saattir anlamaya çalışıyor.",
    "Yeter, gidin yatın.",
    "Sus lan mal",
    "Gahahaha diye gülenin dediğine bak.",
    "Yarın hiç hoş olmayacaksın.",
    "Sinirliyim zaten, uğraşmayın benimle. Sjdkdkkdmfgm",
    "Bu arada yüzümü telefon gözükmesin diye öyle tutmuyordum sebebini bilmiyorum djjd",
    "Doğum günü kızıyım ben şşş. Nasıl bir değişiklik bekliyordunuz dkdkdk",
    "İnternetten baksana",
    "Müzik dersi hangi gün? Hocaya söz vermiştim.",
    "Hem arkamdan kaşar diyorsun, hem de kardeşim diyorsun.",
    "Böyle böyle yürüyor ya ahahahahahahaha",
    "Her an'ımda",
    "bff bff bff forever bff",
    "Yine, yeni, yeniden ♥️",
    "Buraya sığdıramayacağım milyon tane iyi anımız var, hep de olsun.",
    "İyi ki doğdun kız kardeşim, seni çok seviyorum ♥️",
]


@register(outgoing=True, pattern="^.ecem$")
async def ecem(e):
    """ Ecem's dictionary """
    await e.edit(choice(ECEM_STRINGS))
    
    
CMD_HELP.update({
    "ecem":
    ".ecem or reply to someones text with .ecem\
    \nUsage: Ecem quotes."
})
