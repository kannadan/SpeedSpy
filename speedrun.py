import json
from urllib.request import urlopen
from dateutil.relativedelta import relativedelta

users_url = 'https://www.speedrun.com/api/v1/users?max=200&name='
games_url = 'https://www.speedrun.com/api/v1/games/'
category_url = 'https://www.speedrun.com/api/v1/categories/'
leaderboardurl = "https://www.speedrun.com/api/v1/leaderboards/"    # ad gameid/category/catid?var-subcatvariables


def get_user(username):
    try:
        user = json.load(urlopen(users_url + username))
    except UnicodeEncodeError as e:
        print("Unicode error: ", e)
        return None
    # print(user["data"][0]["id"])
    if user["data"]:
        if user["pagination"]["size"] != 1:
            for u in user["data"]:
                if username.lower() == u["names"]["international"].lower():
                    return u
        else:
            return user["data"][0]
    return None


def get_best(user):
    bestlink = next((item for item in user["links"] if item["rel"] == "personal-bests"), None)
    personal_bests = json.load(urlopen(bestlink["uri"]))
    return personal_bests["data"]


def parse_pb(pbs, userid):
    parsedlist = []

    for a in pbs:
        if a["run"]["level"] is not None:
            continue
        result = {"place": int(a["place"]), "userid": userid, "runid": a["run"]["id"], "gameid": a["run"]["game"]}
        time = a["run"]["times"]["primary_t"]

        result["time"] = get_time_string(time)
        game = json.load(urlopen(games_url + a["run"]["game"]))
        result["game"] = game["data"]["names"]["international"]
        cat_data = get_categories(a)
        result["category"] = cat_data["ctext"]
        result["catid"] = cat_data["id"]
        result["subCats"] = cat_data["subs"]
        lb_data = get_lb_data(result["gameid"], cat_data["id"], cat_data["subs"])
        result["totalruns"] = lb_data["total"]
        result["wr"] = lb_data["wr"]
        result["link"] = a["run"]["weblink"]
        parsedlist.append(result)
    return parsedlist


def get_time_string(timeseconds):
    time = relativedelta(seconds=timeseconds)
    time.hours = time.hours + time.days * 24
    timestr = f'{time.hours}h {int(time.minutes):02d}m'
    if isinstance(time.seconds, int):
        timestr = timestr + f' {time.seconds:02d}s'
    else:
        timestr = timestr + f' {time.seconds:06.3f}s'
    return timestr


def get_categories(run):
    categories = json.load(urlopen(games_url + run["run"]["game"] + "/categories"))
    category = next((item for item in categories["data"] if item["id"] == run["run"]["category"]), None)
    result = {"name": category["name"], "id": category["id"]}
    ctext = category["name"]
    subs = ""
    if run["run"]["values"]:
        variables = json.load(urlopen(category_url + run["run"]["category"] + "/variables"))
        for d in variables["data"]:
            if d["is-subcategory"]:
                ctext = ctext + ", " + d["values"]["values"][run["run"]["values"][d["id"]]]["label"]  # this json is nightmarish. d ->value->value->a variable id -> that id's label
                if subs:
                    subs = subs + "," + d["id"] + "=" + run["run"]["values"][d["id"]]
                else:
                    subs = subs + d["id"] + "=" + run["run"]["values"][d["id"]]
    result["ctext"] = ctext
    result["subs"] = subs
    return result


def get_lb_data(gameid, catid, subcats):
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
    wr = get_time_string(lb["data"]["runs"][0]["run"]["times"]["primary_t"])
    return {"total": total, "wr": wr}


if __name__ == "__main__":
    user = get_user("kannadan")
    pbs = get_best(user)
    print(parse_pb(pbs, user["id"]))
