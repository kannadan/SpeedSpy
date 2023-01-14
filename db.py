import sqlite3

def connectdb():
    return sqlite3.connect('speedrunners.db')

def createTables():
    conn = connectdb()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS runners(
                   userid TEXT PRIMARY KEY,
                   name TEXT);
                """)
    cur.execute("""CREATE TABLE IF NOT EXISTS runs(
                   runid TEXT NOT NULL,
                   userid TEXT NOT NULL,
                   place INT,
                   game TEXT,
                   category TEXT,
                   time TEXT,
                   categoryid TEXT,
                   subCategories TEXT,
                   gameid TEXT,
                   runners INT,
                   wr TEXT,
                   link TEXT,
                   wrStatus TEXT DEFAULT 'INAPPLICAPLE',
                   verified,
                   PRIMARY KEY(runid, userid));
                """)
    conn.commit()
    conn.close()

def dropRuns():
    conn = connectdb()
    cur = conn.cursor()
    cur.execute("""DROP TABLE runs; """)

    conn.commit()
    conn.close()


def insertRunner(id, name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO runners(userid, name)
                        VALUES(?, ?);""", (id, name))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def updateRunner(id, name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" UPDATE runners
                        SET name = ?
                        WHERE userid=?; """, (name, id))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def insertrun(run):
    """
        rundata:
            runid       id of run
            userid      user id
            place       position in category
            game        game name
            category    category name. Includes sub-categories
            time        run time
            catid       id of main category
            subCats     ids of subcategories in format <sub categoryid>=<sub category choice>, ...
            gameid      id of game
            runners     Amount of runners for category
            wr          world record time
            links       link to run
            wrStatus    for meta competition
            verified    Time run was verified. If wr, time when first wr was verified
    """
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO runs(runid, userid, place, game, category, time, categoryid, subCategories, gameid, runners, wr, link, wrStatus, verified)
                        VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""",
                                (run["runid"], run["userid"], run["place"],
                                 run["game"], run["category"], run["time"],
                                 run["catid"], run["subCats"], run["gameid"],
                                 run["totalruns"], run["wr"], run["link"], 
                                 run["wrStatus"], run["verified"]))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def updaterun(run):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" UPDATE runs
                        SET place = ?, runners = ?, wr = ?, wrStatus = ?
                        WHERE runid=?; """, (run["place"], run["totalruns"], run["wr"], run["wrStatus"], run["runid"]))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def deleterun(runid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM runs
                        WHERE runid=? """, (runid, ) )
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def deleteRunner(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM runners
                        WHERE userid=? """, (userid, ) )
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def getAllruns():
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM runs; """)
        result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

def getAllMetaruns():
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM runs WHERE wrStatus <> 'INAPPLICAPLE' ORDER BY userid ASC; """)
        result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

def getUserruns(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM runs WHERE userid=?; """, (userid, ))
        result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

def getRunner(name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM runners WHERE name=?; """, (name, ))
        result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

def getRunnerName(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT name FROM runners WHERE userid=?; """, (userid, ))
        result = cur.fetchone()
        if conn:
            conn.close()
        if result:
            return result[0]
        else:
            return None
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

def getAllRunners():
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM runners; """)
        result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()

if __name__ == "__main__":
    pass
