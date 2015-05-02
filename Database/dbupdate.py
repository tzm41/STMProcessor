import sqlite3 as db
import os
import dbapi

__author__ = 'Colin Tan'
__version__ = '0.8'

dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'database.db')


# insert one spectrum
def insertSpectrum(xseries, yseries, doping):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getID = "SELECT max(SpecID) FROM SpecData"
    cursor.execute(getID)
    # new ID follows the current ID
    newID = cursor.fetchone()[0] + 1
    xtext = dbapi.seriesToText(xseries)
    ytext = dbapi.seriesToText(yseries)
    insertSpec = """INSERT INTO SpecData
        (SpecID, xdata, ydata, Doping)
        VALUES (?, ?, ?, ?)
    """
    cursor.execute(insertSpec, (newID, xtext, ytext, doping))
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


# insert one average spectrum
# withe its x series, y series, min and max of gap size in the process
# and the number of spectra averaged into this spectrum
def insertAveSpectrum(xseries, yseries, gapMin, gapMax, numAve, specID=None):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getID = "SELECT max(AveID) FROM AveSpec"
    cursor.execute(getID)
    # new ID follows the current ID
    newID = cursor.fetchone()[0] + 1
    xtext = dbapi.seriesToText(xseries)
    ytext = dbapi.seriesToText(yseries)
    insertSpec = """INSERT INTO AveSpec
        VALUES (?, ?, ?, ?, ?, ?)
    """
    cursor.execute(insertSpec, (newID, numAve, gapMin, gapMax, xtext, ytext))
    conn.commit()
    conn.close()


# insert a pair of spectrum and its group average spectrum
def insertSpecAvePair(specID, aveID):
    conn = db.current(filename)
    cursor = conn.cursor()
    sql = "INSERT INTO SpecAvePair VALUES (?, ?)"
    cursor.execute(sql, (specID, aveID))
    conn.commit()
    conn.close()
