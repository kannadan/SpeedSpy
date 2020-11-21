import sqlite3


def connectdb():
    return sqlite3.connect('speedrunners.db')


def create_tables(guild_id):
    conn = connectdb()
    cur = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS whitelist_%s(
                   userid TEXT PRIMARY KEY,
                   name TEXT);
                """ % guild_id)
    cur.execute("""CREATE TABLE IF NOT EXISTS blacklist_%s(
                   name TEXT PRIMARY KEY);
                """ % guild_id)
    cur.execute("""CREATE TABLE IF NOT EXISTS runs_%s(
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
                """ % guild_id)
    conn.commit()
    conn.close()


def drop_runs(guild_id):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute("""DROP TABLE IF EXISTS runs_%s; """ % guild_id)
    except Exception as e:
        print("Exception in _query_drop_runs: %s" % e)
    conn.commit()
    conn.close()


def insert_whitelist(id, name, guild_id):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO whitelist_%s(userid, name)
                        VALUES(?, ?);""" % guild_id, (id, name))
    except Exception as e:
        print("Exception in _query_insert_whitelist: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def insert_blacklist(name, guild_id):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO blacklist_%s(name)
                        VALUES(?);""" % guild_id, (name, ))
    except Exception as e:
        print("Exception in _query_insert_blacklist: %s" % e)
    if conn:
        conn.commit()
        conn.close()


def insertrun(run, guild_id):
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
        cur.execute(""" INSERT INTO runs_%s(runid, userid, place, game, category, time, categoryid, subCategories, gameid, runners, wr, link)
                    VALUES(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);""" % guild_id, (
                    run["runid"], run["userid"], run["place"],
                    run["game"], run["category"], run["time"],
                    run["catid"], run["subCats"], run["gameid"],
                    run["totalruns"], run["wr"], run["link"]))
    except Exception as e:
        print("Exception in _query_insertrun: %s" % e)
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
        print("Exception in _query_updaterun: %s" % e)
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
        print("Exception in _query_deleterun: %s" % e)
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
        print("Exception in _query_deletewhite: %s" % e)
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
        print("Exception in _query_deleteblack: %s" % e)
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
        print("Exception in _query_getallruns: %s" % e)
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
        print("Exception in _query_getuserruns: %s" % e)
    if conn:
        conn.close()


def getuser(name, guild_id):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" SELECT * FROM whitelist_%s WHERE name=?; """ % guild_id, (name, ))
        result = cur.fetchall()
        if not result:
            cur.execute(""" SELECT * FROM blacklist_%s WHERE name=?; """ % guild_id, (name, ))
            result = cur.fetchall()
        if conn:
            conn.close()
        return result
    except Exception as e:
        print("Exception in _query_get_user: %s" % e)
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
        print("Exception in _query_get_user_name: %s" % e)
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
        print("Exception in _query_getallwhite: %s" % e)
    if conn:
        conn.close()


if __name__ == "__main__":
    pass
