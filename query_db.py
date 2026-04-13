import duckdb as db

con = db.connect("bora.db")

#con.sql("select * from sonic_26458 order by datetime asc limit 10").show()
#con.sql("select * from sonic_26458 where u_1 is null").show()

con.close()