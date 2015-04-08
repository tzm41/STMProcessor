import sqlite3 as db
from sqlite3 import OperationalError

__author__ = 'Colin Tan'
__version__ = 1.0

fd = open('dbcreate.sql', 'r')
sqlFile = fd.read()
fd.close()

sqlcmds = sqlFile.split(";")

conn = db.connect("database.db")
cursor = conn.cursor()

for cmd in sqlcmds:
    try:
        cursor.execute(cmd)
    except OperationalError, msg:
        print("Command skipped: ", msg)

conn.commit()
cursor.close()
conn.close()
print("Finished creating the database")
