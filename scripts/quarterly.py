import duckdb, pandas as pd, os, glob
os.chdir(os.environ.get('DATA_DIR', '.'))
O=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results')+'/'
con=duckdb.connect(); con.sql("SET threads=8")
R=lambda p: f"read_csv('{p}', all_varchar=true, header=true, quote='\"')"
def cols(p): return [c[0] for c in con.sql(f"select * from {R(p)} limit 0").description]
# ---------- 1-T quarterly: KCP 252101 = средняя начисленная зарплата, STKD 1 = всего.
# На предприятие приходится несколько строк -> сначала среднее по предприятию, затем медиана по предприятиям.
kv=[]
for y in range(2021,2025):
  for q in range(1,5):
    p=glob.glob(f'1t_kv/{y}/{q}kv/*.csv')[0]; v='VAL_NUM' if 'VAL_NUM' in cols(p) else 'GR1'
    d=con.sql(f"""with f as (select ID, avg(try_cast({v} as double)) x from {R(p)}
        where KCP='252101' and STKD='1' and try_cast({v} as double)>0 group by 1)
      select count(*) firms, median(x) med, quantile_cont(x,0.25) p25, quantile_cont(x,0.75) p75, avg(x) wmean from f""").df()
    d['year']=y; d['q']=q; kv.append(d)
pd.concat(kv).to_csv(O+'t1kv_wages_recomputed.csv',index=False)
# ---------- D-004: share of refusals (REZ != '1') per quarter
rf=[]
for y in range(2021,2025):
  for q in range(1,5):
    d=con.sql(f"select avg((REZ<>'1')::int) refusal from {R(f'd004/{y}/{q}kv/kv_vopr0.csv')}").df(); d['yr']=y; d['q']=q; rf.append(d)
pd.concat(rf)[['yr','q','refusal']].to_csv(O+'d004_refusal.csv',index=False)
# ---------- missingness by form x year (cell-weighted, from profile.py output)
m=pd.read_csv(O+'missing_by_table.csv'); m['cells']=m.rows*m.cols; m['miss_cells']=m.cells*m.cell_missing
g=m.groupby(['form','year']).agg(tables=('path','count'),rows=('rows','sum'),cols=('cols','max'),cells=('cells','sum'),miss_cells=('miss_cells','sum'),
    empty=('cols_empty','sum'),gt90=('cols_gt90','sum')).reset_index()
g['miss']=g.miss_cells/g.cells; g[['form','year','tables','rows','cols','miss','empty','gt90']].to_csv(O+'missing_form_year.csv',index=False)
