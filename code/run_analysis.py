"""Reproduce all quantitative results from the audited public-data CSVs.

Python 3.11+. Dependencies: numpy, pandas, scikit-learn, matplotlib.
Forecasts are retrospective one-month-ahead exercises, not live 2026 predictions.
Validation selects a model before the final test year is evaluated. Each origin
uses only earlier observations; previously observed test months may update the
next one-step forecast. No random train/test split is used.
"""
from pathlib import Path
import calendar, json, sys
import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'outputs'; OUT.mkdir(exist_ok=True)
def dump(name,obj):
    (OUT/name).write_text(json.dumps(obj,indent=2,allow_nan=False))

def features(y, dates, t):
    """All lags are strictly before target t; calendar features are known in advance."""
    m=dates[t].month
    return [y[t-1],y[t-2],y[t-3],np.mean(y[t-3:t]),t,
            np.sin(2*np.pi*m/12),np.cos(2*np.pi*m/12),dates[t].days_in_month]

def forecast(y,dates,t,model):
    hist=y[:t]
    if model=='Naive': return float(hist[-1])
    if model=='Day-adjusted naive': return float(hist[-1]/dates[t-1].days_in_month*dates[t].days_in_month)
    if model=='Seasonal naive': return float(y[t-12])
    if model=='12-month drift': return max(0,float(hist[-1]+(hist[-1]-hist[-12])/11))
    X=np.array([features(y,dates,i) for i in range(3,t)])
    rf=RandomForestRegressor(n_estimators=200,max_depth=3,min_samples_leaf=3,random_state=42,n_jobs=1)
    rf.fit(X,y[3:t])
    return float(rf.predict([features(y,dates,t)])[0])

def main():
    df=pd.read_csv(ROOT/'data/clean/corridor_monthly.csv',parse_dates=['date'])
    tr=pd.read_csv(ROOT/'data/clean/total_trains_monthly.csv',parse_dates=['date'])
    gt=pd.read_csv(ROOT/'data/clean/total_gtkm_monthly.csv')
    ann=tr.groupby('fy_start').agg(trains=('trains','sum'),calendar_days=('days','sum')).reset_index()
    ann['trains_per_day']=ann.trains/ann.calendar_days
    ann['total_gtkm_million']=ann.fy_start.map(gt.groupby('fy_start').gtkm_million.sum())
    ann['train_growth_pct']=ann.trains.pct_change()*100
    ann.loc[ann.fy_start==2021,'train_growth_pct']=np.nan # partial first FY is not comparable
    ann.to_csv(OUT/'annual_network_summary.csv',index=False)
    ca=df.groupby(['fy_start','corridor']).agg(speed_mean=('speed_kmph','mean'),speed_n=('speed_kmph','count'),wtr_mean=('wtr_days','mean'),trains_day_mean=('trains_per_day','mean'),trains_day_n=('trains_per_day','count'),gtkm_million=('gtkm_million','sum')).reset_index()
    ca.to_csv(OUT/'annual_corridor_summary.csv',index=False)
    cor=[]
    for c,g in df.groupby('corridor'):
        g=g.sort_values('date').set_index('date')
        sub=g[['trains_per_day','speed_kmph']].dropna()
        dif=g[['trains_per_day','speed_kmph']].diff().dropna() # gaps remain NA, never joined across missing month
        cor.append(dict(corridor=c,level_n=len(sub),level_r=sub.corr().iloc[0,1],difference_n=len(dif),difference_r=dif.corr().iloc[0,1]))
    pd.DataFrame(cor).to_csv(OUT/'traffic_speed_association.csv',index=False)
    s=df[(df.corridor=='WDFC')&(df.fy_start==2022)].speed_kmph
    sens={'exclude_disputed_month':float(s.mean()),'use_older_48_7':float((s.sum()+48.7)/12),'use_newer_58_7':float((s.sum()+58.7)/12)}
    dump('speed_discrepancy_sensitivity.json',sens)
    models=['Naive','Day-adjusted naive','Seasonal naive','12-month drift','Random forest']
    y=tr.trains.to_numpy(dtype=float); dates=list(tr.date)
    records=[]
    for split,start,end in [('Validation','2023-04-01','2024-03-01'),('Test','2024-04-01','2025-03-01')]:
        for t,date in enumerate(dates):
            if pd.Timestamp(start)<=date<=pd.Timestamp(end):
                for model in models:
                    pred=forecast(y,dates,t,model)
                    records.append(dict(split=split,date=date.strftime('%Y-%m-%d'),model=model,actual=y[t],prediction=pred,train_through=dates[t-1].strftime('%Y-%m-%d')))
    pred=pd.DataFrame(records)
    metrics=[]
    for (split,model),g in pred.groupby(['split','model']):
        metrics.append(dict(split=split,model=model,n=len(g),MAE=mean_absolute_error(g.actual,g.prediction),RMSE=np.sqrt(mean_squared_error(g.actual,g.prediction)),WAPE_pct=100*np.abs(g.actual-g.prediction).sum()/g.actual.sum()))
    metrics=pd.DataFrame(metrics)
    winner=metrics[metrics.split=='Validation'].sort_values('MAE').iloc[0].model
    metrics['selected_on_validation']=metrics.model.eq(winner)
    metrics.to_csv(OUT/'forecast_metrics.csv',index=False)
    pred.to_csv(OUT/'forecast_predictions.csv',index=False)
    val=pred[(pred.split=='Validation')&(pred.model==winner)]
    # Empirical validation residual band: descriptive, no coverage guarantee.
    width=float(np.quantile(np.abs(val.actual-val.prediction),.8,method='higher'))
    test=pred[(pred.split=='Test')&(pred.model==winner)].copy()
    test['lower']=np.maximum(0,test.prediction-width);test['upper']=test.prediction+width
    coverage=float(((test.actual>=test.lower)&(test.actual<=test.upper)).mean())
    test.to_csv(OUT/'selected_forecast_test.csv',index=False)
    dates_next=dates+[pd.Timestamp('2025-04-01')]
    nextpred=forecast(y,dates_next,len(y),winner)
    forecast_summary={'selected_model':winner,'selection_metric':'Validation MAE; Apr2023-Mar2024','test_period':'Apr2024-Mar2025, rolling one-step ahead','next_month':'2025-04-01','forecast_vintage':'retrospective monthly data cutoff 2025-03-31; publication vintages not reconstructed','next_prediction':nextpred,'heuristic_band_half_width':width,'next_lower':max(0,nextpred-width),'next_upper':nextpred+width,'test_band_coverage':coverage,'band_warning':'80th percentile of 12 validation absolute errors; not a calibrated confidence interval'}
    dump('forecast_summary.json',forecast_summary)
    cap=pd.read_csv(ROOT/'data/raw/conventional_capacity_reported.csv')
    cap['section']=cap['from']+'–'+cap['to']
    cap['total_trains']=cap.passenger_trains_day+cap.freight_trains_day+cap.other_trains_day
    cap['implied_effective_capacity']=cap.total_trains/(cap.reported_utilization_pct/100)
    cap['required_diversion_share_to_100']=(cap.total_trains-cap.implied_effective_capacity)/cap.freight_trains_day
    for d in [0,.25,.5,.75,1]:
        cap[f'util_at_{int(d*100)}pct_diversion']=cap.reported_utilization_pct*(cap.total_trains-d*cap.freight_trains_day)/cap.total_trains
    cap.to_csv(OUT/'capacity_scenarios.csv',index=False)
    assumptions={'trains_per_day':20,'operating_days':300,'value_per_train_hour_inr':5000,'capital_cost_crore':.4,'annual_opex_crore':.3,'base_hours_saved':1,'base_cash_realization':.4,'status':'All inputs hypothetical; not measured DFCCIL costs or savings'}
    dump('cost_assumptions.json',assumptions)
    costs=[]
    for label,h,r in [('Low',.25,.2),('Base',1,.4),('High',1.5,.6)]:
        gross=20*300*5000*h/1e7; cash=gross*r; net=cash-.3
        costs.append(dict(scenario=label,hours_saved=h,cash_realization=r,gross_time_value_crore=gross,realized_benefit_crore=cash,annual_net_crore=net,first_year_net_crore=net-.4,payback_months=.4/net*12 if net>0 else None))
    pd.DataFrame(costs).to_csv(OUT/'cost_benefit_scenarios.csv',index=False)
    # TF-IDF characterizes a deliberately curated evidence-card corpus, not all rail literature.
    cards=json.loads((ROOT/'data/clean/evidence_cards.json').read_text())
    vec=TfidfVectorizer(stop_words='english',ngram_range=(1,2),max_features=500)
    X=vec.fit_transform([c['summary'] for c in cards]); terms=vec.get_feature_names_out()
    nl=[]
    for i,c in enumerate(cards):
        ranked=np.argsort(X[i].toarray()[0])[::-1][:5]
        nl.append(dict(card_id=c['id'],source_id=c['source_id'],theme=c['theme'],top_terms='; '.join(terms[ranked])))
    pd.DataFrame(nl).to_csv(OUT/'text_analysis.csv',index=False)
    # Export strict JSON once; both the standalone dashboard and figures use these values.
    def records_json(frame): return json.loads(frame.to_json(orient='records',date_format='iso'))
    payload={'monthly':records_json(tr),'corridor':records_json(df),'annual':records_json(ann),'corridorAnnual':records_json(ca),'forecast':records_json(pred),'metrics':records_json(metrics),'selectedTest':records_json(test),'forecastSummary':forecast_summary,'capacity':records_json(cap),'cost':costs,'assumptions':assumptions,'cards':cards,'textAnalysis':nl}
    dump('dashboard_data.json',payload)
    latest=ca[ca.fy_start==2024].set_index('corridor'); prior=ca[ca.fy_start==2023].set_index('corridor')
    summary={'train_growth_pct':float((130116/88225-1)*100),'gtkm_growth_pct':float((gt[gt.fy_start==2024].gtkm_million.sum()/gt[gt.fy_start==2023].gtkm_million.sum()-1)*100),'EDFC_speed_latest':float(latest.loc['EDFC','speed_mean']),'EDFC_speed_prior':float(prior.loc['EDFC','speed_mean']),'EDFC_wtr_latest':float(latest.loc['EDFC','wtr_mean']),'EDFC_wtr_prior':float(prior.loc['EDFC','wtr_mean']),'EDFC_wtr_change_pct':float((latest.loc['EDFC','wtr_mean']/prior.loc['EDFC','wtr_mean']-1)*100),'WDFC_speed_latest':float(latest.loc['WDFC','speed_mean']),'WDFC_wtr_latest':float(latest.loc['WDFC','wtr_mean']),'selected_forecast_model':winner,'heuristic_test_coverage':coverage}
    dump('key_results.json',summary)
    print(json.dumps(summary,indent=2)); print(metrics.to_string(index=False))
    # Assertions address material data and leakage risks, not cosmetic implementation details.
    assert len(pred)==120 and all(pd.to_datetime(pred.train_through)<pd.to_datetime(pred.date))
    assert (cap['util_at_100pct_diversion']<=cap['util_at_0pct_diversion']).all()
    assert np.isclose(ann[ann.fy_start==2024].trains.iloc[0],130116)
    dump('analysis_checks.json',{'forecast_origin_order':'passed','forecast_records':len(pred),'capacity_monotonicity':'passed','annual_total_reconciliation':'passed','random_seed':42,'actuals_imputed':0})

if __name__=='__main__': main()
