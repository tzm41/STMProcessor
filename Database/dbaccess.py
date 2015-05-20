import sqlite3 as db
import os

__author__ = 'Colin Tan'
__version__ = '1.0'

dir = os.path.dirname(__file__)
filename = os.path.join(dir, 'database.db')


# displays number of spectra in the database.
def displaySpectraNum():
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM SpecData"
    cursor.execute(sql)

    data = cursor.fetchone()
    conn.close()
    return data[0]


# get one spectrum from ID
def getSpectrumFromID(specID):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE SpecID = ?"
    cursor.execute(sql, (specID,))

    data = cursor.fetchone()
    conn.close()
    return data


# get spectra from ID range
def getSpectrumFromRange(idl, idh):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE SpecID BETWEEN ? AND ?;"
    cursor.execute(sql, (idl, idh))

    data = cursor.fetchall()
    conn.close()
    return data


# get spectra from doping
def getSpectrumFromDoping(doping):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE Doping = ?"
    cursor.execute(sql, (doping,))

    data = cursor.fetchall()
    conn.close()
    return data


# get spectra from temperature
def getSpectrumFromTemp(temp):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE Temperature = ?"
    cursor.execute(sql, (temp,))

    data = cursor.fetchall()
    conn.close()
    return data


# get average spectrum of a spectrum
def getSpecAvePair(specID):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getAveID = "SELECT AveID FROM SpecAvePair WHERE SpecID = ?"
    cursor.execute(getAveID, (specID,))
    aveID = cursor.fetchone()[0]

    getAveSpec = "SELECT * FROM AveSpec WHERE AveID = ?"
    cursor.execute(getAveSpec, (aveID))
    data = cursor.fetchall()
    conn.close()
    return data


# get average spectra of specific boxcar width
def getAveFromBoxcarWidth(boxcar):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getAve = """SELECT * FROM AveSpec WHERE AveID IN (
            SELECT DISTINCT AveID FROM SpecAvePair
            WHERE SpecID IN (
                SELECT SpecID
                FROM GapData
                WHERE BoxcarWidth = ?
            )
        )"""
    cursor.execute(getAve, (boxcar,))
    data = cursor.fetchall()
    conn.close()
    return data


# get IDs of spectra associated with gap sizes
def specWithGap():
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT SpecID FROM GapData"
    cursor.execute(sql)

    data = cursor.fetchall()
    conn.close()
    data = [row[0] for row in data]
    return data


# get gap size of a spectrum
def getGap(specID):
    conn = db.connect(filename)
    cursor = conn.cursor()
    getGap = "SELECT GapSize FROM GapData WHERE SpecID = ?"
    cursor.execute(getGap, (specID,))
    gap = cursor.fetchone()[0]
    conn.close()
    return gap
