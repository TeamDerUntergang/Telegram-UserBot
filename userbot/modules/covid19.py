# Copyright (C) 2019 The Raphielscape Company LLC.
# Copyright (C) 2020 TeamDerUntergang.
#
# Licensed under the Raphielscape Public License, Version 1.c (the "License");
# you may not use this file except in compliance with the License.
#

# @NaytSeyd tarafından portlanmıştır.

from covid import Covid
from userbot import CMD_HELP, bot
from userbot.events import register


@register(outgoing=True, pattern="^.covid (.*)")
async def covid(event):
    covid = Covid()
    data = covid.get_data()
    country = event.pattern_match.group(1)
    country_data = get_country_data(country, data)
    output_text = "" 
    for name, value in country_data.items():
        output_text += "`{}`: `{}`\n".format(str(name), str(value))
    await event.edit("**{} Ülkesi için Covid 19 İstatistikleri**:\n\n{}".format(country.capitalize(), output_text))

def get_country_data(country, world):
    for country_data in world:
        if country_data["country"].lower() == country.lower():
            return country_data
    return {"Bu ülke hakkında henüz bilgi yok!"}
    
    
CMD_HELP.update({
        "covid19": 
        ".covid <ülkeismi> \
        \n**Kullanım**: Belirtilen ülke için Covid 19 İstatistikleri. \
        \n**Örnek: .covid Turkey**"
    })
