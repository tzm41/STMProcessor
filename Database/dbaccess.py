import sqlite3 as db
import os

__author__ = 'Colin Tan'
__version__ = 0.8

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
def getSpectrumFromID(id):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE SpecID = ?"
    cursor.execute(sql, (id,))

    data = cursor.fetchone()
    conn.close()
    print(data)


# get spectra from doping
def getSpectrumFromDoping(doping):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE Doping = ?"
    cursor.execute(sql, (doping,))

    data = cursor.fetchall()
    conn.close()
    print(data)


# get average spectrum of a spectrum
def getSpecAvePair(specID):
    conn = db.current(filename)
    cursor = conn.cursor()
    getAveID = "SELECT AveID FROM SpecAvePair WHERE SpecID = ?"
    cursor.execute(getAveID, (specID,))
    aveID = cursor.fetchone()[0]

    getAveSpec = "SELECT * FROM AveSpec WHERE AveID = ?"
    cursor.execute(getAveSpec, (aveID))
    data = cursor.fetchall()
    conn.close()
    print(data)
