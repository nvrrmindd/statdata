import duckdb, pandas as pd, os, glob, json
os.chdir(os.environ.get('DATA_DIR', '.'))
O=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results')+'/'
con=duckdb.connect(); con.sql("SET threads=8")
R=lambda p: f"read_csv('{p}', all_varchar=true, header=true, quote='\"', union_by_name=true)"
man=pd.read_csv('MANIFEST.csv')
def cols(p): return [c[0] for c in con.sql(f"select * from {R(p)} limit 0").description]
def valcol(p): c=cols(p); return 'VAL_NUM' if 'VAL_NUM' in c else 'GR1'
res={}
# ---------- 1T annual (row-level medians; synthetic headcounts too noisy for weighting)
god={2021:'1t_god/2021/2021_1t_god.csv',2022:'1t_god/2022/2022_1t_god.csv',2023:'1t_god/2023/2023_1t_god.csv',2024:'1t_god/2024/sr_1t_god_12_2024.csv'}
ga=[];reg=[]
for y,p in god.items():
    v=valcol(p)
    d=con.sql(f"""with t as (select ID, SP, try_cast({v} as double) x from {R(p)} where KCP='252101' and try_cast({v} as double)>0)
    select count(distinct ID) firms_w, median(x) filter (where SP='0') med_wage, quantile_cont(x,0.25) filter (where SP='0') p25, quantile_cont(x,0.75) filter (where SP='0') p75,
      median(x) filter (where SP='2')/median(x) filter (where SP='1') fm_ratio from t""").df()
    d['firms']=con.sql(f"select count(distinct ID) from {R(p)}").fetchone()[0]; d['year']=y; ga.append(d)
    r=con.sql(f"""select left(KATO,2) reg, count(distinct ID) firms, median(try_cast({v} as double)) med from {R(p)} where KCP='252101' and SP='0' and try_cast({v} as double)>0 group by 1""").df(); r['year']=y; reg.append(r)
ga=pd.concat(ga); ga.to_csv(O+'t1god_summary.csv',index=False); print(ga.to_string())
reg=pd.concat(reg); reg.to_csv(O+'t1god_regions.csv',index=False)
# ---------- 2T individual wages
t2=[];edu=[]
for p in man[man.form=='2t'].path:
    y=int(p.split('/')[1])
    d=con.sql(f"""with w as (select SP, SUO, try_cast(VAL_NUM as double) x from {R(p)} where KCP='252101' and try_cast(VAL_NUM as double)>0)
    select count(*) workers, median(x) med, quantile_cont(x,0.1) p10, quantile_cont(x,0.9) p90, avg(x) mean,
      median(x) filter (where SP='2')/median(x) filter (where SP='1') fm_med,
      avg(x) filter (where SP='2')/avg(x) filter (where SP='1') fm_mean from w""").df(); d['year']=y; t2.append(d)
    e=con.sql(f"""select SUO, SP, count(*) n, median(try_cast(VAL_NUM as double)) med from {R(p)} where KCP='252101' and try_cast(VAL_NUM as double)>0 group by all""").df(); e['year']=y; edu.append(e)
    h=con.sql(f"select least(floor(try_cast(VAL_NUM as double)/25000),40) b, count(*) n from {R(p)} where KCP='252101' and try_cast(VAL_NUM as double)>0 group by 1 order by 1").df(); h['year']=y; h.to_csv(O+f'2t_hist_{y}.csv',index=False)
t2=pd.concat(t2); t2.to_csv(O+'2t_summary.csv',index=False); print(t2.to_string())
pd.concat(edu).to_csv(O+'2t_edu.csv',index=False)
# ---------- T-001 labour force
lf=[];lfr=[];lfg=[]
for p in man[man.form=='t001'].path:
    y=int(p.split('/')[1])
    base=f"""select *, try_cast(vosr as int) age, (ZAN_RABOTA='1') emp, (ZAN_RABOTA='2' and PSK_RABOTA='1') unemp from {R(p)}"""
    d=con.sql(f"""with b as ({base}) select count(*) n, avg(emp::int) emp_rate, sum(unemp::int)/(sum(emp::int)+sum(unemp::int)) unemp_rate,
      sum(unemp::int) filter (where age<=24)/(sum(emp::int) filter (where age<=24)+sum(unemp::int) filter (where age<=24)) youth_unemp,
      sum(unemp::int) filter (where DH_POLRESP='2')/(sum(emp::int) filter (where DH_POLRESP='2')+sum(unemp::int) filter (where DH_POLRESP='2')) unemp_f,
      sum(unemp::int) filter (where DH_POLRESP='1')/(sum(emp::int) filter (where DH_POLRESP='1')+sum(unemp::int) filter (where DH_POLRESP='1')) unemp_m,
      sum(unemp::int) filter (where K='1')/(sum(emp::int) filter (where K='1')+sum(unemp::int) filter (where K='1')) unemp_urban,
      sum(unemp::int) filter (where K='2')/(sum(emp::int) filter (where K='2')+sum(unemp::int) filter (where K='2')) unemp_rural,
      avg(emp::int) filter (where age between 15 and 64) emp_rate_1564
      from b""").df(); d['year']=y; lf.append(d)
    r=con.sql(f"""with b as ({base}) select left(TE,2) reg, count(*) n, sum(unemp::int)/(sum(emp::int)+sum(unemp::int)) unemp_rate, avg(emp::int) emp_rate from b group by 1""").df(); r['year']=y; lfr.append(r)
    g=con.sql(f"""with b as ({base}) select case when age<25 then '15-24' when age<35 then '25-34' when age<45 then '35-44' when age<55 then '45-54' when age<65 then '55-64' else '65+' end ag,
      count(*) n, avg(emp::int) emp_rate, sum(unemp::int)/nullif(sum(emp::int)+sum(unemp::int),0) unemp_rate from b group by 1 order by 1""").df(); g['year']=y; lfg.append(g)
lf=pd.concat(lf); lf.to_csv(O+'t001_summary.csv',index=False); print(lf.to_string())
pd.concat(lfr).to_csv(O+'t001_regions.csv',index=False); pd.concat(lfg).to_csv(O+'t001_age.csv',index=False)
# ---------- D004 household budgets (per quarter)
inc_cols="+".join(f"coalesce(try_cast(GR{i} as double),0)" for i in [1,2]+list(range(4,22)))
hh=[]
for y in range(2021,2025):
  for q in range(1,5):
    base=f"d004/{y}/{q}kv"
    if not os.path.exists(base+'/kv_vopr11.csv'): continue
    d=con.sql(f"""
    with r as (select NOMER, REZ from {R(base+'/kv_vopr0.csv')}),
    inc as (select NOMER, sum({inc_cols}) inc, sum(coalesce(try_cast(GR1 as double),0)) wage, sum(coalesce(try_cast(GR2 as double),0)) selfemp,
                   sum(coalesce(try_cast(GR4 as double),0)) pens from {R(base+'/kv_vopr11.csv')} group by 1),
    ex as (select NOMER, sum(try_cast(STOIMK as double)) exp from (
        {' union all '.join(f"select NOMER, STOIMK from {R(base+f'/kv_vopr{k}.csv')}" for k in [1,2,3,4,5,6,7])}) group by 1),
    debt as (select NOMER, sum(try_cast(STOIMK as double)) debt from {R(base+'/kv_vopr12.csv')} group by 1)
    select count(*) hh, avg((REZ='1')::int) resp_rate, median(inc) inc_med, avg(inc) inc_mean, sum(wage)/sum(inc) sh_wage, sum(selfemp)/sum(inc) sh_self,
      sum(pens)/sum(inc) sh_pens, median(exp) exp_med, avg((debt>0)::int) debt_share
    from r left join inc using(NOMER) left join ex using(NOMER) left join debt using(NOMER) where REZ='1'""").df()
    d['year']=y; d['q']=q; hh.append(d)
hh=pd.concat(hh); hh.to_csv(O+'d004_summary.csv',index=False); print(hh.to_string())
# ---------- D008 roster
ro=con.sql(f"""select GOD year, count(*) persons, count(distinct NOMER) hh, avg(try_cast(KOL_CHL as int)) filter (where NOMP='01') hh_size,
   avg((POL='2')::int) share_f, avg((try_cast(GOD as int)-try_cast(GOD_ROJD as int))<15 ::int) share_child
   from {R('d008/*/kontr_k.csv')} group by 1 order by 1""").df(); ro.to_csv(O+'d008_summary.csv',index=False); print(ro)
