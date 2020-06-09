import json
from urllib.request import urlopen

usersUrl = 'https://www.speedrun.com/api/v1/users?name='
gamesUrl = 'https://www.speedrun.com/api/v1/games/'

def getUser(username):
    user = json.load(urlopen(usersUrl + username))
    #print(user["data"][0]["id"])
    if user["data"]:
        if user["pagination"]["size"] != 1:
            for u in user["data"]:
                if username.lower() == u["names"]["international"].lower():
                    return u
        else:
            return user["data"][0]
    return None

def getBest(user):
    bestLink = next((item for item in user["links"] if item["rel"] == "personal-bests"), None)
    personal_bests = json.load(urlopen(bestLink["uri"]))
    return personal_bests["data"]

def parsePB(pbs, userid):
    parsedList = []

    for a in pbs:
        if a["run"]["level"] != None:
            continue
        result = {"place" : int(a["place"]), "userid" : userid, "runid": a["run"]["id"]}
        game = json.load(urlopen(gamesUrl + a["run"]["game"]))
        result["game"] = game["data"]["names"]["international"]
        categories = json.load(urlopen(gamesUrl + a["run"]["game"] + "/categories"))
        category = next((item for item in categories["data"] if item["id"] == a["run"]["category"]), None)
        result["category"] = category["name"]
        parsedList.append(result)
    return parsedList

if __name__ == "__main__":
    pass
