import sqlite3


def connectdb():
    return sqlite3.connect('speedrunners.db')


def create_tables():
    conn = connectdb()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS whitelist(
                   userid TEXT PRIMARY KEY,
                   name TEXT);
                """)
    cur.execute("""CREATE TABLE IF NOT EXISTS blacklist(
                   name TEXT PRIMARY KEY);
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
                   PRIMARY KEY(runid, userid));
                """)
    conn.commit()
    conn.close()


def drop_runs():
    conn = connectdb()
    cur = conn.cursor()
    cur.execute("""DROP TABLE runs; """)

    conn.commit()
    conn.close()


def insert_whitelist(id, name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO whitelist(userid, name)
                        VALUES(?, ?);""", (id, name))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def insert_blacklist(name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO blacklist(name)
                        VALUES(?);""", (name, ))
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
            links       link to run
    """
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO runs(runid, userid, place, game, category, time, categoryid, subCategories, gameid, runners, wr, link)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""", (
                    run["runid"], run["userid"], run["place"],
                    run["game"], run["category"], run["time"],
                    run["catid"], run["subCats"], run["gameid"],
                    run["totalruns"], run["wr"], run["link"]))
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
                        SET place = ?
                        WHERE runid=?; """, (run["place"], run["runid"]))
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
                        WHERE runid=? """, (runid, ))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def deletewhite(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM whitelist
                        WHERE userid=? """, (userid, ))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def deleteblack(name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM blacklist
                        WHERE name=? """, (name, ))
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def getallruns():
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


def getuserruns(userid):
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


def getuser(name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM whitelist WHERE name=?; """, (name, ))
        result = cur.fetchall()
        if not result:
            cur.execute(""" SELECT * FROM blacklist WHERE name=?; """, (name, ))
            result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.close()


def get_user_name(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT name FROM whitelist WHERE userid=?; """, (userid, ))
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


def getallwhite():
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM whitelist; """)
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
