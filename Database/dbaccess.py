import sqlite3 as db

__author__ = 'Colin Tan'
__version__ = 0.8

filename = 'database.db'


# Displays number of spectra in the database.
def displayStudentList():
    conn = db.connect(filename)
    cursor = conn.cursor()
    print
    print "Display number of spectra."
    sql = "SELECT COUNT(*) FROM spectrum"
    cursor.execute(sql)

    data = cursor.fetchall()
    print str(data)
    conn.close()
