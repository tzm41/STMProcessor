import sqlite3 as db
from sqlite3 import OperationalError

__author__ = 'Colin Tan'
__version__ = 1.0

conn = db.connect("database.db")
cursor = conn.cursor()

sql = """DROP TABLE IF EXISTS spectrum"""

cursor.execute(sql)

sql = """CREATE TABLE spectrum
(
id int PRIMARY KEY AUTO_INCREMENT,
x text,
y text
)
"""

cursor.execute(sql)

conn.commit()
cursor.close()
conn.close()
print "Finished creating the database"
