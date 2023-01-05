import json
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from dateutil.relativedelta import relativedelta
from random import randrange
from datetime import datetime


usersUrl = 'https://www.speedrun.com/api/v1/users'
gamesUrl = 'https://www.speedrun.com/api/v1/games/'
categoryUrl = 'https://www.speedrun.com/api/v1/categories/'
leaderboardurl = "https://www.speedrun.com/api/v1/leaderboards/"    # ad gameid/category/catid?var-subcatvariables
platformUrl = 'https://www.speedrun.com/api/v1/platforms/'

default_wr_status = 'INAPPLICAPLE'

def getTime():
    return datetime.now()

def getRequest(url):
    try:
        results = json.load(urlopen(url))
        return results
    except HTTPError as e:
        print(getTime(), "HttpError {} occured".format(e.code), url)
    except URLError as e:
        print(getTime(), 'URLError occured. Reason: ', e.reason, url)
    except UnicodeEncodeError as e:
        print(getTime(), "Unicode error", url)
    except:
        print(getTime(), "Unknown error", url)
    return None

def getUser(username):

    user = getRequest(usersUrl + "?max=200&lookup=" + username)
    if user == None:
        return None
    #print(getTime(), user["data"][0]["id"])
    if user["data"]:
        if user["pagination"]["size"] != 1:
            for u in user["data"]:
                if username.lower() == u["names"]["international"].lower():
                    return u

        else:
            return user["data"][0]
    return None

def getBest(userId):
    personal_bests = getRequest(usersUrl + "/" + userId + "/personal-bests?embed=game,category.variables")
    if personal_bests is None:
        return []
    return personal_bests["data"]

def parsePB(pbs, userid):
    """
        {
        "place": 1,
        "userid": 123456,
        "runid": 789012,
        "gameid": 135790,
        "time": "01:23:45",
        "game": "Super Mario Bros.",
        "category": "Any%",
        "catid": 13,
        "subCats": ["Glitchless"],
        "totalruns": 100,
        "wr": True,
        "link": "https://www.speedrun.com/run/abcdefg",
        "wrStatus": "INAPPLICAPLE",
        "verified": "2022-01-01T12:34:56Z"
    }
    """
    parsedList = []

    for a in pbs:
        if a["run"]["level"] != None:
            continue
        result = {"place" : int(a["place"]), "userid" : userid, "runid": a["run"]["id"], "gameid": a["run"]["game"]}
        time = a["run"]["times"]["primary_t"]

        result["time"] = getTimeString(time)
        game = a["game"]
        if game is None:
            continue
        result["game"] = game["data"]["names"]["international"]
        catData = getCategories(a, a["category"]["data"])
        if catData is None:
            continue
        result["category"] = catData["ctext"]
        result["catid"] = catData["id"]
        result["subCats"] = catData["subs"]
        lbData = getLeaderboardData(result["gameid"], catData["id"], catData["subs"])
        if lbData is None:
            continue
        result["totalruns"] = lbData["total"]
        result["wr"] = lbData["wr"]
        result["link"] = a["run"]["weblink"]
        result["wrStatus"] = default_wr_status
        result["verified"] = a["run"]["status"]["verify-date"]
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

def getCategories(run, category):
    if category is None:
        return None
    result = {"name": category["name"], "id": category["id"]}
    ctext = category["name"]
    subs = ""
    if run["run"]["values"]:
        variables = category["variables"]
        if variables is None:
            return None
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
    lb = getRequest(url)
    if lb is None:
        return None
    total = len(lb["data"]["runs"])
    wr = getTimeString(lb["data"]["runs"][0]["run"]["times"]["primary_t"])
    return {"total": total, "wr": wr}

def getRandomGame():
    offset = randrange(0,25000)
    url = f'{gamesUrl[:-1]}?offset={offset}&_bulk=yes'
    lb =  getRequest(url)
    if(len(lb["data"]) == 0):
        url = lb["pagination"]["links"][0]["uri"]
        lb = getRequest(url)
    games = len(lb["data"])
    if(games == 0):
        return 0
    bulkGame = lb["data"][randrange(0, games - 1)]
    url = f'{gamesUrl}{bulkGame["id"]}'
    lb = getRequest(url)

    platforms = lb["data"]["platforms"]
    plat = 0
    if(len(platforms) > 0):
        pUrl = f'{platformUrl}{platforms[0]}'
        plat = getRequest(pUrl)

    caturl = url + '/categories'
    catRes = getRequest(caturl)

    catIndex = randrange(0, len(catRes["data"]))
    leaderUrl = f'{leaderboardurl}{bulkGame["id"]}/category/{catRes["data"][catIndex]["id"]}'
    wrRes = getRequest(leaderUrl)

    return (lb["data"], plat["data"], catRes["data"][catIndex], wrRes["data"])


if __name__ == "__main__":
    user = getUser("kannadan")
    pbs = getBest(user)
    print(getTime(), parsePB(pbs, user["id"]))
