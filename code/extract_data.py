"""Extract published DFCCIL tables; preserve raw cells and explicit audit decisions.

Run from any working directory: python code/extract_data.py
Input: pdftotext -layout text from the official 2024-25 annual report.
No observations are imputed or synthesized. Scenario inputs are in separate files.
"""
from pathlib import Path
import calendar, hashlib, json, re
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
RAW, CLEAN = ROOT/'data/raw', ROOT/'data/clean'
MONTHS = dict(zip(['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec'], range(1,13)))
SOURCE = ROOT/'source_documents/dfccil_ar_2024_25.txt'

def rows(section, n):
    out=[]
    for line in section.splitlines():
        m=re.match(r'^\s*(Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar)\s+', line)
        if m:
            vals=[float(x.replace(',','')) for x in re.findall(r'\d[\d,]*(?:\.\d+)?', line[m.end():])]
            assert len(vals)==n, (line, vals)
            out.append((m.group(1),vals))
    assert len(out)==12, len(out)
    return out

def main():
    RAW.mkdir(parents=True,exist_ok=True); CLEAN.mkdir(parents=True,exist_ok=True)
    text=SOURCE.read_text()
    block=text.split('Corridor wise Number of Trains per Day',1)[1].split('Table: 3',1)[0]
    cells=[]
    def add(mon, fy, corridor, metric, value, table, page):
        month=MONTHS[mon]; year=fy if month>=4 else fy+1
        cells.append(dict(date=f'{year}-{month:02d}-01',fy_start=fy,corridor=corridor,metric=metric,value=value,source_id='S1',table=table,printed_page=page))
    for mon, vals in rows(block,9):
        for y in range(3):
            for j,c in enumerate(['EDFC','WDFC','TOTAL']): add(mon,2022+y,c,'trains_per_day',vals[y*3+j],2,47)
    block=text.split('Corridor wise Total GTKMs',1)[1].split('Table: 5',1)[0]
    for mon, vals in rows(block,12):
        for y in range(4):
            for j,c in enumerate(['EDFC','WDFC','TOTAL']): add(mon,2021+y,c,'gtkm_million',vals[y*3+j],4,48)
    for metric,start,end,table in [('speed_kmph','Year wise / Month wise Average Speeds','Table: 6',5),('wtr_days','DFCR Wagon Turnround (WTR) (in days)','Table: 7',6)]:
        block=text.split(start,1)[1].split(end,1)[0]
        for mon,vals in rows(block,8):
            for j,c in enumerate(['EDFC','WDFC']):
                for y in range(4): add(mon,2021+y,c,metric,vals[j*4+y],table,49)
    raw=pd.DataFrame(cells)
    raw.to_csv(RAW/'dfccil_reported_cells.csv',index=False)
    clean=raw[raw.corridor!='TOTAL'].pivot(index=['date','fy_start','corridor'],columns='metric',values='value').reset_index()
    clean['quality_flag']=''
    # Published speed conflict: older report 48.7, newer 58.7. Exclude, do not guess.
    mask=(clean.date=='2023-03-01')&(clean.corridor=='WDFC')
    clean.loc[mask,'speed_kmph']=np.nan
    clean.loc[mask,'quality_flag']='WDFC Mar2023 speed disputed: S1=58.7; S2=48.7; excluded'
    # Table 2 Feb2023: E+W=222.00 vs reported total229.93. No basis to assign discrepancy.
    mask=clean.date=='2023-02-01'
    clean.loc[mask,'trains_per_day']=np.nan
    clean.loc[mask,'quality_flag']='Feb2023 corridor train rates fail total reconciliation; excluded'
    clean.to_csv(CLEAN/'corridor_monthly.csv',index=False)
    # Re-extract table 3 independently of the feasibility audit.
    block=text.split('DFCR Year wise: Total Number of Trains',1)[1].split('Commodity-wise',1)[0]
    trains=[]
    for line in block.splitlines():
        m=re.match(r'^\s*(Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec|Jan|Feb|Mar)\s+',line)
        if not m: continue
        mon=MONTHS[m.group(1)]
        values=[int(v.replace(',','')) for v in re.findall(r'\d[\d,]*',line[m.end():])]
        fys=list(range(2020 if mon in [12,1,2,3] else 2021,2025))
        assert len(values)==len(fys)
        for fy,val in zip(fys,values):
            yr=fy if mon>=4 else fy+1
            trains.append(dict(date=f'{yr}-{mon:02d}-01',fy_start=fy,trains=val,days=calendar.monthrange(yr,mon)[1],source_id='S1',table=3,printed_page=48))
    train=pd.DataFrame(trains).sort_values('date').reset_index(drop=True)
    assert len(train)==52 and not train.date.duplicated().any()
    expected={2020:2470,2021:23544,2022:62277,2023:88225,2024:130116}
    actual=train.groupby('fy_start').trains.sum().to_dict()
    assert actual==expected, (actual,expected)
    train['trains_per_calendar_day']=train.trains/train.days
    train.to_csv(CLEAN/'total_trains_monthly.csv',index=False)
    total=raw[(raw.corridor=='TOTAL')&(raw.metric=='gtkm_million')].rename(columns={'value':'gtkm_million'})
    total[['date','fy_start','gtkm_million','source_id','table','printed_page']].to_csv(CLEAN/'total_gtkm_monthly.csv',index=False)
    # Manual transcription, checked against World Bank ICR Annex 4 Table 5, printed p85.
    cap=[('DDU','Allahabad',110,74,10,150,148),('Allahabad','Kanpur',110,74,10,150,148),('Kanpur','Tundla',136,32,20,162,129),('Tundla','Khurja',136,42,20,176,129),('Khurja','Dadri',128,52,20,182,126),('Khurja','Saharanpur',128,60,20,164,145),('Saharanpur','Ludhiana',122,68,16,148,159),('DDU','Lucknow',66,46,16,52,281),('Lucknow','Moradabad',130,66,20,110,224),('Moradabad','Saharanpur',78,62,20,110,166)]
    cap=pd.DataFrame(cap,columns=['from','to','passenger_trains_day','freight_trains_day','other_trains_day','nominal_capacity_trains_day','reported_utilization_pct'])
    cap['period']='FY2022-23 (partly post-DFC)';cap['source_id']='S3';cap['printed_page']=85
    cap['route_note']=['direct parallel']*5+['via Delhi-Ambala','direct parallel']+['alternative route']*3
    cap.to_csv(RAW/'conventional_capacity_reported.csv',index=False)
    audit=[
      ('D01','Table 3 annual totals','All five FY sums agree','Retain; FY2020-21 only Dec-Mar'),
      ('D02','Feb2023 corridor trains/day','141.62+80.38=222.00; total229.93','Exclude both corridor rates; retain independently reconciled total train count6438'),
      ('D03','FY2023-24 Table 2 Avg/Day total','211.67 repeats April; contradicts annual count','Ignore printed summary; compute88225/366=241.052'),
      ('D04','Mar2023 WDFC speed','S1 Table5=58.7; S2 Table5=48.7','Exclude from clean speed; sensitivity retains either reported value'),
      ('D05','GTKM table','Some corridor sums and published totals differ by1-3 million','Retain published monthly cells; aggregate monthly total column; disclose rounding'),
      ('D06','Annual daily train averages','Monthly means differ from calendar-day weighted totals','Use annual total/days for network rate; corridor means are unweighted'),
      ('D07','Conventional capacity','Published utilization differs from total/nominal capacity','Infer effective capacity from reported utilization only for normalized scenarios'),
      ('D08','Comparison coverage','No matched train-level pre/post controls or current section data','No nationwide causal or actual current path-release estimate')]
    pd.DataFrame(audit,columns=['audit_id','field','finding','decision']).to_csv(CLEAN/'discrepancy_log.csv',index=False)
    dictionary=[
      ('date','YYYY-MM-01','Month start; India FY April-March'),('fy_start','year','2024 denotes FY2024-25'),('trains','count/month','Reported DFC train movements; not necessarily unique consignments'),('trains_per_day','reported daily average','Corridor monthly rate; missing Apr2021-Mar2022 and Feb2023; never zero-filled'),('gtkm_million','million gross tonne-km','Gross train weight multiplied by distance; not net cargo tonnes'),('speed_kmph','km/h','Reported corridor monthly average; annual study means unweighted; one disputed cell excluded'),('wtr_days','days','DFCCIL wagon turnround; do not equate with end-to-end IR wagon cycle or terminal dwell'),('reported_utilization_pct','percent','World Bank parallel line FY2022-23 incl maintenance convention'),('implied_effective_capacity','normalized train equivalents/day','Derived total trains/(reported utilization/100); not engineering line capacity'),('diversion_share','fraction 0-1','Hypothetical additional share of FY2022-23 residual freight shifted; not observed'),('cash_realization','fraction 0-1','Hypothetical monetizable share of valued hours saved')]
    pd.DataFrame(dictionary,columns=['field','unit','definition_and_limit']).to_csv(CLEAN/'data_dictionary.csv',index=False)
    qa={'raw_metric_cells':len(raw),'corridor_month_rows':len(clean),'total_month_rows':len(train),'annual_count_totals':actual,'unique_corridor_dates':bool(not clean.duplicated(['date','corridor']).any()),'missing_clean_speed':int(clean.speed_kmph.isna().sum()),'missing_clean_train_rates':int(clean.trains_per_day.isna().sum()),'input_sha256':hashlib.sha256(SOURCE.read_bytes()).hexdigest(),'status':'passed'}
    (ROOT/'outputs/extraction_audit.json').write_text(json.dumps(qa,indent=2))
    print(json.dumps(qa,indent=2))

if __name__=='__main__': main()
