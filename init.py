# ⚪️ Standard lib
import os
import random
import pprint
import logging as log
from dotenv import load_dotenv
from sys import stdout


# ⚪️ Third party
import asyncio
import discord

# Internal
from api import apiCall
from scraper import scrapeCall



# 🔴 Settings
pp = pprint.PrettyPrinter(indent=4)
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
ERROR_MESSAGES = [
    "Are you retarded?",
    "Well played.",
    "Daylight's burning.",
    "Kek.",
    "Did someone say starfol?"
]
def month_num(month):
    m = {'jan':"01",'feb':"02",'mar':"03",'apr':"04",'may':"05",'jun':"06",'jul':"07",'aug':"08",'sep':"09",'oct':"10",'nov':"11",'dec':"12"}
    s = month.strip()[:3].lower()
    out = m[s]
    return out

##  logger config
log.basicConfig(
    filename='rawr.log', 
    filemode='a', 
    format='%(asctime)s %(levelname).4s (%(lineno).3s %(funcName)s)  %(message)s', 
    datefmt='[%Y/%m/%d %H:%M:%S]',
    level=log.INFO)
log.getLogger().addHandler(log.StreamHandler(stdout))

# 🟢 Exec
try:
    client = discord.Client()

    # send print after bot init
        
    async def on_ready():
        log.info('{} has connected to Discord!'.format(client.user.name))
        print("x")

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
            response = apiCall("guild", query.replace(" ", "+"))
            if response == "doesnt exist":
                to_send = random.choice(ERROR_MESSAGES) +" " + query + " does not exist."
            elif response == "error":
                to_send = "Something is wrong. <@661303805899440148>, heal me! Quickly!"
            else:
                to_send = "{guild_name} has {amount} members, {online_amount} online.".format(guild_name=response["name"], amount=response["membercount"], online_amount=response["online_counter"])
                if "online_names_list" in response:
                    to_send = to_send[:-1] + ": " + response["online_names_list"]
            await message.channel.send(to_send)

        # !who keyword
        if message.content.startswith('!who '):
            query = message.content.split()[-1].capitalize()
            log.error(query)
            api_response = apiCall("character", query)
            if api_response == "doesnt exist":  # if given thing doesnt exist in db
                await message.channel.send(random.choice(ERROR_MESSAGES) +" " + query + " does not exist.")
            elif api_response == "error" or api_response == "":  # if there was another error
                await message.channel.send("Something is wrong. <@661303805899440148>, heal me! Quickly!")
            else:  # if all is oke
                scrape_response = scrapeCall("character", query)

                class_icons = {  # icons uploaded as emojis to my dev server, used for classes
                    "Mage": '855739857409146880', 
                    "Death Knight": '855748451677634560',
                    "Hunter": '855748451623370762',
                    "Druid": '855748451799138344',
                    "Paladin": '855748451735699456',
                    "Priest": '855748451782230026',
                    "Rogue": '579532030086217748',
                    "Shaman": '855748451643031553',
                    "Warlock": '855748451672260608',
                    "Warrior": '855748451644211200'
                }

                title = query + " (" + api_response["level"] + ")"  # title - "Name (level)"
                description = api_response["specs"]  # descriprion - "Guild • Spec/Spec"
                if api_response["guild"] != "":
                    description = api_response["guild"] + " • " + description

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


        # !loot
        if message.content.startswith('!loot'):

            rewarded_list = []
            replace_dict = {
                "**":"", 
                "  ":" ",
                " (offhand)":"",
                " (OS)":"",
                "- ":": ",
                "Marks:":"Mark:",
                " (trinket)":""
            } 
            
 
            async for msg in client.get_channel(827234214982058045).history(limit=100): # As an example, I've set the limit to 10000
                if msg.id != 827234534280921139:  # skip the description message

                    message_whole = msg.content  # get rid of bold and split message into rows
                    for replace_key in replace_dict.keys():  # replace all strings as in the dict above
                        message_whole = message_whole.replace(replace_key, replace_dict[replace_key])
                    message_whole = message_whole.split("\n")  # split message into list of rows
                    message_whole = [i.strip() for i in message_whole]  # strip front/back whitespaces in each row

                    # date
                    msg_date = message_whole[0].split(" ")  # split date to 2 elements
                    msg_date[1] = month_num(msg_date[1])  # convert month to number
                    msg_date[0] = msg_date[0].replace("st", "").replace("th", "").replace("nd", "").replace("rd", "").zfill(2)  # remove affixes and fill zero in front if needed
                    msg_date = "/".join(reversed(msg_date))  # first row is date row

                    # items
                    msg_items = message_whole[1:]  # separate items rows from date row
                    for item in msg_items:  # roll through all items in this message
                        item_data = item.split(": ")  # split by ": " to get item name separated
                        item_name = item_data[0]  # get the item name
                        item_persons = item_data[1].replace(" / ", ", ").replace(" & ", ", ").split(", ")  # divide persons by ", "
                        for person in item_persons:  # roll through all persons
                            if "(x2)" in person:  # if given person name has (x2)
                                person = person.replace(" (x2)", "")  # remove " (x2)" from the person's name
                                rewarded_list.append([msg_date, item_name, person])
                                rewarded_list.append([msg_date, item_name, person])
                            else:
                                rewarded_list.append([msg_date, item_name, person])

        # fucking hell finally a list
        pp.pprint(rewarded_list)
                        

    client.run(TOKEN)

except Exception as e:
    log.error(e)

"""
data = data.append({'content': msg.content,
'time': msg.created_at,
'author': msg.author.name}, ignore_index=True)
"""