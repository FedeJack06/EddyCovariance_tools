import duckdb as db
import src.pre_processing as pp

out_dir = "./data/"
in_dir = "./data/"
station = "26458"

if station == "26458":
    field_sonic =  ['u_1', 'v_1', 'w_1', 'Ts_1', 'u_2', 'v_2', 'w_2', 'Ts_2']
    field_slow = ['AirTC1','RH1','AirTC2','RH2']
else:
    field_sonic =  ['u_1', 'v_1', 'w_1', 'Ts_1']
    field_slow = ['AirTC1','RH1']

slow_df, h_slow = pp.import_file(in_dir+"TOA5_Slow_2026-03-26_00-01-34.dat", measure_fields=field_slow, clear_df=True)
sonic_df, h_sonic = pp.import_file(in_dir+"TOA5_Sonic_2026-03-26_00-03-23.dat", measure_fields=field_sonic, clear_df=True)
stat_df, h_stat = pp.import_file(in_dir+'TOA5_Stat_2026-03-26_00-02-24.dat', measure_fields=['BattV_Min'])

#print(slow_df)
#print(sonic_df)
#print(stat_df)

############# 999.99 as NAN in Sonic file
sonic_df = sonic_df.mask(sonic_df > 999)

############# remove index
slow_df.reset_index(inplace=True)
sonic_df.reset_index(inplace=True)
stat_df.reset_index(inplace=True)

############# import in duck database
con = db.connect("bora.db")

try:
    sonic_insert = con.execute(f"""
        INSERT INTO sonic_{station} (datetime, u_1, v_1, w_1, ts_1, u_2, v_2, w_2, ts_2)
        SELECT TIMESTAMP, u_1, v_1, w_1, Ts_1, u_2, v_2, w_2, Ts_2 FROM sonic_df
    """).fetchone()[0]

    print(f"Sonic: Query OK, {sonic_insert} row(s) affected")

except db.Error as e:
    print(f"Error Sonic: {e}")

try:
    slow_insert = con.execute(f"""
        INSERT INTO slow_{station} (datetime, t_1, rh_1, t_2, rh_2)
        SELECT TIMESTAMP, AirTC1, RH1, AirTC2, RH2 FROM slow_df
    """).fetchone()[0]
    print(f"Slow: Query OK, {slow_insert} row(s) affected")

except db.Error as e:
    print(f"Error Slow: {e}")

try:
    stat_insert = con.execute(f"""
        INSERT INTO stat_{station} (datetime, battVmin, card_status)
        SELECT TIMESTAMP, BattV_Min, CardStatus FROM stat_df
    """).fetchone()[0]
    print(f"Stat: Query OK, {stat_insert} row(s) affected")

except db.Error as e:
    print(f"Error Stat: {e}")

con.close()