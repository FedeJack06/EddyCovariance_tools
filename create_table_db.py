import duckdb as db

table_name = "stat_26458"

con = db.connect("bora.db")

querySonic = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        datetime DATETIME PRIMARY KEY,
        u_1 DECIMAL(6, 3),
        v_1 DECIMAL(6, 3),
        w_1 DECIMAL(6, 3),
        ts_1 DECIMAL(6, 3),
        u_2 DECIMAL(6, 3),
        v_2 DECIMAL(6, 3),
        w_2 DECIMAL(6, 3),
        ts_2 DECIMAL(6, 3)
    )
"""

querySlow = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        datetime DATETIME PRIMARY KEY,
        t_1 DECIMAL(5, 2),
        rh_1 DECIMAL(5, 2),
        t_2 DECIMAL(5, 2),
        rh_2 DECIMAL(5, 2)
    )
"""

queryStat = f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        datetime DATETIME PRIMARY KEY,
        battVmin DECIMAL(5, 2),
        card_status VARCHAR(10)
    )
"""
#con.execute(f"drop table {table_name}")
con.execute(queryStat)
con.sql("show tables").show()
con.sql(f"show {table_name}").show()
con.close()