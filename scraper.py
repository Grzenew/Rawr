#  Third party modules ———————————————————————————————————————————————————————————————————————————
import requests
import html_to_json


#  Exec ——————————————————————————————————————————————————————————————————————————————————————————
def scrapeCall(CATEGORY, QUERY, REALM="Lordaeron"):

    ANSWER = {}
    BASE_URL = "http://armory.warmane.com/character/{character}/{realm}/".format(character=QUERY, realm=REALM)
    TO_CHECK = {
        "ICC25": {
            "id": 15042,
            "achis": {
                # NM
                "ach4604": [4, "Lower"], #  4 bosses - lower
                "ach4605": [3, "Plague"], #  3 bosses - plague
                "ach4606": [2, "Blood"], #  2 bosses - blood
                "ach4607": [2, "Frost"], #  2 bosses - frost
                "ach4608": [1, "LK"],  #  1 - big boye
                # HC
                "ach4632": [40, "Lower HC"], #  4 bosses - lower
                "ach4633": [30, "Plague HC"], #  3 bosses - plague
                "ach4634": [20, "Blood HC"], #  2 bosses - blood
                "ach4635": [20, "Frost HC"], #  2 bosses - frost
                "ach4637": [10, "LK HC"],  #  1 - big boye
            },
        },
        "ICC10": {
            "id": 15041,
            "achis": {
                # NM
                "ach4531": [4, "Lower"], #  4 bosses - lower
                "ach4528": [3, "Plague"], #  3 bosses - plague
                "ach4529": [2, "Blood"], #  2 bosses - blood
                "ach4527": [2, "Frost"], #  2 bosses - frost
                "ach4532": [1, "LK"],  #  1 - big boye
                # HC
                "ach4628": [40, "Lower HC"], #  4 bosses - lower
                "ach4629": [30, "Plague HC"], #  3 bosses - plague
                "ach4630": [20, "Blood HC"], #  2 bosses - blood
                "ach4631": [20, "Frost HC"], #  2 bosses - frost
                "ach4636": [10, "LK HC"]  #  1 - big boye
            }
        }
    }

    if CATEGORY=="character":

        # scrape achievements
        url = BASE_URL + "/achievements"

        for instance_name, instance_data in TO_CHECK.items():
            headers = {'Authorization': 'Bearer 05f7544e468d6067a914a781660486a9612df4478e', 'Cookie': 'PHPSESSID=k3mkdkk1be86l5kr7bu2th5chn'}
            response = requests.request("POST", url, headers=headers, data={'category': instance_data["id"]})
            response_json = html_to_json.convert(response.text[12:-2].encode().decode('unicode_escape').replace("\\/","/"))
            response_json = response_json["div"][0]["div"]
            score_nm, score_hc = 0, 0
            ANSWER[instance_name] = {}
            ANSWER[instance_name] = {"achievements": {}}

            for element in response_json:
                if element["_attributes"]["id"] in instance_data["achis"].keys():  # check if this element is one of achis we need to check
                    if len(element["div"])==5 and element["div"][4]["_attributes"]["class"][0] == 'date':  # check if theres 5 elements and if 5th is 'date'
                        ANSWER[instance_name]["achievements"][instance_data["achis"][element["_attributes"]["id"]][1]] = element["div"][4]["_value"][7:]
                        if instance_data["achis"][element["_attributes"]["id"]][0] < 5:  # if score for this achi is below 5 i.e. is normal
                            score_nm += instance_data["achis"][element["_attributes"]["id"]][0]  # add to nm score
                        else:
                            score_hc += instance_data["achis"][element["_attributes"]["id"]][0]  # add to hc score

            # answer is: ICC10 (12/12) (4/12 HC)
            # the HC score is divided by 10, because the scores in the dictionary are 10/20/30 etc
            ANSWER[instance_name]["score_nm"] = str(int(score_nm))
            ANSWER[instance_name]["score_hc"] = str(int(score_hc/10))
            #ANSWER += instance_name + " (" + str(int(score_nm)) + "/12) (" + str(int(score_hc/10)) + "/12 HC)" + "\n"

    print("Scraped data for " + QUERY)            
    return ANSWER