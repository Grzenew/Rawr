# Item Types - https://trinitycore.atlassian.net/wiki/spaces/tc/pages/2130222/item+template


#  Third party modules ———————————————————————————————————————————————————————————————————————————
import requests
import html_to_json
import mysql.connector as mysql
import logging as log
import math


# Settings ———————————————————————————————————————————————————————————————————————————————————————
db = mysql.connect(
    host = "localhost",
    user = "user",
    passwd = "icoteraz2010",
	database="items"
)


# Exec ————————————————————————————————————————————————————————————————————————————————————————————
def scrapeCall(CATEGORY, QUERY, IS_HUNTER=False, REALM="Lordaeron"):

    try:

        ACHI_DATA = {}
        ANSWER = {}
        BASE_URL = "http://armory.warmane.com/character/{character}/{realm}/".format(character=QUERY, realm=REALM)
        HEADERS = {'Authorization': 'Bearer 05f7544e468d6067a914a781660486a9612df4478e', 'Cookie': 'PHPSESSID=k3mkdkk1be86l5kr7bu2th5chn'}

        GS_Formula = {
            "A": {
                4: { "A": 91.4500, "B": 0.6500 },
                3: { "A": 81.3750, "B": 0.8125 },
                2: { "A": 73.0000, "B": 1.0000 }
            },
            "B": {
                4: { "A": 26.0000, "B": 1.2000 },
                3: { "A": 0.7500, "B": 1.8000 },
                2: { "A": 8.0000, "B": 2.0000 },
                1: { "A": 0.0000, "B": 2.2500 }
            }
        }

        ENCHANTABLE = [16,17,18,36,1,3,5,7,8,9,10,15]

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
        
        ITEM_SLOTS = [
            'head',     # 1
            'neck',     # 2
            'shoulders',# 3
            'cloak',    # 16
            'chest',     # 5, 20
            'shirt',
            'tabard',
            'bracers',   # 8
            'hands',    # 10
            'belt',     # 6
            'legs',     # 7
            'boots',    # 8
            'ring',     # 11
            'ring2',    # 11
            'trinket',  # 12
            'trinket2', # 12
            'mainhand', # 21
            'offhand',  # 23
            'idol'      # 2
        ]
     
        ITEM_TYPES = {
            1: 1,
            2: 0.5625,
            3: 0.75,
            5: 1,
            6: 0.75,
            7: 1,
            8: 0.75,
            9: 0.5625,
            10: 0.75,
            11: 0.5625,
            12: 0.5625,
            13: 1, # axe
            14: 1, # shield
            15: 0.3164, # bow
            16: 0.5625,
            17: 2, # 2-hand weapon
            20: 1,
            21: 1,
            23: 1,
            25: 0.3164,
            26: 0.3164, # bow
            28: 0.3164
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
                    fester = False
                    if ACHI_DATA[instance_data['name']] == "4":  # check if there's 4 for Lower ICC for given icc difficulty from previous check
                        counter += 2  # if yes, means dude has killed all 4 bosses from Lower ICC -> add 2 points - not 4 because Gunship and DBS are covered by statistics check
                    for boss in instance_data["data"]:  # roll through each boss row in this difficulty
                        if boss["td"][1]["_value"] != "- -":  # if value is not - - it means that given person killed given boss
                            counter += 1  # add 1 to the boss kills score
                            if not fester and instance_data['name'][-6:] == "heroic" and (boss["td"][0]["_value"][:6] == "Fester" or boss["td"][0]["_value"][:6] == "Victor") and ACHI_DATA[instance_data['name']] == "0": # if "fester" is not true and its heroic and boss is Fester or LK (Victory over...) and there's no achi for lower ICC
                                counter += 1  # add 1 since if someone killed Fester, they most probably also killed Marrowgar
                                fester = True  # remember that fester has been added already
                    ANSWER[instance_data['name']] = str(counter)  # store kill count in answer
                    if len(ANSWER[instance_data['name']]) == 1:
                        ANSWER[instance_data['name']] = " " + ANSWER[instance_data['name']]
                    
                    

            # scrape items
            url = BASE_URL + "/profile"
            response = requests.get(url)
            response_json = html_to_json.convert(response.text.encode().decode('unicode_escape').replace("\\/","/").replace("\n",""))
            item_data = response_json["html"][0]["body"][0]["div"][2]["div"][4]["div"][0]["div"][1]["div"][0]["div"][1]["div"][2]["div"][0]["div"][0]["div"][:3]  # a long path to reach the item data
            
            item_enchanted = []
            item_list = {}
            item_slot = 0
            item_query_dict = {}
            item_list_final = {}

            for items_side in item_data:  # iterate through side (left, right, bottom - as visibel in webpage)
                for item in items_side["div"]:  # get all items except last, which is useless
                    enchanted = False          
                    if "rel" in item["div"][0]["a"][0]["_attributes"]:  # if rel is here, then an item is here
                        item_data = item["div"][0]["a"][0]["_attributes"]["rel"][0]  # get the item data
                        if "ench=" in item_data:
                            enchanted = True
                        item_data = item_data.replace("ench=","").replace("item=","").replace("gems=","").split("&")  # remove unnecessary words and split by & into list of attributes - id, ench id, gems id's
                        if item_slot != 5 and item_slot != 6:
                            item_list.update({item_slot: item_data[0]})
                        if enchanted:
                            item_enchanted.append(item_slot)  # add to the list

                    item_slot += 1  # add to item slot iteration
            
            dbcursor = db.cursor()
            sql_query = "SELECT ItemLevel, Quality, InventoryType, name, entry FROM item_template WHERE ItemLevel > 1 AND entry IN ({item_list})".format(item_list=", ".join(item_list.values()))
            dbcursor.execute(sql_query)
            item_query_all = list(dbcursor.fetchall())

            # iterate through sql query items and convert them into dictionary of ITEM_ID: ITEM_ALL_DATA
            for item_list_single in item_query_all:
                item_query_dict.update({str(item_list_single[4]): item_list_single})

            # iterate through items collected from website and check if the value (i.e. ITEM ID) exists in the 'item_query_dict' - if it does, add the item data to final item list
            for item_single in item_list.items():
                if item_single[1] in item_query_dict:
                    item_list_final.update({item_single[0]: item_query_dict[item_single[1]]})

            # calculate GS
            gs_GearScore = 0
            gs_TitanGrip = False

            for item_list_single in sorted(item_list_final.items(), reverse=True):  # need to reverse the order so that script first checks if offhand is 2h (i.e. titan grip)
                
                # prepare
                gs_QualityScale = 1
                gs_Scale = 1.8618
                gs_ItemSlot = item_list_single[0]
                gs_ItemType = item_list_single[1][2]
                gs_ItemLevel = item_list_single[1][0]
                gs_ItemRarity = item_list_single[1][1]
                gs_Table = {}
                gs_Name = item_list_single[1][3]

                # estimate multipliers according to item rarity
                if gs_ItemRarity == 5:  # legendary
                    gs_QualityScale = 1.3
                    gs_ItemRarity = 4 
                elif gs_ItemRarity == 1 or gs_ItemRarity == 0:  # common/poor
                    gs_QualityScale = 0.005
                    gs_ItemRarity = 2 
                elif gs_ItemRarity == 7:  # heirloom
                    gs_ItemRarity = 3
                    gs_ItemLevel = 187.05

                # if item too low quality
                if gs_ItemLevel > 120:
                    gs_Table = GS_Formula["A"]
                else:
                    gs_Table = GS_Formula["B"]

                # the main calculation
                gs_GearScore_Item = math.floor(((gs_ItemLevel - gs_Table[gs_ItemRarity]["A"]) / gs_Table[gs_ItemRarity]["B"]) * ITEM_TYPES[gs_ItemType] * gs_Scale * gs_QualityScale)

                # titans grip
                if gs_ItemSlot == 17 and gs_ItemType == 17:  # if slot is 17 (offhand) and weapon type is 17 (2h)
                    gs_TitanGrip = True  # remember that its titan grip so that main hand 2h also gets 50% reduced GS
                    gs_GearScore_Item = gs_GearScore_Item * 0.5
                if gs_TitanGrip and gs_ItemSlot == 16 and gs_ItemType == 17:  # if slot is 16 (mainhand) and weapon type is 17 (2h)
                    gs_GearScore_Item = gs_GearScore_Item * 0.5

                # for hunter only
                if IS_HUNTER:  
                    if gs_ItemType == 13:  # one handed weapon
                        gs_GearScore_Item = math.floor(gs_GearScore_Item * 0.3164)
                    elif gs_ItemType == 17: # two handed weapon
                        gs_GearScore_Item = math.floor(gs_GearScore_Item * 0.3164)
                    elif gs_ItemSlot == 18:  # ranged weapon
                        gs_GearScore_Item = math.floor(gs_GearScore_Item * 5.3224)


                # if this item is enchantable and is not found in the 'enchanted' list
                if gs_ItemSlot not in item_enchanted and gs_ItemType in ENCHANTABLE:
                    gs_EnchantPercent = ( math.floor((-2 * ( ITEM_TYPES[gs_ItemType]  )) * 100) / 100 )
                    gs_EnchantPercent = 1 + (gs_EnchantPercent/100)
                    gs_GearScore_Item = gs_EnchantPercent * gs_GearScore_Item
                    
                #print(str(gs_ItemSlot) + " " + str(gs_QualityScale) + ": " + gs_Name + " - type/slot:" + str(gs_ItemType) + "/" + str(gs_ItemSlot) + " - gs:" + str(gs_GearScore_Item) + " - grip?:" + str(gs_TitanGrip))

                # add rounded GS to overall score
                gs_GearScore += math.floor(gs_GearScore_Item)

            ANSWER["gs"] = gs_GearScore
            #print(gs_GearScore)


        print("Scraped data for {} ({})".format(QUERY, IS_HUNTER))
        return ANSWER
        
    except Exception as e:
        print(e)
        log.error(e)


#scrapeCall("character","Frejr",True)
#scrapeCall("character","Neunet",False) # 5855
#scrapeCall("character","Kunefe",False) # 5867
#scrapeCall("character","Myrmiidon",False) # 5517