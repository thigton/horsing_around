import sqlite3

conn = sqlite3.connect('filename')

c = conn.cursor()
with conn: 
    # put stuff in here so you don't need to commit 
c.execute('INSERT INTO table name  VALUES (:first, :last, :pay)', {'first':x, 'last':x,'pay':x })



conn.commit() # commit changes to database made using execute

conn.close() # close the connection