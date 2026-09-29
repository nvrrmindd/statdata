import duckdb, os
os.chdir(os.environ.get('DATA_DIR', '.'))
con=duckdb.connect()
def q(s): print(s.strip()[:110]); print(con.sql(s).df().to_string(max_rows=60)); print()
R=lambda p: f"read_csv('{p}', all_varchar=true, header=true, quote='\"')"
q(f"select min(try_cast(vosr as int)), max(try_cast(vosr as int)), count(*) from {R('t001/2023/baza.csv')}")
q(f"select SP, count(*), median(try_cast(VAL_NUM as double)) from {R('1t_kv/2024/4kv/1t_kv_12_2024.csv')} where KCP='252101' and STKD='1' group by 1")
q(f"select KCP, SP, STKD, count(*) from {R('1t_kv/2024/4kv/1t_kv_12_2024.csv')} group by all order by 4 desc limit 8")
q(f"select SUO, count(*) n, median(try_cast(VAL_NUM as double)) w from {R('2t/2023/2_t_oplata_truda_2023.csv')} where KCP='252101' group by 1 order by 1")
q(f"select count(distinct ID) from {R('2t/2023/2_t_oplata_truda_2023.csv')}")
for y in [2021,2022,2023,2024]:
    f={2021:'1t_god/2021/2021_1t_god.csv',2022:'1t_god/2022/2022_1t_god.csv',2023:'1t_god/2023/2023_1t_god.csv',2024:'1t_god/2024/sr_1t_god_12_2024.csv'}[y]
    q(f"select {y} y, count(distinct ID) ids, min(length(KATO)) , max(length(KATO)) from {R(f)}")
q(f"select * from {R('1t_god/2022/2022_1t_god.csv')} limit 2")
q(f"select * from {R('1t_god/2023/2023_1t_god.csv')} limit 2")
q(f"select NOMVOPR, count(*) from {R('d004/2023/1kv/kv_vopr11.csv')} group by 1 order by 2 desc limit 10")
q(f"select POL, count(*) from {R('d008/2023/kontr_k.csv')} group by 1")
q(f"select KOL_CHL, count(*) from {R('d008/2023/kontr_k.csv')} where NOMP='01' group by 1 order by 1")
q(f"select count(distinct NOMER) from {R('d008/2023/kontr_k.csv')}")
q(f"select count(distinct NOMER) from {R('d004/2023/1kv/kv_vopr0.csv')}")
