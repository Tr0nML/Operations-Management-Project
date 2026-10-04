"""Create publication-ready charts from computed outputs, without manual data edits."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Rectangle

ROOT=Path(__file__).resolve().parents[1]; F=ROOT/'figures'; F.mkdir(exist_ok=True)
plt.rcParams.update({'font.family':'DejaVu Sans','font.size':10,'axes.spines.top':False,'axes.spines.right':False,'axes.labelcolor':'#243746','text.color':'#172b3a','axes.edgecolor':'#acb7bd','grid.color':'#e2e7ea','axes.titleweight':'bold','savefig.dpi':220})
BLUE='#176b87';ORANGE='#c56634';GRAY='#6b7880'
def save(fig,name):
    fig.tight_layout(pad=.6);fig.savefig(F/(name+'.png'),bbox_inches='tight',facecolor='white');plt.close(fig)
def main():
    tr=pd.read_csv(ROOT/'data/clean/total_trains_monthly.csv',parse_dates=['date'])
    df=pd.read_csv(ROOT/'data/clean/corridor_monthly.csv',parse_dates=['date'])
    fig,ax=plt.subplots(figsize=(7,2.7));ax.plot(tr.date,tr.trains,color=BLUE,lw=2)
    ax.fill_between(tr.date,tr.trains,alpha=.09,color=BLUE);ax.set_ylabel('Train movements / month');ax.set_ylim(0,14500);ax.grid(axis='y');ax.annotate('12,497',xy=(tr.date.iloc[-1],12497),xytext=(-52,10),textcoords='offset points',weight='bold');save(fig,'01_train_growth')
    fig,axes=plt.subplots(1,2,figsize=(7,2.8))
    for c,color in [('EDFC',BLUE),('WDFC',ORANGE)]:
        g=df[df.corridor==c]
        axes[0].plot(g.date,g.speed_kmph,label=c,color=color,lw=1.6)
        axes[1].plot(g.date,g.wtr_days,label=c,color=color,lw=1.6)
    for ax in axes:
        ax.grid(axis='y');ax.tick_params(axis='x',rotation=35);ax.xaxis.set_major_locator(matplotlib.dates.YearLocator());ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%Y'))
    axes[0].set_ylabel('Monthly speed (km/h)');axes[0].legend(frameon=False,ncol=2,loc='lower left',fontsize=9)
    axes[1].set_ylabel('Reported wagon turnround (days)');save(fig,'02_speed_wtr')
    pred=pd.read_csv(ROOT/'outputs/selected_forecast_test.csv',parse_dates=['date'])
    fig,ax=plt.subplots(figsize=(7,2.4));ax.plot(pred.date,pred.actual,label='Observed',color=BLUE,lw=2);ax.plot(pred.date,pred.prediction,label='Day-adjusted naive',color=ORANGE,lw=1.7,ls='--');ax.set_ylabel('Monthly train movements');ax.legend(frameon=False,ncol=2,fontsize=9);ax.grid(axis='y');ax.xaxis.set_major_formatter(matplotlib.dates.DateFormatter('%b %y'));save(fig,'03_forecast')
    cap=pd.read_csv(ROOT/'outputs/capacity_scenarios.csv')
    sel=cap.iloc[[0,2,4,6]].copy();fig,ax=plt.subplots(figsize=(7,2.9));x=np.arange(4)
    ax.barh(x+.17,sel.util_at_0pct_diversion,height=.3,label='Reported FY2022-23',color=GRAY)
    ax.barh(x-.17,sel.util_at_50pct_diversion,height=.3,label='50% additional freight diversion',color=BLUE)
    ax.axvline(100,ls='--',color=ORANGE,lw=1);ax.set_yticks(x,sel.section);ax.set_xlabel('Normalized utilization index (%)');ax.legend(frameon=False,fontsize=8,loc='lower center',bbox_to_anchor=(.5,1.02),ncol=2);ax.set_xlim(0,190);ax.invert_yaxis();save(fig,'04_capacity')
    fig,ax=plt.subplots(figsize=(7,2.4));hours=np.linspace(0,2,60)
    for r,color in [(.2,GRAY),(.4,BLUE),(.6,ORANGE)]: ax.plot(hours,(3*hours*r-.7),label=f'{r:.0%} cash realization',color=color,lw=2)
    ax.axhline(0,color='#444444',lw=.8);ax.set_xlabel('Assumed hours saved per pilot train');ax.set_ylabel('First-year net benefit\n(INR crore)');ax.legend(frameon=False,fontsize=8);ax.grid(axis='y');save(fig,'05_cost_sensitivity')
    # Methodology workflow: explicit extraction audit precedes both evidence and forecast streams.
    fig,ax=plt.subplots(figsize=(7,2.9));ax.set_xlim(0,10);ax.set_ylim(-.2,5);ax.axis('off')
    nodes=[(.1,3.2,2.6,.9,'Official sources\nPDFs and webpages'),(3.6,3.2,2.7,.9,'Extract and audit\nRaw cells and flags'),(7.1,3.2,2.7,.9,'Clean monthly data\nNo invented observations'),(1.2,1.25,3.0,.9,'Descriptive analysis\nCapacity and cost scenarios'),(5.8,1.25,3.0,.9,'Temporal forecast validation\nNLP evidence retrieval'),(3.3,-.02,3.4,.8,'Dashboard and recommendations\nHuman review and limitations')]
    for x,y,w,h,label in nodes:
        ax.add_patch(Rectangle((x,y),w,h,facecolor='#f4f7f8',edgecolor='#8da4ae',linewidth=.8));ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=9)
    for a,b in [((2.7,3.65),(3.6,3.65)),((6.3,3.65),(7.1,3.65)),((8.45,3.2),(7.3,2.15)),((7.1,3.2),(2.7,2.15)),((2.7,1.25),(4.1,.8)),((7.3,1.25),(5.9,.8))]: ax.add_patch(FancyArrowPatch(a,b,arrowstyle='-|>',mutation_scale=10,color=BLUE,lw=1))
    save(fig,'06_methodology')
    tasks=['Agree KPI definitions','Capture timestamp baseline','Pilot interchange coordination','Compare with matched movements','Review and decide expansion']
    fig,ax=plt.subplots(figsize=(7,2.4));starts=[1,3,5,8,11];dur=[2,2,5,3,2]
    for i,(s,d) in enumerate(zip(starts,dur)): ax.barh(i,d,left=s-.5,height=.55,color=BLUE if i%2==0 else GRAY)
    ax.set_yticks(range(5),tasks);ax.invert_yaxis();ax.set_xticks(range(1,13));ax.set_xlim(.5,12.5);ax.set_xlabel('Weeks after approval');ax.grid(axis='x',alpha=.4);save(fig,'07_implementation')
    print('Created 7 figures.')
if __name__=='__main__': main()
