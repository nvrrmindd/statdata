import duckdb, pandas as pd, os
os.chdir(os.environ.get('DATA_DIR', '.'))
O=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results')+'/'
con=duckdb.connect(); con.sql("SET threads=8")
R=lambda p: f"read_csv('{p}', all_varchar=true, header=true, quote='\"')"
man=pd.read_csv('MANIFEST.csv')
# ---- 1. missingness per table
rows=[]
for _,m in man.iterrows():
    p=m.path
    cols=[c[0] for c in con.sql(f"select * from {R(p)} limit 0").description]
    expr=",".join(f'count("{c}")' for c in cols)
    cnt=con.sql(f"select count(*), {expr} from {R(p)}").fetchone()
    n=cnt[0]; nn=cnt[1:]
    full=sum(1 for v in nn if v==n); empty=sum(1 for v in nn if v==0)
    rows.append(dict(path=p,form=m.form,year=m.year,rows=n,cols=len(cols),
        cell_missing=1-sum(nn)/(n*len(cols)) if n else None, cols_full=full, cols_empty=empty,
        cols_gt90=sum(1 for v in nn if n and v/n<0.1)))
    print(p,n,round(rows[-1]['cell_missing'],3),flush=True)
pd.DataFrame(rows).to_csv(O+'missing_by_table.csv',index=False)
