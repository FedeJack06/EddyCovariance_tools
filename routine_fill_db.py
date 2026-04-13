import duckdb as db
import src.pre_processing as pp
import os

db_file = "trieste_campaign.db"
in_dir = "/media/federico/BackupFoto/trieste_campaign/"
stations = ["26458","4175","26428","4174","6551"]

con = db.connect(db_file)

for station in stations:
    print(f"\n  STATION {station}")
    # set column names
    if station == "26458":
        field_sonic =  ['u_1', 'v_1', 'w_1', 'Ts_1', 'u_2', 'v_2', 'w_2', 'Ts_2']
        field_slow = ['AirTC1','RH1','AirTC2','RH2']
        db_sonic_col =  'u_1, v_1, w_1, ts_1, u_2, v_2, w_2, ts_2'
        db_slow_col = 't_1 , rh_1, t_2, rh_2'
    else:
        field_sonic =  ['u_1', 'v_1', 'w_1', 'Ts_1']
        field_slow = ['AirTC1','RH1']
        db_sonic_col =  'u_1, v_1, w_1, ts_1'
        db_slow_col = 't_1 , rh_1'
    
    # column names for insert query
    df_sonic_col = ", ".join(field_sonic)
    df_slow_col = ", ".join(field_slow)

    ################################################################
    ################# import files #################################
    path = in_dir+station+"_sd"
    
    ################# SONIC
    try:
        start_name = "TOA5_"+station+"_sonic"
        files = sorted([f for f in os.listdir(path) if f.startswith(start_name) and f.endswith('.dat')])
        print(f"Find {len(files)} file {start_name} in {path}\n")

    except FileNotFoundError:
        print(f"Error: folder {path} not found. Skip station...")
        files = []
        continue

    for file in files:
        filepath = os.path.join(path, file)
 
        sonic_df, h_sonic = pp.import_file(filepath, measure_fields=field_sonic, clear_df=True)

        #print(sonic_df)

        ############# 999.99 as NAN in Sonic file
        sonic_df = sonic_df.mask(sonic_df > 999)

        ############# remove index
        sonic_df.reset_index(inplace=True, names="index")

        ##################################################################
        ################ import in duck database #########################
        try:
            sonic_insert = con.execute(f"""
                INSERT INTO sonic_{station} (datetime, {db_sonic_col})
                SELECT index, {df_sonic_col} FROM sonic_df
            """).fetchone()[0]

            print(f"Sonic: Query OK, {sonic_insert} row(s) affected")

        except db.Error as e:
            print(f"Error Sonic: {e}")

    ###########################################
    ################# SLOW ####################
    try:
        start_name = "TOA5_"+station+"_slow"
        files = sorted([f for f in os.listdir(path) if f.startswith(start_name) and f.endswith('.dat')])
        print(f"Find {len(files)} file {start_name} in {path}\n")

    except FileNotFoundError:
        print(f"Error: folder {path} not found. Skip station...")
        files = []
        continue

    for file in files:
        filepath = os.path.join(path, file)

        slow_df, h_slow = pp.import_file(filepath, measure_fields=field_slow, clear_df=True)

        #print(slow_df)

        ############# remove index
        slow_df.reset_index(inplace=True, names="index")

        ##################################################################
        ################ import in duck database #########################
        try:
            slow_insert = con.execute(f"""
                INSERT INTO slow_{station} (datetime, {db_slow_col})
                SELECT index, {df_slow_col} FROM slow_df
            """).fetchone()[0]
            print(f"Slow: Query OK, {slow_insert} row(s) affected")

        except db.Error as e:
            print(f"Error Slow: {e}")

    ###########################################
    ################# STAT ####################
    try:
        start_name = "TOA5_"+station+"_stat"
        files = sorted([f for f in os.listdir(path) if f.startswith(start_name) and f.endswith('.dat')])
        print(f"Find {len(files)} file {start_name} in {path}\n")

    except FileNotFoundError:
        print(f"Error: folder {path} not found. Skip station...")
        files = []
        continue

    for file in files:
        filepath = os.path.join(path, file)

        stat_df, h_stat = pp.import_file(filepath, measure_fields=['BattV_Min'])

        #print(stat_df)

        ############# remove index
        stat_df.reset_index(inplace=True, names="index")

        ##################################################################
        ################ import in duck database #########################
        try:
            stat_insert = con.execute(f"""
                INSERT INTO stat_{station} (datetime, battVmin, card_status)
                SELECT index, BattV_Min, CardStatus FROM stat_df
            """).fetchone()[0]
            print(f"Stat: Query OK, {stat_insert} row(s) affected")

        except db.Error as e:
            print(f"Error Stat: {e}")

con.close()