import sqlite3 as db

__author__ = 'Colin Tan'
__version__ = 0.8

filename = 'database.db'


# Displays number of spectra in the database.
def displaySpectraNum():
    conn = db.connect(filename)
    cursor = conn.cursor()
    sql = "SELECT COUNT(*) FROM spectrum"
    cursor.execute(sql)

    data = cursor.fetchone()
    print("\nNumber of spectra is {}.".format(str(data[0])))
    conn.close()
