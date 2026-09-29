import duckdb, os
os.chdir(os.environ.get('DATA_DIR', '.'))
con=duckdb.connect()
def q(s): print(s.strip()[:120]); print(con.sql(s).df().to_string(max_rows=80)); print()
r="read_csv('{}', all_varchar=true, header=true)"
q(f"select KCP, SP, count(*) n, median(try_cast(GR1 as double)) med from {r.format('1t_god/2021/2021_1t_god.csv')} group by all order by n desc limit 40")
q(f"select KCP, SP, count(*) n, median(try_cast(VAL_NUM as double)) med from {r.format('1t_god/2024/sr_1t_god_12_2024.csv')} group by all order by n desc limit 30")
q(f"select KCP, STKD, SP, count(*) n, median(try_cast(GR1 as double)) med from {r.format('1t_kv/2021/1kv/1kv2021.csv')} group by all order by n desc limit 30")
q(f"select KCP, SP, count(*) n, median(try_cast(VAL_NUM as double)) med from {r.format('2t/2023/2_t_oplata_truda_2023.csv')} group by all order by n desc limit 20")
for c in ['ZAN_PR_ST','ZAN_RABOTA','PSK_RABOTA','TE','K','vosr','DH_OBRAZOV','DH_POLRESP']:
    q(f"select {c}, count(*) n from {r.format('t001/2024/baza.csv')} group by 1 order by n desc limit 25")
