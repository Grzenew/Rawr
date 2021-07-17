# Standard lib ———————————————————————————————————————————————————————————————————————————
import os
import random
import pprint
import psutil
from configparser import ConfigParser
from sys import exit
from operator import itemgetter
from datetime import datetime

# Third party ———————————————————————————————————————————————————————————————————————————
import asyncio
import discord

# Internal ——————————————————————————————————————————————————————————————————————————————
from api import apiCall
from scraper import scrapeCall

# Settings ——————————————————————————————————————————————————————————————————————————————
pp = pprint.PrettyPrinter(indent=4)
POST_STARFALL_QUOTES = [
    'Bestworldx has no mana for DI! ☄️☄️☄️',
    'Dcarl has no SIMBOLS DE DIVINIDAD! ☄️☄️☄️',
    (
        'DI from Breg misses ☄️☄️☄️, '
        'DI from Ebe is super effective! 🌜🦉🌛'
    ),
]
ERROR_MESSAGES = [
    "Are you a dumdum?",
    "Well played.",
    "Kek.",
    "Wat."
]

# load config
config = ConfigParser()
config.read(r'/home/pi/.config')
TOKEN = config.get('settings', 'token')
DB_PWD = config.get('settings', 'db_pwd')


# Functions —————————————————————————————————————————————————————————————————————————————
# return month number for given three letter month name
def month_num(month):
    m = {'jan':"01",'feb':"02",'mar':"03",'apr':"04",'may':"05",'jun':"06",'jul':"07",'aug':"08",'sep':"09",'oct':"10",'nov':"11",'dec':"12"}
    s = month.strip()[:3].lower()
    out = m[s]
    return out

# basic logging function
def log(INPUT):
    now = datetime.now()
    print("[{time}]  {input}".format(time=now.strftime("%m/%d/%Y - %H:%M:%S"), input=INPUT))


# Exec ——————————————————————————————————————————————————————————————————————————————————


# check if script is already running, abort if it is
log("Boot completed, initialization started.")
for q in psutil.process_iter():
    if q.name().startswith('python'):
        if len(q.cmdline())>1 and "init.py" in q.cmdline()[1] and q.pid !=os.getpid():
            log("Bot is already running via 'init.py', aborting the start...")
            exit()

# if bot is not running, begin starting
log("Bot is not yet running. Starting 'init.py'.")


# Main bot script
try:
    client = discord.Client()

    # send print after bot init
    @client.event
    async def on_ready():
        log('{} has connected to {}!'.format(client.user.name, client.guilds))
        await client.change_presence(activity=discord.Game(name="!rawr"))  # change status of bot to "rawr"

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
        elif message.content == 'Starfall':
            response = random.choice(POST_STARFALL_QUOTES)
            await message.channel.send(response)


        # !rawr
        elif message.content == '!rawr':
            log("{nickname} asked for bot info.".format(nickname = message.author.display_name))            
            embedVar = discord.Embed(description="• The commands work when you send a direct message to a bot as well.\n• Bot is under construction so if you had any idea, bug or suggestion, let <@661303805899440148> know!\n• Soon we will have a contest for a name and avatar for the bot, current image is a derp placeholder :)", color=0xdab022)  # settings of embed
            embedVar.add_field(name="!who *nickname*", value="Gives information about chosen character, including GearScore and ICC progression.", inline=False)
            #embedVar.add_field(name="!loot *nick, nick nick*", value="Lists recent loot councilled items that went to chosen players", inline=False)
            embedVar.add_field(name="!guild *Guild Name*", value="Shows basic info about a guild. Work in progress!", inline=False)
            await message.channel.send(embed=embedVar)


        # !guild
        elif message.content.startswith('!guild '):
            query = message.content.split(" ", 1)[1]  # split by 1 space only, i.e. get everything after the space
            log("{nickname} queried guild info for '{query}'".format(nickname = message.author.display_name, query=query))
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
            

        # !reboot
        elif message.content.startswith('!restart me pls'):
            log("{} initiated a reboot.".format(message.author))
            if message.author.id == 661303805899440148:
                await message.add_reaction("👍")
                await client.change_presence(status=discord.Status.idle)
                os.system('sudo reboot')                
            else:
                await message.channel.send("Only daddy can rebooty me.")               

        # !who
        elif message.content.startswith('!who '):
            query = message.content.split()[-1].capitalize()
            log("{nickname} queried character info for '{query}'".format(nickname = message.author.display_name, query=query))
            api_response = apiCall("character", query)
            if api_response == "doesnt exist":  # if given thing doesnt exist in db
                await message.channel.send(random.choice(ERROR_MESSAGES) +" " + query + " does not exist.")
            elif api_response == "error" or api_response == "":  # if there was another error
                await message.channel.send("Something is wrong. <@661303805899440148>, heal me! Quickly!")
            else:  # if all is oke
                if api_response["class"] == "Hunter":
                    is_hunter = True
                else:
                    is_hunter = False
                scrape_response = scrapeCall("character", query, IS_HUNTER=is_hunter)            

                icons = {  # icons uploaded as emojis to my dev server, used for classes
                    "Mage": '855739857409146880', 
                    "Death Knight": '855748451677634560',
                    "Hunter": '855748451623370762',
                    "Druid": '855748451799138344',
                    "Paladin": '855748451735699456',
                    "Priest": '855748451782230026',
                    "Rogue": '579532030086217748',
                    "Shaman": '855748451643031553',
                    "Warlock": '855748451672260608',
                    "Warrior": '855748451644211200',
                    "Alliance": '860191290503069697',
                    "Horde": '860191290829570068'
                }


                if api_response["online"] == True:
                    online_status = "<:Online:861959950721089556>"
                else:
                    online_status = ""

                title = "{online} {nickname} ({level})".format(online=online_status, level=api_response["level"], nickname=query)  # title - "Name (level)"
                description = "<:class{classname}:{icon}> {specs}".format(icon=icons[api_response["class"]], specs=api_response["specs"], classname=api_response["class"].lower().replace(" ",""))  # descriprion - "Guild • Spec/Spec"
                description += "\n<:{faction}:{icon}> {guild}".format(faction=api_response["faction"], icon=icons[api_response["faction"]], guild=api_response["guild"])  # descriprion - "Guild • Spec/Spec"
                description += "\n<:Gearscore:861705201362796594> {}".format(str(scrape_response["gs"]))
                description += "\n<:AchievementPoints:861706248884584459> {}".format(api_response["ap"])
                icc_completion = ""


                embedVar = discord.Embed(title=title, description=description, url='http://armory.warmane.com/character/{nick}/Lordaeron/profile'.format(nick=query), color=0xdab022)
                if int(scrape_response["ICC10 normal"]) > 0:
                    icc_completion += "` {result}/12 ` 10-man NM {lk}\n".format(result=scrape_response["ICC10 normal"], lk=scrape_response["lk"]["10"])
                if int(scrape_response["ICC10 heroic"]) > 0:
                    icc_completion += "` {result}/12 ` 10-man HC {lk}\n".format(result=scrape_response["ICC10 heroic"], lk=scrape_response["lk"]["10hc"])
                if int(scrape_response["ICC25 normal"]) > 0:
                    icc_completion += "` {result}/12 ` 25-man NM {lk}\n".format(result=scrape_response["ICC25 normal"], lk=scrape_response["lk"]["25"])
                if int(scrape_response["ICC25 heroic"]) > 0:
                    icc_completion += "` {result}/12 ` 25-man HC {lk}".format(result=scrape_response["ICC25 heroic"], lk=scrape_response["lk"]["25hc"])
                if icc_completion != "":
                    embedVar.add_field(name="Icecrown Citadel", value=icc_completion, inline=False)
                #embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                embedVar.set_thumbnail(url='https://cdn.discordapp.com/emojis/{class_icon_id}.png'.format(class_icon_id=icons[api_response["class"]]))
                await message.channel.send(embed=embedVar)


        # !loot     
        elif message.content.startswith('!loot ') and message.channel.guild.name=="Lions Pride" and message.channel.name in ["notepad","officer-chat","officers-and-helpers"]:
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
            # manually add two rows for data from first message
            rewarded_list.append(["0401", "Glowing Twilight Scale", "Frejr"])
            rewarded_list.append(["0401", "Charred Twilight Scale", "Gotfai"])
 
            async for msg in client.get_channel(827234214982058045).history(limit=100): # As an example, I've set the limit to 10000
                if msg.id != 827234534280921139:  # skip the description message

                    message_whole = msg.content
                    for replace_key in replace_dict.keys():  # replace all strings as in the dict above
                        message_whole = message_whole.replace(replace_key, replace_dict[replace_key])
                    message_whole = message_whole.split("\n")  # split message into list of rows
                    message_whole = [i.strip() for i in message_whole]  # strip front/back whitespaces in each row

                    # date
                    msg_date = message_whole[0].split(" ")  # split date to 2 elements
                    msg_date[1] = month_num(msg_date[1])  # convert month to number
                    msg_date[0] = msg_date[0].replace("st", "").replace("th", "").replace("nd", "").replace("rd", "").zfill(2)  # remove affixes and fill zero in front if needed
                    msg_date = "".join(reversed(msg_date))  # join month and day in reversed order, so that you can sort by month and day

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


            # do actions related ot the query
            query = message.content.split(" ", 1)[1]  # get rid of "!loot" for query

            if query[0:4] == "item":  # if first 4 characters are "item"
                query = query.split(" ", 1)[1]  # cut off first word (it is surely "item/items")
                log("{nickname} queried item info for '{item}'".format(nickname = message.author.display_name, item=query))
                await message.channel.send("Doesn't work yet.")

            else:  # if it is not for item, i.e. is for character(s)
                output = []
                output_rows = ""
                loot_counter = {}
                output_footer = []
                nicknames = query.replace(","," ").replace("  ", " ").split(" ")
                nicknames = [i.capitalize() for i in nicknames]  # strip whitespaces around nicknames and capitalize them
                log("{nickname} queried player loot info for '{item}'".format(nickname = message.author.display_name, item=query))

                # roll through the queried nicknames
                for nickname in nicknames:
                    for rewarded_row in rewarded_list:  # roll through rewarded 
                        if rewarded_row[2] == nickname:  # is 3rd value of the rewarded list's row is equal to nickname?
                            if nickname not in loot_counter:
                                loot_counter[nickname] = 0
                            loot_counter[nickname] += 1
                            output.append(rewarded_row)

                output = sorted(output, key=itemgetter(0), reverse=True)

                # output the collected data to a embed
                embedVar = discord.Embed(description="", color=0xdab022)  # settings of embed
                for output_row in output:  # iterate through the prepared list od rewarded items
                    output_row[0] = output_row[0][2:4] + "/" + output_row[0][0:2]  # prepare date to be DD/MM
                    output_row[2] = "**{}**".format(output_row[2])  # make item name t h i c c
                    output_row[1] = output_row[1].replace(" heroic", " **HC**").replace(" Heroic", " **HC**")  # replace Heroic with HC
                    output_rows += output_row[0] + " " + output_row[2] +  " " + output_row[1] + "\n"

                for counter_nick, counter_count in loot_counter.items():  # iterate through the counter items and prepare footer items
                    output_footer.append("{} ({})".format(counter_nick, counter_count))
                output_footer = "⠀•⠀".join(output_footer)  # split footer items by a dot

                # add joined fields to the embed output, add foter and print to channel
                embedVar.add_field(name="Coucilled loot for {}.".format(", ".join(nicknames)), value=output_rows, inline=True)
                embedVar.set_footer(text=output_footer)
                await message.channel.send(embed=embedVar)


    client.run(TOKEN)

except Exception as e:
    log(e)
