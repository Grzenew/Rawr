#  Third party modules ———————————————————————————————————————————————————————————————————————————
import logging as log
import requests
from sys import getsizeof, stdout


#  Settings ——————————————————————————————————————————————————————————————————————————————————————
##  headers are required since api denies bot calls
HEADERS = "{'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.102 Safari/537.36'}"
##  logger config
log.basicConfig(
    filename='rawr.log', 
    filemode='a', 
    format='%(asctime)s %(levelname).4s (%(lineno).3s %(funcName)s)  %(message)s', 
    datefmt='[%Y/%m/%d %H:%M:%S]',
    level=log.INFO)  


#  Exec ——————————————————————————————————————————————————————————————————————————————————————————
def apiCall(CATEGORY, QUERY, REALM="Lordaeron"):
    ANSWER = {}

    try:
        ##  death grip the data
        with requests.get("http://armory.warmane.com/api/{category}/{query}/{realm}/summary".format(category=CATEGORY, query=QUERY, realm=REALM), HEADERS) as result:
            result_array = result.json()  # save JSON response into python object

            ###  if an error was returned
            if "error" in result_array:
                ###  if given thing does not exist
                if result_array["error"][-15:] == "does not exist.":  
                    ANSWER = "doesnt exist"
                    log.info('{} "{}" does not exist.'.format(CATEGORY.capitalize(), QUERY))
                ###  if there was another error
                elif result_array["error"]:
                    ANSWER = "error"
                    log.error('Other error: {}'.format(result_array))

            ###  if there's no response from server
            elif result == "":
                ANSWER = "crash"
                log.error('No answer from server, probably it has crashed.')

            ###  if there has been no error
            else:

                ### Character data called
                if CATEGORY == "character":

                    ### Save the data into a nice dictionary object
                    ANSWER = {
                        "level": result_array["level"],
                        "class": result_array["class"],
                        "guild": result_array["guild"],
                        "specs": "/".join(str(x["tree"]) for x in result_array["talents"]),
                        "race": result_array["race"]
                    }

                    ### Return data and save info to log
                    log.info('Returning {} bytes.'.format(getsizeof(ANSWER)))
                    return ANSWER 


                ###  Guild data called
                elif CATEGORY == "guild":

                    online_counter = 0
                    online_names = []

                    ###  Count online dudes
                    for i in range(int(result_array["membercount"])):  ### loop through the list
                        if result_array["roster"][i]["online"]:  ### if "online" is TRUE
                            online_counter += 1
                            online_names.append(result_array["roster"][i]["name"])  ### also add the nickname to a list

                    ### if there is more than 0 online
                    if online_counter > 0:
                        ANSWER["online_names_list"] = ", ".join(str(x) for x in online_names)

                    ### save the data into a dict
                    ANSWER.update({
                        "name": result_array["name"],
                        "online_counter": online_counter,
                        "membercount": result_array["membercount"]
                    })

                    log.info('Returning {} bytes.'.format(getsizeof(ANSWER)))

    except Exception as e:
        ANSWER = "error"
        log.error(e)

    return ANSWER

#print(apiCall("guild", "Lions Pridxe"))
#print(apiCall("character", "Gotfai"))