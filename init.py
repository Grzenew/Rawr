# ⚪️ Standard lib
import os
import random
from sys import api_version
from dotenv import load_dotenv

# ⚪️ Third party
import asyncio
import discord

# Internal
from api import apiCall
from scraper import scrapeCall



# 🔴 Settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN') # authentication token is stored in .env file locally
POST_STARFALL_QUOTES = [
    'Bestworldx has no mana for DI! ☄️☄️☄️',
    'Dcarl has no SIMBOLS DE DIVINIDAD! ☄️☄️☄️',
    (
        'DI from Breg misses ☄️☄️☄️, '
        'DI from Ebe is super effective! 🌜🦉🌛'
    ),
]


# 🟢 Exec
client = discord.Client()

# send print after bot init
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

# send to new users joining the server
#@client.event
#async def on_member_join(member):
#    await member.create_dm()
#    await member.dm_channel.send(
#        f'Hi {member.name}, gib me strudels!'
#    )

# if user writes "tomb", then bot asks given dude for :sindra: reaction. If user gives it, then bot responds with random "belly/head" OR "Wipe" if 60 secs pass w/o any action
# if someone writes "Starfall", a random str gets printed by the bot
@client.event
async def on_message(message):

    # avoid endless loop in case bot said its own trigger word
    if message.author == client.user:
        return

    # tomb keyword
    elif message.content.startswith('tomb'):
        channel = message.channel
        await channel.send('Send me that <:sindra:853223712702201858> reaction, %s!' % message.author.name)

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '<:sindra:853223712702201858>'

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=10.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('{} has wiped on Sindy.'.format(message.author.name))
        else:
            await channel.send(random.choice(["Belly!", "Head!"]))

    # Starfall keyword
    if message.content == 'Starfall':
        response = random.choice(POST_STARFALL_QUOTES)
        await message.channel.send(response)

    # !old who keyword
    """if message.content.startswith('!who '):
        query = message.content.split()[-1].capitalize()  # get the last word of the call - "!who is Andrew"  and "!who Andrew" and "!who the fuck is Andrew" work
        api_response = apiCall("character", query)
        scrape_response = scrapeCall("character", query)
        await message.channel.send(api_response + "\n" + scrape_response)
    """

    # !guild keyword
    if message.content.startswith('!guild '):
        query = message.content.split(" ", 1)[1]  # split by 1 space only, i.e. get everything after the space
        response = apiCall("guild", query)
        await message.channel.send(response)

    # !who keyword
    if message.content.startswith('!who '):
        query = message.content.split()[-1].capitalize()
        api_response = apiCall("character", query)
        scrape_response = scrapeCall("character", query)

        class_icons = { "Mage": '855739857409146880', 
                        "Death Knight": '855748451677634560',
                        "Hunter": '855748451623370762',
                        "Druid": '855748451799138344',
                        "Paladin": '855748451735699456',
                        "Priest": '855748451782230026',
                        "Rogue": '579532030086217748',
                        "Shaman": '855748451643031553',
                        "Warlock": '855748451672260608',
                        "Warrior": '855748451644211200' }

        title = query + " (" + api_response["level"] + ")"
        description = api_response["guild"] + " • " + api_response["specs"]

        embedVar = discord.Embed(title=title, description=description, url='http://armory.warmane.com/character/{nick}/Lordaeron/achievements'.format(nick=query), color=0xdab022)
        if int(scrape_response["ICC10"]["score_nm"]) > 0:
            embedVar.add_field(name="ICC10", value=scrape_response["ICC10"]["score_nm"] + "/12")
        if int(scrape_response["ICC25"]["score_nm"]) > 0:
            embedVar.add_field(name="ICC25", value=scrape_response["ICC25"]["score_nm"] + "/12", inline=True)
        if int(scrape_response["ICC10"]["score_hc"]) > 0:
            embedVar.add_field(name="ICC10 Heroic", value=scrape_response["ICC10"]["score_hc"] + "/12", inline=True)
        if int(scrape_response["ICC25"]["score_hc"]) > 0:
            embedVar.add_field(name="ICC25 Heroic", value=scrape_response["ICC25"]["score_hc"] + "/12", inline=True)
        embedVar.set_thumbnail(url='https://cdn.discordapp.com/emojis/{class_icon_id}.png'.format(class_icon_id=class_icons[api_response["class"]]))
        await message.channel.send(embed=embedVar)


client.run(TOKEN)
