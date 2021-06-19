#     Discord api   https://discordpy.readthedocs.io/en/stable/api.html
#     Warmane api   https://armory.warmane.com/api/guild/Lions+Pride/Lordaeron/members
#                   http://armory.warmane.com/api/character/Gotfai/Lordaeron/summary
#                   http://armory.warmane.com/api/team/name/realm/type
#    Database api   http://mop.cavernoftime.com/api



# ⚪️ Standard lib
import os
import random
from dotenv import load_dotenv


# 🟡 Third party
import asyncio
import requests 
import discord


# 🔴 Settings
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')
GUILD_URL = "https://armory.warmane.com/api/guild/Lions+Pride/Lordaeron/members"
POST_STARFALL_QUOTES = [
    'Bestworldx has no mana for DI! ☄️☄️☄️',
    'Dcarl has no SIMBOLS DE DIVINIDAD! ☄️☄️☄️',
    (
        'DI from Breg misses ☄️☄️☄️, '
        'DI from Ebe is super effective! 🌜🦉🌛'
    ),
]


# 🟢 Exec
with requests.get(GUILD_URL, headers={'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}) as result:
    print(result.content.decode())

client = discord.Client()

# send print after bot init
@client.event
async def on_ready():
    print(f'{client.user.name} has connected to Discord!')

# send to new users joining the server
@client.event
async def on_member_join(member):
    await member.create_dm()
    await member.dm_channel.send(
        f'Hi {member.name}, gib me strudels!'
    )

# if user writes "tomb", then bot asks given dude for :sindra: reaction. If user gives it, then bot responds with random "belly/head" OR "Wipe" if 60 secs pass w/o any action
# if someone writes "Starfall", a random str gets printed by the bot
@client.event
async def on_message(message):

    # avoid endless loop in case bot said its own trigger word
    if message.author == client.user:
        return

    # if someone says heh -> bot triggers
    elif message.content.startswith('tomb'):
        channel = message.channel
        await channel.send('Send me that <:sindra:853223712702201858> reaction, %s!' % message.author.name)

        def check(reaction, user):
            return user == message.author and str(reaction.emoji) == '<:sindra:853223712702201858>'

        try:
            reaction, user = await client.wait_for('reaction_add', timeout=60.0, check=check)
        except asyncio.TimeoutError:
            await channel.send('Wipe')
        else:
            await channel.send(random.choice(["Belly!", "Head!"]))


    if message.content == 'Starfall':
        response = random.choice(POST_STARFALL_QUOTES)
        await message.channel.send(response)


client.run(TOKEN)
