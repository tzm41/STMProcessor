import sqlite3 as db

conn = db.connect("database.db")
cursor = conn.cursor()

sql = """DROP TABLE IF EXISTS spectrum"""

cursor.execute(sql)

sql = """CREATE TABLE spectrum
(
id int PRIMARY KEY,
x text,
y text
)
"""

cursor.execute(sql)

conn.commit()
cursor.close()
conn.close()
print "Finished creating the database"
