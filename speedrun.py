import json
from urllib.request import urlopen
from dateutil.relativedelta import relativedelta
from random import randrange

usersUrl = 'https://www.speedrun.com/api/v1/users?max=200&name='
gamesUrl = 'https://www.speedrun.com/api/v1/games/'
categoryUrl = 'https://www.speedrun.com/api/v1/categories/'
leaderboardurl = "https://www.speedrun.com/api/v1/leaderboards/"    # ad gameid/category/catid?var-subcatvariables
platformUrl = 'https://www.speedrun.com/api/v1/platforms/'

def getUser(username):
    try:
        user = json.load(urlopen(usersUrl + username))
    except UnicodeEncodeError as e:
        print("Unicode error")
        return None
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
        result = {"place" : int(a["place"]), "userid" : userid, "runid": a["run"]["id"], "gameid": a["run"]["game"]}
        time = a["run"]["times"]["primary_t"]

        result["time"] = getTimeString(time)
        game = json.load(urlopen(gamesUrl + a["run"]["game"]))
        result["game"] = game["data"]["names"]["international"]
        catData = getCategories(a)
        result["category"] = catData["ctext"]
        result["catid"] = catData["id"]
        result["subCats"] = catData["subs"]
        lbData = getLeaderboardData(result["gameid"], catData["id"], catData["subs"])
        result["totalruns"] = lbData["total"]
        result["wr"] = lbData["wr"]
        result["link"] = a["run"]["weblink"]
        parsedList.append(result)
    return parsedList

def getTimeString(timeseconds):
    time = relativedelta(seconds=timeseconds)
    time.hours = time.hours + time.days*24
    timestr = f'{time.hours}h {int(time.minutes):02d}m'
    if isinstance(time.seconds, int):
        timestr = timestr + f' {time.seconds:02d}s'
    else:
        timestr = timestr + f' {time.seconds:06.3f}s'
    return timestr

def getCategories(run):
    categories = json.load(urlopen(gamesUrl + run["run"]["game"] + "/categories"))
    category = next((item for item in categories["data"] if item["id"] == run["run"]["category"]), None)
    result = {"name": category["name"], "id": category["id"]}
    ctext = category["name"]
    subs = ""
    if run["run"]["values"]:
        variables = json.load(urlopen(categoryUrl + run["run"]["category"] + "/variables"))
        for d in variables["data"]:
            if d["is-subcategory"]:
                ctext = ctext + ", " + d["values"]["values"][run["run"]["values"][d["id"]]]["label"]  #this json is nightmarish. d ->value->value->a variable id -> that id's label
                if subs:
                    subs = subs + "," + d["id"] + "=" + run["run"]["values"][d["id"]]
                else:
                    subs = subs + d["id"] + "=" + run["run"]["values"][d["id"]]
    result["ctext"] = ctext
    result["subs"] = subs
    return result

def getLeaderboardData(gameid, catid, subcats):
    """
    return number of players in category, WR time
    """
    url = leaderboardurl + gameid + "/category/" + catid + "?"
    if subcats:
        catlist = subcats.split(",")
        for cat in catlist:
            url = url + "var-" + cat + "&"
    lb = json.load(urlopen(url))
    total = len(lb["data"]["runs"])
    wr = getTimeString(lb["data"]["runs"][0]["run"]["times"]["primary_t"])
    return {"total": total, "wr": wr}

def getRandomGame():
    offset = randrange(0,25000)
    url = f'{gamesUrl[:-1]}?offset={offset}&_bulk=yes'
    lb = json.load(urlopen(url))
    if(len(lb["data"]) == 0):
        url = lb["pagination"]["links"][0]["uri"]
        lb = json.load(urlopen(url))
    games = len(lb["data"])
    if(games == 0):
        return 0
    bulkGame = lb["data"][randrange(0, games - 1)]
    url = f'{gamesUrl}{bulkGame["id"]}'
    lb = json.load(urlopen(url))

    platforms = lb["data"]["platforms"]
    plat = 0
    if(len(platforms) > 0):
        pUrl = f'{platformUrl}{platforms[0]}'
        plat = json.load(urlopen(pUrl))
    
    categoryUrl = url + '/categories'    
    catRes = json.load(urlopen(categoryUrl))

    leaderUrl = f'{leaderboardurl}{bulkGame["id"]}/category/{catRes["data"][0]["id"]}'
    wrRes = json.load(urlopen(leaderUrl))
        
    return (lb["data"], plat["data"], catRes["data"][0], wrRes["data"]["runs"])


if __name__ == "__main__":
    user = getUser("kannadan")
    pbs = getBest(user)
    print(parsePB(pbs, user["id"]))
