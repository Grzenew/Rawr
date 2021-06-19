# 🟡 Third party modules
from os import replace
import numpy as np
import requests


# 🔴 Settings
HEADERS = "{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}"
# headers required since api denies bot calls


# 🟢 Exec
def scrape(TYPE, QUERY, REALM="Lordaeron"):

    # 🟢 player data called
    if TYPE == "character":

        # capitalize nickname coz dumdum api doesn't understand otherwise
        QUERY = QUERY.capitalize()

        # death grip the data
        with requests.get("http://armory.warmane.com/api/character/{query}/{realm}/summary".format(query=QUERY, realm=REALM), HEADERS) as result:
            result_array = result.json()

            # dictionary of class emojis
            classes = {"Mage": '<:classmage:855739857409146880>', 
                       "Death Knight": '<:classdk:855748451677634560>',
                       "Hunter": '<:classhunter:855748451623370762>',
                       "Druid": '<:classdruid:855748451799138344>',
                       "Paladin": '<:classpaladin:855748451735699456>',
                       "Priest": '<:classpriest:855748451782230026>',
                       "Rogue": '<:classrogue:855748451812114443>',
                       "Shaman": '<:classshaman:855748451643031553>:',
                       "Warlock": '<:classwarlock:855748451672260608>',
                       "Warrior": '<:classwarrior:855748451644211200>'}

            return "\n{icon}**{level}** {name} is the best {race} that has ever existed on Azeroth.".format(icon=classes[result_array["class"]], level=result_array["level"], race=result_array["race"].lower(), name=result_array["name"])

    # 🟢 if duder taunts guild data
    elif TYPE == "guild":

        # replace spaces with plus signs
        if " " in QUERY:
            QUERY.replace(" ", "+")

        # death grip the data
        with requests.get("https://armory.warmane.com/api/guild/{query}/{realm}/members".format(query=QUERY, realm=REALM), HEADERS) as result:
            result_array = result.json()
            guild_name = result_array["name"]

            # Count online dudes
            online_counter = 0
            online_names = []
            for i in range(int(result_array["membercount"])):  # loop through the list
                if result_array["roster"][i]["online"]:  # if "online" is TRUE
                    online_counter += 1
                    online_names.append(result_array["roster"][i]["name"])
                    online_names_list = ", ".join(str(x) for x in online_names)

        return "\n{name} has {amount} members, {online_amount} online: {online}.".format(name=guild_name, amount=result_array["membercount"], online_amount=online_counter, online=online_names_list)

