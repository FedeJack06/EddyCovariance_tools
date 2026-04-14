import duckdb as db

con = db.connect("trieste_campaign.db")

con.sql("select * from sonic_6551 order by datetime desc limit 10").show()
#con.sql("select * from sonic_26458 where u_1 is null").show()
#con.sql("select count(1) from sonic_4175").show()

con.close()