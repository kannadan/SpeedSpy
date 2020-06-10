import sqlite3

def connectdb():
    return sqlite3.connect('speedrunners.db')

def createTables():
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
                   runid TEXT PRIMARY KEY,
                   userid TEXT,
                   place INT,
                   game TEXT,
                   category TEXT);
                """)
    conn.commit()
    conn.close()



def insertWhitelist(id, name):
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

def insertBlacklist(name):
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
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" INSERT INTO runs(runid, userid, place, game, category)
                        VALUES(?, ?, ?, ?, ?);""", (run["runid"], run["userid"], run["place"],
                                                    run["game"], run["category"]))
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
                        WHERE runid=? """, (runid, ) )
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def deleteWhite(userid):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM whitelist
                        WHERE userid=? """, (userid, ) )
    except Exception as e:
        print("Exception in _query: %s" % e)
    if conn:
        conn.commit()
        conn.close()

def deleteBlack(name):
    conn = connectdb()
    cur = conn.cursor()
    try:
        cur.execute(""" DELETE FROM blacklist
                        WHERE name=? """, (name, ) )
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

def getUser(name):
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

def getUserName(userid):
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

def getAllWhite():
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
