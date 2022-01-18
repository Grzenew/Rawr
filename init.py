# Standard lib ———————————————————————————————————————————————————————————————————————————
import os, subprocess
import random
import psutil
import logging
from logging.config import dictConfig
from time import time, gmtime, strftime
from configparser import ConfigParser
from sys import exit
from operator import itemgetter

# Third party ———————————————————————————————————————————————————————————————————————————
import asyncio
import discord



# Settings ——————————————————————————————————————————————————————————————————————————————

ERROR_MESSAGES = [
    "Are you a dumdum?",
    "Well played.",
    "Kek.",
    "Wat."
]
ADMIN_RIGHTS = [
    436167336337211394, # gotfai
    661303805899440148  # frej
]
OFFICER_RIGHTS = [
    436167336337211394, # gotfai
    362977236132823042, # mata
    630128046006861854, # wolf
    661303805899440148  # frej
]
LOOT_LIST_ENABLED = [
    "notepad",
    "officer-chat",
    "loot-council"
]
MATA_EMOJIS = [
    "814549178625163314",
    "814551666896273449",
    "817082440665006101",
    "814551666896273449",
    "814549233998626908",
    "818475175767048233",
    "814551487127617546",
    '814547569287364608',
    '864982158355333170',
    '864982161076781056',
    '814549288225865748'
]

# load config
config = ConfigParser()
config.read(r'/home/pi/production/Rawr/.conf')
CFG_TOKEN = config.get('settings', 'token')
CFG_LOGGING_PATH = config.get('settings', 'log_path')
#CFG_TEMPERATURE_PATH = config.get('settings', 'temperature_path')

# logger config
dictConfig({
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'standard': {
            'format': '%(asctime)s %(levelname).4s (%(lineno)3s %(module)s/%(funcName)s)  %(message)s', 
            'datefmt': '[%Y/%m/%d %H:%M:%S]',
        }
    },
   'handlers' : {
        'default': {
            'level': 'INFO', 
            'class': 'logging.StreamHandler',
            'formatter': 'standard',
        },
        'file': {
            'level': 'INFO', 
            'class': 'logging.FileHandler',
            'formatter': 'standard',
            'filename': CFG_LOGGING_PATH,
            'mode': 'a',
        }
   }, 
   'loggers': {
        '__main__': {
            'level': 'INFO', 
            'handlers' : ['default', 'file'], 
            'propagate': False,
        },
        'scraper': {
            'level': 'INFO', 
            'handlers' : ['default', 'file'], 
            'propagate': False,
        },
   },
   'root': {
        'level': 'WARN',
        'handlers': ['default', 'file']
   },
})

# create logger
log = logging.getLogger(__name__)


# Internal ——————————————————————————————————————————————————————————————————————————————
from api import apiCall
from scraper import scrapeCall


# Functions —————————————————————————————————————————————————————————————————————————————
# return month number for given three letter month name
def month_num(month):
    m = {'jan':"01",'feb':"02",'mar':"03",'apr':"04",'may':"05",'jun':"06",'jul':"07",'aug':"08",'sep':"09",'oct':"10",'nov':"11",'dec':"12"}
    s = month.strip()[:3].lower()
    out = m[s]
    return out

# check if a message is too long for discord output
def strip_msg(message, length=2000):
    if len(message) > length: 
        message = message[:length-12] + "\n(too long)"  # return the longest possible part of message + information it has been to long
    return message


# Exec ——————————————————————————————————————————————————————————————————————————————————


# check if script is already running, abort if it is
log.info("Boot completed, initialization started.")
for q in psutil.process_iter():
    if q.name().startswith('python'):
        if len(q.cmdline())>1 and "init.py" in q.cmdline()[1] and q.pid !=os.getpid():
            log.info("Bot is already running via 'init.py', aborting the start...")
            exit()

# if bot is not running, begin starting
log.info("Bot is not yet running. Starting 'init.py'.")


# Main bot script
try:
    client = discord.Client()

    # send print after bot init
    @client.event
    async def on_ready():
        log.info('{} has connected to {}!'.format(client.user.name, client.guilds))
        await client.change_presence(activity=discord.Game(name="!rawr"))  # change status of bot to "In game: !rawr"


    # if someone writes "Starfall", a random str gets printed by the bot
    @client.event
    async def on_message(message):

        author_nickname = message.author.display_name+" ("+message.author.name+"#"+message.author.discriminator+")"

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


        # !rawr
        elif message.content == '!rawr':
            log.info("{} asked for bot info.".format(author_nickname))            
            embedVar = discord.Embed(description="• The commands work when you send a direct message to a bot as well.\n• Bot is under construction so if you had any idea, bug or suggestion, let <@661303805899440148> know!\n• Soon we will have a contest for a name and avatar for the bot, current image is a derp placeholder :)", color=0xdab022)  # settings of embed
            embedVar.add_field(name="!who *nickname*", value="Gives information about chosen character, including GearScore and ICC progression.", inline=False)
            #embedVar.add_field(name="!loot *nick, nick nick*", value="Lists recent loot councilled items that went to chosen players", inline=False)
            embedVar.add_field(name="!guild *Guild Name*", value="Shows basic info about a guild. Work in progress!", inline=False)
            await message.channel.send(embed=embedVar)


        # !guild
        elif message.content.startswith('!guild '):
            query = message.content.split(" ", 1)[1]  # split by 1 space only, i.e. get everything after the space
            log.info("{} queried guild info for '{}'".format(author_nickname, query))
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
            

        # !pls - system commands
        elif message.content.startswith('!pls'):            
            log.info("{} sent '{}'.".format(author_nickname, message.content))
            if message.author.id in OFFICER_RIGHTS:
                query = message.content.split(" ")  # split by spaces
                if len(query) > 1:  # if has more than one element, i.e. has some command

                    print(query[1])
                    print(message.author.id)

                    # restarting bot
                    if query[1] in ["reboot", "restart"]:
                        await message.add_reaction("👍")
                        await client.change_presence(status=discord.Status.idle)
                        os.system("sudo reboot")

                    # stopping bot
                    elif query[1] in ["exit", "stop"] and message.author.id in ADMIN_RIGHTS:
                        await message.add_reaction("👍")
                        exit()

                    # stopping bot
                    elif query[1] == "git" and message.author.id in ADMIN_RIGHTS:
                        if query[2] == "status":
                            await message.add_reaction("👍")
                            batcmd="git --git-dir=production/Rawr/.git fetch ; git --git-dir=production/Rawr/.git status"
                            result = subprocess.check_output(batcmd, shell=True).splitlines()
                            await message.channel.send("{}".format(result[1].decode("utf-8")))
                        if query[2] == "pull":
                            await message.add_reaction("👍")
                            batcmd="git --git-dir=production/Rawr/.git pull"
                            result = subprocess.check_output(batcmd, shell=True)


                    # reading from log
                    elif query[1] == "log":
                        lines_to_read = int(query[2])  # get 2nd argument, i.e amount of lines to read
                        log_file = open(CFG_LOGGING_PATH, "r")
                        file = log_file.readlines()
                        last_lines = "".join(file[-lines_to_read:])
                        if len(last_lines) > 1999:
                            last_lines = last_lines[:1985] + "\n (too long)"
                        dm = await message.author.create_dm()
                        await dm.send("`"+last_lines+"`")

                # in nothing was given, measure temperature
                else:
                    #os.system("vcgencmd measure_temp")
                    uptime = time() - psutil.boot_time()
                    uptime_msg = "<:Online:861959950721089556> " + strftime("%H hours, %M minutes", gmtime(uptime))
                    #temperature = int(open(CFG_TEMPERATURE_PATH).readline())
                    temperature = int(os.popen("vcgencmd measure_temp").readline())
                    temperature = str(round(temperature/1000, 2))
                    temperature_msg = "🔥 " + temperature + "°C"
                    await message.channel.send("{}\n{}".format(temperature_msg, uptime_msg))

                    # delete message if it is on a server, not a DM
                    if message.guild is not None and message.author != client.user:  
                        await message.delete()

            else:
                await message.channel.send("Only daddy can do dis.")               

        # !who
        elif message.content.startswith('!who '):
            query = message.content.split()[-1].capitalize()
            log.info("{} queried character info for '{}'".format(author_nickname, query))
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
        elif message.content.startswith('!loot '):

            # if it was sent via DM
            if message.guild is None:
                dm = await message.author.create_dm()
                await dm.send("Sorries, it doesn't work via DM. Try on {}".format(", ".join(LOOT_LIST_ENABLED)))

            # if it was sent on a channel, check if server is Lions' and if this command is enabled for this channel
            elif (message.channel.guild.name=="Lions Pride" or message.channel.guild.name=="Rawr Dev") and message.channel.name in LOOT_LIST_ENABLED:
                rewarded_list = []
                replace_dict = {  # all occurences from first column will be replaced with that from 2nd column
                    "**":"", 
                    "  ":" ",
                    " (offhand)":"",
                    " (OS)":"",
                    "- ":": ",
                    "Marks:":"Mark:",
                    " (trinket)":"",
                    "Mark: Cede\n":"Mark: Cedevitago\n"
                }

                # manually add two rows for data from first message
                rewarded_list.append(["20210401", "Glowing Twilight Scale", "Frejr"])
                rewarded_list.append(["20210401", "Charred Twilight Scale", "Gotfai"])
    
                async for msg in client.get_channel(827234214982058045).history(limit=200): # How many messages to be scanned in the loot
                    if msg.id != 827234534280921139:  # skip the description message

                        message_whole = msg.content
                        for replace_key in replace_dict.keys():  # replace all strings as in the dict above
                            message_whole = message_whole.replace(replace_key, replace_dict[replace_key])
                        message_whole = message_whole.split("\n")  # split message into list of rows
                        message_whole = [i.strip() for i in message_whole]  # strip front/back whitespaces in each row

                        # date
                        msg_date = message_whole[0].split(" ")  # split date to 3 elements
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

                output = []
                output_rows = ""
                footer_too_long = ""
                loot_counter = {}
                output_footer = []
                nicknames = query.replace(","," ").replace("  ", " ").split(" ")
                nicknames = [i.capitalize() for i in nicknames]  # strip whitespaces around nicknames and capitalize them
                log.info("{} queried player loot info for '{}'".format(author_nickname, query))

                # roll through the queried nicknames
                if message.content.split(" ", 1)[1] == "all":
                    print("all")
                    for rewarded_row in rewarded_list:  # roll through rewarded 
                        if rewarded_row[2] not in loot_counter:
                            loot_counter[rewarded_row[2]] = 0
                        loot_counter[rewarded_row[2]] += 1
                        output.append(rewarded_row)
                else:
                    for nickname in nicknames:
                        for rewarded_row in rewarded_list:  # roll through rewarded 
                            if rewarded_row[2] == nickname:  # is 3rd value of the rewarded list's row is equal to nickname?
                                if nickname not in loot_counter:
                                    loot_counter[nickname] = 0
                                loot_counter[nickname] += 1
                                output.append(rewarded_row)

                output = sorted(output, key=itemgetter(0), reverse=True)

                # Discord's char limit is 1024, otherwise message is not sent. Each row takes ~50 characters, so on average there should be max rows displayed.
                if len(output) > 20:
                    output = output[:20]
                    footer_too_long = "\n⚠️ List was too long, oldest items were cleaved"

                # output the collected data to a embed
                embedVar = discord.Embed(description="", color=0xdab022)  # settings of embed
                for output_row in output:  # iterate through the prepared list od rewarded items
                    output_row[0] = output_row[0][-2:] + "/" + output_row[0][4] + output_row[0][5] + "/" + output_row[0][2] + output_row[0][3]   # prepare date to be DD/MM/YY
                    output_row[2] = "**{}**".format(output_row[2])  # make item name t h i c c
                    output_row[1] = output_row[1].replace(" heroic", " **HC**").replace(" Heroic", " **HC**")  # replace Heroic with HC
                    output_rows += output_row[0] + " " + output_row[2] +  " " + output_row[1] + "\n"

                # sort by amount of items gained 
                loot_counter = dict(sorted(loot_counter.items(), key=lambda item: item[1], reverse=True))

                for counter_nick, counter_count in loot_counter.items():  # iterate through the counter items and prepare footer items
                    output_footer.append("{} ({})".format(counter_nick, counter_count))
                output_footer = "⠀•⠀".join(output_footer) + footer_too_long  # split footer items by a dot

                # add joined fields to the embed output, add foter and print to channel
                embedVar.add_field(name="Councilled loot for {}".format(", ".join(nicknames)), value=output_rows, inline=True)
                embedVar.set_thumbnail(url='https://cdn.discordapp.com/emojis/{}.png'.format(random.choice(MATA_EMOJIS)))
                embedVar.set_footer(text=output_footer)

                # if there was some data, print, otherwise output error
                if len(output) > 0:
                    await message.channel.send(embed=embedVar)
                else:
                    await message.channel.send("Seemingly there has been no loot for {}".format(", ".join(nicknames)))

                # remove the author's call message
                await message.delete()

        if message.guild is None and message.author != client.user:
            if message.channel.id == message.author.dm_channel.id:
                log.info("{} DM'd: '{}'".format(author_nickname, message.content))


    client.run(CFG_TOKEN)

except Exception as e:
    log.info(e)
