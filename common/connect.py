import mariadb

conn = mariadb.connect(user="", password="", host="", database="")

cur = conn.cursor()
