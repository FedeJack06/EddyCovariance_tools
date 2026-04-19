import duckdb as db

database = "~/unibo/trieste/trieste_campaign.db"
with db.connect(database) as con:

    #con.sql("describe tables").show()
    #con.sql("select * from sonic_6551 order by datetime desc limit 10").show()
    con.sql("select * from sonic_4175 where u_1 is null").show()
    #con.sql("select count(1) from sonic_4175").show()
    '''con.sql("""
        SELECT *
        FROM (
            SELECT *,
                datetime - lag(datetime) OVER (ORDER BY datetime) AS delta_t
            FROM sonic_26458
        ) subquery
        WHERE delta_t > INTERVAL '50 milliseconds';
    """).show()'''

    con.sql("""SELECT '(' || list_agg(column_name || ' IS NULL', ' OR ') || ')'
FROM information_schema.columns
WHERE table_name = 'sonic_4175';""").show()