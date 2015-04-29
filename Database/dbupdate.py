import sqlite3 as db
import dbapi

__author__ = 'Colin Tan'
__version__ = 0.8

filename = 'database.db'


# insert one spectrum
def insertSpectrum(xseries, yseries, doping):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getID = "SELECT max(SpecID) FROM SpecData"
    cursor.execute(getID)
    id = cursor.fetchone()[0] + 1
    xtext = dbapi.seriesToText(xseries)
    ytext = dbapi.seriesToText(yseries)
    insertSpec = """INSERT INTO SpecData
        (SpecID, xdata, ydata, Doping)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(insertSpec, (id, xtext, ytext, doping))
    conn.commit()
    conn.close()


# insert gap data
def insertGap(SpecID, gapSize, boxcarWidth):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "INSERT OR REPLACE INTO GapData VALUES (?, ?, ?)"
    cursor.execute(sql, (SpecID, gapSize, boxcarWidth))
    conn.commit()
    conn.close()
