import duckdb

source_db = 'trieste_campaign.db'
target_db = 'trieste_campaign_tmp.db'

# 1. Apri una connessione neutra (in-memory)
con = duckdb.connect()

# 2. Collega (ATTACH) entrambi i database alla sessione corrente
con.execute(f"ATTACH '{source_db}' AS source_db;")
# Se target.db non esiste, DuckDB creerà automaticamente un file vuoto
con.execute(f"ATTACH '{target_db}' AS target_db;")

# 3. Copia l'intero database specificando di copiare SOLO la struttura (SCHEMA)
con.execute("COPY FROM DATABASE source_db TO target_db (SCHEMA);")

con.close()

print(f"Struttura di '{source_db}' clonata con successo in '{target_db}'!")