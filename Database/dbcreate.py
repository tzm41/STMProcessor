import sqlite3 as db
import os
from sqlite3 import OperationalError

__author__ = 'Colin Tan'
__version__ = '1.0'


def main():
    dir = os.path.dirname(__file__)
    sqlfilename = os.path.join(dir, 'dbcreate.sql')
    dbfilename = os.path.join(dir, 'database.db')

    fd = open(sqlfilename, 'r')
    sqlFile = fd.read()
    fd.close()

    sqlcmds = sqlFile.split(";")

    conn = db.connect(dbfilename)
    cursor = conn.cursor()

    for cmd in sqlcmds:
        try:
            cursor.execute(cmd)
        except OperationalError:
            print("Command skipped: ", cmd)

    conn.commit()
    cursor.close()
    conn.close()
    return "Finished creating the database"

if __name__ == "__main__":
    main()
