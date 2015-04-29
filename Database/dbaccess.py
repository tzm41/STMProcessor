import sqlite3 as db

__author__ = 'Colin Tan'
__version__ = 0.8

filename = 'database.db'


# displays number of spectra in the database.
def displaySpectraNum():
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM SpecData"
    cursor.execute(sql)

    data = cursor.fetchone()
    print("Number of spectra is {}.".format(str(data[0])))
    conn.close()


# get one spectrum from ID
def getSpectrumFromID(id):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE SpecID = ?"
    cursor.execute(sql, (id,))

    data = cursor.fetchone()
    print(data)
    conn.close()


# get spectra from doping
def getSpectrumFromDoping(doping):
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT * FROM SpecData WHERE Doping = ?"
    cursor.execute(sql, (doping,))

    data = cursor.fetchall()
    print(data)
    conn.close()
