# coding: utf-8

# ⚪️ Standard lib
import os
import random
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

    # !who keyword
    if message.content.startswith('!who '):
        query = message.content.split()[-1].capitalize()  # get the last word of the call - "!who is Andrew"  and "!who Andrew" and "!who the fuck is Andrew" work
        api_response = apiCall("character", query)
        scrape_response = scrapeCall("character", query)
        await message.channel.send(api_response + "\n" + scrape_response)

    # !guild keyword
    if message.content.startswith('!guild '):
        query = message.content.split(" ", 1)[1]  # split by 1 space only, i.e. get everything after the space
        response = apiCall("guild", query)
        await message.channel.send(response)

    # !sexy keyword
    # WIP
    if message.content.startswith('!sexy '):
        embedVar = discord.Embed(title="Gotfai", description="His staff is longer than his height.", uel='http://armory.warmane.com/character/Gotfai/Lordaeron/achievements', color=0xdab022)
        embedVar.add_field(name="ICC10", value="12/12")
        embedVar.add_field(name="ICC10 Heroic", value="-3/12", inline=True)
        embedVar.add_field(name="\u200b", value="\u200b", inline=True) # empty to skip 3rd column in this row
        embedVar.add_field(name="ICC25", value="12/12", inline=True)
        embedVar.add_field(name="ICC25 Heroic", value="-2137/12", inline=True)
        embedVar.add_field(name="\u200b", value="\u200b", inline=True) # empty to skip 3rd column in this row, otherwise it glitches
        embedVar.set_thumbnail(url='https://cdn.discordapp.com/emojis/855739857409146880.png')
        await message.channel.send(embed=embedVar)


client.run(TOKEN)
