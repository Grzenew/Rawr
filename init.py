# ⚪️ Standard lib
import os
import random
import pprint
import logging as log
from sys import stdout, exit
from operator import itemgetter
import configparser
import psutil

# check if script is already running, print to output
print("Attempting to start...")
def is_running(script):
    for q in psutil.process_iter():
        if q.name().startswith('python'):
            if len(q.cmdline())>1 and script in q.cmdline()[1] and q.pid !=os.getpid():
                exit("Bot is already running via '{}', aborting the start...".format(script))
                return True
    return False
if not is_running("init.py"):
	print("Script is not running, starting...")


# ⚪️ Third party
import asyncio
import discord

# Internal
from api import apiCall
from scraper import scrapeCall



# 🔴 Settings
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
    "Did someone say starfol?"
]
def month_num(month):
    m = {'jan':"01",'feb':"02",'mar':"03",'apr':"04",'may':"05",'jun':"06",'jul':"07",'aug':"08",'sep':"09",'oct':"10",'nov':"11",'dec':"12"}
    s = month.strip()[:3].lower()
    out = m[s]
    return out

# load config from local file
config = configparser.ConfigParser()
#config.readfp(open(r'.config'))  # local
config.readfp(open(r'/home/pi/.config'))  # production
TOKEN = config.get('settings', 'token')
LOG_PATH = config.get('settings', 'logPath')

##  logger config
log.basicConfig(
    filename=LOG_PATH, 
    filemode='a', 
    format='%(asctime)s %(levelname).4s (%(lineno).3s %(funcName)s)  %(message)s', 
    datefmt='[%Y/%m/%d %H:%M:%S]',
    level=log.INFO)
log.getLogger().addHandler(log.StreamHandler(stdout))

log.info('Bot initiated, settings loaded.')


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
            log.info("{nickname} queried character info for '{query}'".format(nickname = message.author.display_name, query=query))
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
                    description += "\nItem level: " + str(scrape_response["ilvl"])

                embedVar = discord.Embed(title=title, description=description, url='http://armory.warmane.com/character/{nick}/Lordaeron/achievements'.format(nick=query), color=0xdab022)
                if int(scrape_response["ICC10 normal"]) > 0:
                    embedVar.add_field(name="ICC10", value=scrape_response["ICC10 normal"] + "/12")
                else:
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                if int(scrape_response["ICC10 heroic"]) > 0:
                    embedVar.add_field(name="ICC10 Heroic", value=scrape_response["ICC10 heroic"] + "/12", inline=True)
                else:
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                if int(scrape_response["ICC25 normal"]) > 0:
                    embedVar.add_field(name="ICC25", value=scrape_response["ICC25 normal"] + "/12", inline=True)
                else:
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                if int(scrape_response["ICC25 heroic"]) > 0:
                    embedVar.add_field(name="ICC25 Heroic", value=scrape_response["ICC25 heroic"] + "/12", inline=True)
                else:
                    embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                embedVar.add_field(name="\u200b", value="\u200b", inline=True)
                embedVar.set_thumbnail(url='https://cdn.discordapp.com/emojis/{class_icon_id}.png'.format(class_icon_id=class_icons[api_response["class"]]))
                await message.channel.send(embed=embedVar)


        # !loot
        if message.content.startswith('!loot '):

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
                log.info("{nickname} queried item info for '{item}'".format(nickname = message.author.display_name, item=query))
                await message.channel.send("Doesn't work yet.")

            else:  # if it is not for item, i.e. is for character(s)
                output = []
                loot_counter = {}
                output_footer = []
                nicknames = query.replace(","," ").replace("  ", " ").split(" ")
                nicknames = [i.capitalize() for i in nicknames]  # strip whitespaces around nicknames and capitalize them
                log.info("{nickname} queried player loot info for '{item}'".format(nickname = message.author.display_name, item=query))

                # roll through the queried nicknames
                for nickname in nicknames:
                    for rewarded_row in rewarded_list:  # roll through rewarded 
                        if rewarded_row[2] == nickname:  # is 3rd value of the rewarded list's row is equal to nickname?
                            if nickname not in loot_counter:
                                loot_counter[nickname] = 0
                            loot_counter[nickname] += 1
                            output.append(rewarded_row)

                output = sorted(output, key=itemgetter(0), reverse=True)
                #pp.pprint(output)

                # output the collected data to a embed
                description = "Coucilled loot for {}.".format(", ".join(nicknames))  # top description row of embed
                embedVar = discord.Embed(description=description, color=0xdab022)  # settings of embed
                for output_row in output:  # iterate through the prepared list od rewarded items
                    output_row[0] = output_row[0][2:4] + "/" + output_row[0][0:2]  # prepare date to be DD/MM
                    output_row[2] = "**{}**".format(output_row[2])  # make item name t h i c c
                    output_row[1] = output_row[1].replace(" heroic", " **HC**").replace(" Heroic", " **HC**")  # replace Heroic with HC

                output_dates = "\n".join([item[0] for item in output])  # join all date cells into one string separated by \n
                output_nicknames = "\n".join([item[2] for item in output])  # as above, but for nicknames
                output_items = "\n".join([item[1] for item in output])  # as above by for item names
                for counter_nick, counter_count in loot_counter.items():  # iterate through the counter items and prepare footer items
                    output_footer.append("{} ({})".format(counter_nick, counter_count))
                output_footer = "⠀•⠀".join(output_footer)  # split footer items by a dot

                # add joined fields to the embed output, add foter and print to channel
                embedVar.add_field(name="\u200b", value=output_dates, inline=True)
                embedVar.add_field(name="\u200b", value=output_nicknames, inline=True)
                embedVar.add_field(name="\u200b", value=output_items, inline=True)
                embedVar.set_footer(text=output_footer)
                await message.channel.send(embed=embedVar)


    client.run(TOKEN)

except Exception as e:
    log.error(e)
