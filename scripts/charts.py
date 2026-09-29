import os, pandas as pd, numpy as np, matplotlib
matplotlib.use('Agg'); import matplotlib.pyplot as plt
O=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','results')+'/'
C=os.path.join(os.path.dirname(os.path.abspath(__file__)),'..','charts')+'/'
SURF='#fbfbf8'; INK='#1c2230'; INK2='#5a6170'; GRID='#e4e4de'; B='#2a78d6'; OR='#eb6834'; GR='#8d918f'
plt.rcParams.update({'font.family':'Arial','font.size':15,'axes.edgecolor':GRID,'axes.labelcolor':INK2,'xtick.color':INK2,'ytick.color':INK2,
  'axes.facecolor':SURF,'figure.facecolor':SURF,'axes.spines.top':False,'axes.spines.right':False,'axes.spines.left':False,'axes.grid':True,'grid.color':GRID,'grid.linewidth':1,'axes.axisbelow':True})
fmt=lambda v: f"{v:,.0f}".replace(',',' ')
# ---- Chart 1: indexed dynamics
kv=pd.read_csv(O+'t1kv_wages.csv'); hh=pd.read_csv(O+'d004_summary.csv')
x=np.arange(16); lab=[f"{q}кв\n{y}" if q==1 else f"{q}кв" for y,q in zip(kv.year,kv.q)]
w=kv.med.values/kv.med.values[0]*100; h=hh.inc_med.values/hh.inc_med.values[0]*100
cpi_x=[-0.5,3,7,11,15]; cpi=[100,108.4,130.4,143.2,155.5]
fig,ax=plt.subplots(figsize=(10.4,6.2),dpi=200)
ax.plot(cpi_x,cpi,color=GR,lw=2,ls=(0,(4,3)),zorder=2)
ax.plot(x,w,color=B,lw=2.5,marker='o',ms=6,mec=SURF,mew=2,zorder=3)
ax.plot(x,h,color=OR,lw=2.5,marker='o',ms=6,mec=SURF,mew=2,zorder=3)
ax.text(15.35,w[-1],f"Зарплата на предприятии\n(медиана, 1-Т кв): {w[-1]:.0f}",va='center',color=INK,fontsize=14)
ax.text(15.35,h[-1]+2,f"Доход домохозяйства\n(медиана, Д-004): {h[-1]:.0f}",va='center',color=INK,fontsize=14)
ax.text(15.35,cpi[-1]-6,f"Цены (ИПЦ, накоп.): {cpi[-1]:.0f}",va='center',color=INK2,fontsize=14)
ax.set_xticks(x); ax.set_xticklabels(lab,fontsize=12.5); ax.set_xlim(-0.6,15.3); ax.set_ylim(90,215)
ax.set_ylabel('Индекс, 1 кв. 2021 = 100'); ax.tick_params(length=0)
fig.subplots_adjust(left=0.08,right=0.72,top=0.97,bottom=0.13); fig.savefig(C+'dyn.png'); plt.close()
# ---- Chart 2: missingness heatmap
m=pd.read_csv(O+'missing_form_year.csv')
order=['t001','2t','1t_kv','1t_god','d004','d002','d008','d006']
names={'t001':'Т-001 рабочая сила','2t':'2-Т оплата труда','1t_kv':'1-Т квартальная','1t_god':'1-Т годовая','d004':'Д-004 бюджеты ДХ','d002':'Д-002 оценки','d008':'Д-008 состав ДХ','d006':'Д-006 жилище'}
P=m.pivot(index='form',columns='year',values='miss').loc[order]*100
fig,ax=plt.subplots(figsize=(7.6,5.6),dpi=200)
from matplotlib.colors import LinearSegmentedColormap
cm=LinearSegmentedColormap.from_list('b',['#eef4fc','#9cc2ee','#2a78d6','#123f7a'])
ax.imshow(P.values,cmap=cm,vmin=0,vmax=75,aspect='auto')
for i in range(P.shape[0]):
  for j in range(P.shape[1]):
    v=P.values[i,j]; ax.text(j,i,f"{v:.0f}%",ha='center',va='center',fontsize=14,color='white' if v>40 else INK)
ax.set_xticks(range(4)); ax.set_xticklabels(P.columns); ax.set_yticks(range(len(order))); ax.set_yticklabels([names[o] for o in order],color=INK)
ax.grid(False); ax.tick_params(length=0); ax.xaxis.tick_top()
for s in ax.spines.values(): s.set_visible(False)
ax.set_xticks(np.arange(-.5,4,1),minor=True); ax.set_yticks(np.arange(-.5,8,1),minor=True); ax.grid(which='minor',color=SURF,lw=3); ax.tick_params(which='minor',length=0)
fig.subplots_adjust(left=0.33,right=0.99,top=0.92,bottom=0.02); fig.savefig(C+'miss.png'); plt.close()
# ---- Chart 3: 2T wage distribution 2021 vs 2024
fig,ax=plt.subplots(figsize=(8.0,5.4),dpi=200)
for y,c in [(2021,OR),(2024,B)]:
  d=pd.read_csv(O+f'2t_hist_{y}.csv'); d=d[d.b<40]; s=d.n/d.n.sum()*100
  xs=d.b*25+12.5; ax.plot(xs,s,color=c,lw=2.5); ax.fill_between(xs,s,color=c,alpha=0.10,lw=0)
t2=pd.read_csv(O+'2t_summary.csv')
ax.set_ylim(0,17.5)
for y,c,dy in [(2021,OR,0),(2024,B,0)]:
  md=t2[t2.year==y].med.iloc[0]/1000; ax.axvline(md,color=c,lw=1.5,ls=(0,(3,3)))
ax.set_yticks(range(0,15,2))
ax.text(t2[t2.year==2021].med.iloc[0]/1000+8,15.6,f"2021\nмедиана {t2[t2.year==2021].med.iloc[0]/1000:.0f} тыс.",ha='left',color=INK,fontsize=14,bbox=dict(fc=SURF,ec='none',pad=2),zorder=5)
ax.text(t2[t2.year==2024].med.iloc[0]/1000+8,11.6,f"2024\nмедиана {t2[t2.year==2024].med.iloc[0]/1000:.0f} тыс.",ha='left',color=INK,fontsize=14,bbox=dict(fc=SURF,ec='none',pad=2),zorder=5)
ax.set_ylim(0,17.5); ax.set_xlim(0,1000); ax.set_xlabel('Начисленная зарплата работника, тыс. тенге в месяц'); ax.set_ylabel('% работников'); ax.tick_params(length=0)
fig.subplots_adjust(left=0.1,right=0.98,top=0.97,bottom=0.14); fig.savefig(C+'dist.png'); plt.close()
# ---- Chart 4: unemployment by age 2021 vs 2024
a=pd.read_csv(O+'t001_age.csv'); a=a[a.ag!='65+']
fig,ax=plt.subplots(figsize=(7.4,5.4),dpi=200)
ags=a.ag.unique(); xi=np.arange(len(ags)); bw=0.3
for k,(y,c) in enumerate([(2021,OR),(2024,B)]):
  v=a[a.year==y].set_index('ag').loc[ags].unemp_rate*100
  ax.bar(xi+(k-0.5)*(bw+0.03),v,width=bw,color=c)
  for xx,vv in zip(xi,v): ax.text(xx+(k-0.5)*(bw+0.03),vv+0.1,f"{vv:.1f}",ha='center',fontsize=12.5,color=INK2)
ax.set_xticks(xi); ax.set_xticklabels(ags); ax.set_ylabel('Безработица, %'); ax.set_ylim(0,7); ax.tick_params(length=0); ax.grid(axis='x',visible=False)
ax.legend(handles=[plt.Rectangle((0,0),1,1,color=OR),plt.Rectangle((0,0),1,1,color=B)],labels=['2021','2024'],frameon=False,loc='upper left',ncol=2)
fig.subplots_adjust(left=0.1,right=0.98,top=0.97,bottom=0.1); fig.savefig(C+'age.png'); plt.close()
print('ok')
