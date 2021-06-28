#  Third party modules ———————————————————————————————————————————————————————————————————————————
import requests
import html_to_json
import mysql.connector as mysql
import logging as log


# Settings ———————————————————————————————————————————————————————————————————————————————————————
db = mysql.connect(
    host = "localhost",
    user = "user",
    passwd = "icoteraz2010",
	database="items"
)


# Exec ————————————————————————————————————————————————————————————————————————————————————————————
def scrapeCall(CATEGORY, QUERY, REALM="Lordaeron"):

    ACHI_DATA = {}
    ANSWER = {}
    BASE_URL = "http://armory.warmane.com/character/{character}/{realm}/".format(character=QUERY, realm=REALM)
    HEADERS = {'Authorization': 'Bearer 05f7544e468d6067a914a781660486a9612df4478e', 'Cookie': 'PHPSESSID=k3mkdkk1be86l5kr7bu2th5chn'}

    # No need to check for anything except lower, as everything else is covered by statistics-page check
    TO_CHECK_ACHI = {
        "ICC25": {
            "id": 15042,
            "achis": {
                # NM
                "ach4604": [4, "Lower"], #  4 bosses - lower
                #"ach4605": [3, "Plague"], #  3 bosses - plague
                #"ach4606": [2, "Blood"], #  2 bosses - blood
                #"ach4607": [2, "Frost"], #  2 bosses - frost
                #"ach4608": [1, "LK"],  #  1 - big boye
                # HC
                "ach4632": [40, "Lower HC"], #  4 bosses - lower
                #"ach4633": [30, "Plague HC"], #  3 bosses - plague
                #"ach4634": [20, "Blood HC"], #  2 bosses - blood
                #"ach4635": [20, "Frost HC"], #  2 bosses - frost
                #"ach4637": [10, "LK HC"],  #  1 - big boye
            },
        },
        "ICC10": {
            "id": 15041,
            "achis": {
                # NM
                "ach4531": [4, "Lower"], #  4 bosses - lower
                #"ach4528": [3, "Plague"], #  3 bosses - plague
                #"ach4529": [2, "Blood"], #  2 bosses - blood
                #"ach4527": [2, "Frost"], #  2 bosses - frost
                #"ach4532": [1, "LK"],  #  1 - big boye
                # HC
                "ach4628": [40, "Lower HC"], #  4 bosses - lower
                #"ach4629": [30, "Plague HC"], #  3 bosses - plague
                #"ach4630": [20, "Blood HC"], #  2 bosses - blood
                #"ach4631": [20, "Frost HC"], #  2 bosses - frost
                #"ach4636": [10, "LK HC"]  #  1 - big boye
            }
        }
    }
    TO_CHECK_DUNG = {
        "icc": {
            "id": 15062
        }
    }

    if CATEGORY=="character":

        # scrape achievements
        url = BASE_URL + "/achievements"

        for instance_name, instance_data in TO_CHECK_ACHI.items():
            headers = {'Authorization': 'Bearer 05f7544e468d6067a914a781660486a9612df4478e', 'Cookie': 'PHPSESSID=k3mkdkk1be86l5kr7bu2th5chn'}
            response = requests.request("POST", url, headers=headers, data={'category': instance_data["id"]})
            response_json = html_to_json.convert(response.text[12:-2].encode().decode('unicode_escape').replace("\\/","/"))
            response_json = response_json["div"][0]["div"]
            score_nm, score_hc = 0, 0
            ACHI_DATA[instance_name] = {}
            ACHI_DATA[instance_name] = {"achievements": {}}

            for element in response_json:
                if element["_attributes"]["id"] in instance_data["achis"].keys():  # check if this element is one of achis we need to check
                    if len(element["div"])==5 and element["div"][4]["_attributes"]["class"][0] == 'date':  # check if theres 5 elements and if 5th is 'date'
                        ACHI_DATA[instance_name]["achievements"][instance_data["achis"][element["_attributes"]["id"]][1]] = element["div"][4]["_value"][7:]
                        if instance_data["achis"][element["_attributes"]["id"]][0] < 5:  # if score for this achi is below 5 i.e. is normal
                            score_nm += instance_data["achis"][element["_attributes"]["id"]][0]  # add to nm score
                        else:
                            score_hc += instance_data["achis"][element["_attributes"]["id"]][0]  # add to hc score

            # ACHI_DATA is: ICC10 (12/12) (4/12 HC)
            # the HC score is divided by 10, because the scores in the dictionary are 10/20/30 etc
            ACHI_DATA[instance_name + " normal"] = str(int(score_nm))
            ACHI_DATA[instance_name + " heroic"] = str(int(score_hc/10))



        # scrape statistics for boss kills
        url = BASE_URL + "/statistics"
        for instance_name, instance_data in TO_CHECK_DUNG.items():
            response = requests.request("POST", url, headers=HEADERS, data={'category': instance_data["id"]})
            # response.text[347:-716]  - cut off unnecessary data
            response_json = html_to_json.convert(response.text[353:-723].encode().decode('unicode_escape').replace("\\/","/"))["tr"]
            response_json = response_json[16:-6]  # skip all statistics rows except ICC

            # Start from 8:/9:/10:/11: to skip LDW and Marrowgar - may be reverted when Warmane fixes their website
            output = [
                {
                    "name": "ICC10 normal",
                    "data": response_json[8::4]
                },
                {
                    "name": "ICC10 heroic",
                    "data": response_json[9::4]
                },
                {
                    "name": "ICC25 normal",
                    "data": response_json[10::4]
                },
                {
                    "name": "ICC25 heroic",
                    "data": response_json[11::4]
                },
            ]


            for instance_data in output:  # roll through instances gathered from webpage
                counter = 0  # initialize counter for bosses killed
                if ACHI_DATA[instance_data['name']] == "4":  # check if there's 4 for Lower ICC for given icc difficulty from previous check
                    counter += 2  # if yes, means dude has killed all 4 bosses from Lower ICC -> add 2 points - not 4 because Gunship and DBS are covered by statistics check
                for boss in instance_data["data"]:  # roll through each boss row in this difficulty
                    if boss["td"][1]["_value"] != "- -":  # if value is not - - it means that given person killed given boss
                        counter += 1  # add 1 to the boss kills score
                        if instance_data['name'][-6:] == "heroic" and boss["td"][0]["_value"][:6] == "Fester" and ACHI_DATA[instance_data['name']] == "0": # if its heroic and boss is Fester and there's no achi for lower ICC
                            counter += 1  # add 1 since if someone killed Fester, they most probably also killed Marrowgar
                ANSWER[instance_data['name']] = str(counter)  # store kill count in answer
				
				

        # scrape items
        url = BASE_URL + "/profile"
        response = requests.get(url)
        response_json = html_to_json.convert(response.text.encode().decode('unicode_escape').replace("\\/","/").replace("\n",""))
        item_data = response_json["html"][0]["body"][0]["div"][2]["div"][4]["div"][0]["div"][1]["div"][0]["div"][1]["div"][2]["div"][0]["div"][0]["div"][:3]  # a long ptath to reach the item data
        
        item_ids = []
        item_level_avg = 0

        for items_side in item_data:  # iterate through side (left, right, bottom - as visibel in webpage)
            for item in items_side["div"][:-1]:  # get all items except last, which is useless
                if "rel" in item["div"][0]["a"][0]["_attributes"]:  # if rel is here, then an item is here
                    item_data = item["div"][0]["a"][0]["_attributes"]["rel"][0]  # get the item data
                    item_data = item_data.replace("item=","").replace("ench=","").replace("gems=","").split("&")  # remove unnecessary words and split by & into list of attributes - id, ench id, gems id's
                    item_ids.append(item_data[0])  # add to the list
                else:
                    print("No " + item["div"][0]["_attributes"]["data-tooltip"])

        dbcursor = db.cursor()
        sql_query = "SELECT ItemLevel FROM item_template WHERE ItemLevel > 1 AND entry IN ({item_ids})".format(item_ids=", ".join(item_ids))  # get all item levels from the SQL DB
        dbcursor.execute(sql_query)
        item_levels_all = dbcursor.fetchall()
        for item_level in item_levels_all:  # iterate through the items
            item_level_avg += item_level[0]  # add each item's ilvl
		
        item_level_avg = round(item_level_avg/14)  # divide by 14 and round 
        ANSWER["ilvl"] = item_level_avg


    print("Scraped data for " + QUERY)
    return ANSWER

# scrapeCall("character","Bestworldx")