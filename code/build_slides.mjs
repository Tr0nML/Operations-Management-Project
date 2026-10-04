// Optional authoring source; requires the first-party presentation runtime.
import fs from 'node:fs/promises';
import path from 'node:path';
import {pathToFileURL,fileURLToPath} from 'node:url';
import {Presentation,PresentationFile} from '@oai/artifact-tool';
const ROOT=path.resolve(path.dirname(fileURLToPath(import.meta.url)),'..');
const SKILL=process.env.PRESENTATIONS_SKILL_ROOT || '/root/.codex/skills/builtins/presentations';
const {resolvePresentationFont,applyPresentationChartFont,finalizePresentation}=await import(pathToFileURL(SKILL+'/container_tools/artifact_tool_utils.mjs').href);
const font=resolvePresentationFont({fontFamily:'Nimbus Sans'});
const p=Presentation.create({slideSize:{width:1280,height:720}});
const D=JSON.parse(await fs.readFile(ROOT+'/outputs/dashboard_data.json','utf8'));
const sources=JSON.parse(await fs.readFile(ROOT+'/data/clean/source_register.json','utf8'));
const INK='#143847',BLUE='#176B87',ORANGE='#C56634',GRAY='#637985',PALE='#EEF3F4',WHITE='#FFFFFF';
function shape(s,x,y,w,h,fill=BLUE,geometry='rect'){return s.shapes.add({geometry,position:{left:x,top:y,width:w,height:h},fill,line:{fill:'none',width:0}})}
function txt(s,text,x,y,w,h,size=26,color=INK,bold=false){let z=shape(s,x,y,w,h,'none','textbox');z.text=text;z.text.style={typeface:font,fontSize:size,color,bold,autoFit:'none'};return z}
function base(title,kicker,source='Study calculations',dark=false){let s=p.slides.add();s.background.fill=dark?INK:WHITE;let color=dark?WHITE:INK;txt(s,kicker.toUpperCase(),64,36,1100,26,14,dark?'#A5CDD7':BLUE,true);txt(s,title,64,83,1150,102,42,color,true);shape(s,64,668,1152,1,dark?'#42606C':'#D9E3E6');txt(s,source,64,681,1060,22,12,dark?'#BDD0D7':GRAY);txt(s,String(p.slides.items?.length||0),1170,679,46,24,14,dark?'#BDD0D7':GRAY);return s}
function notes(s,text,ids=[]){s.speakerNotes.textFrame.setText(text+'\n\nSources\n'+ids.map(id=>{let a=sources.find(z=>z.id===id);return a?`${a.id}: ${a.author}. (${a.year}). ${a.title}. ${a.url}`:id}).join('\n'))}
function chart(s,type,x,y,w,h,categories,series,opts={}){let c=s.charts.add(type,{position:{left:x,top:y,width:w,height:h},categories,series:series.map(a=>({...a,valuesFormatCode:'#,##0.00',dataLabelOverrides:a.values.map((v,idx)=>({idx,text:Number.isInteger(v)?v.toLocaleString('en-US'):v.toFixed(v<100?2:1),showValue:false,textStyle:{typeface:font,fontSize:20,fill:INK}}))})),hasLegend:series.length>1,legend:{position:'bottom',textStyle:{fontSize:18,fill:GRAY}},chartFill:WHITE,plotAreaFill:WHITE,chartLine:{fill:'none',width:0},plotAreaLine:{fill:'none',width:0},barOptions:{direction:'column',grouping:'clustered',gapWidth:100},xAxis:{textStyle:{fontSize:18,fill:GRAY},majorGridlines:null},yAxis:{min:0,textStyle:{fontSize:18,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:20,fill:INK}},...opts});applyPresentationChartFont(c,{fontFamily:font});return c}
function nativeTable(s,values,x,y,w,h,widths){let t=s.tables.add({rows:values.length,columns:values[0].length,left:x,top:y,width:w,height:h,columnWidths:widths,values});t.borders.assign({fill:'#D5DFE3',width:1,style:'solid'});for(let i=0;i<values.length;i++)for(let j=0;j<values[i].length;j++){let c=t.getCell(i,j);c.fill=i===0?INK:i%2?WHITE:PALE;c.text.style={typeface:font,fontSize:22,color:i===0?WHITE:INK,bold:i===0};}return t}

// 1: The decision and main evidence, with student details intentionally editable.
{
let s=p.slides.add();s.background.fill=INK;txt(s,'OPERATIONS MANAGEMENT  ·  WORKING WITH AI',64,50,1110,30,16,'#A8D3DD',true);
txt(s,'Dedicated freight corridors\nand operating performance',64,122,1110,180,60,WHITE,true);
txt(s,'Indian Railways and DFCCIL  |  Public evidence through March 2025',68,326,1100,44,25,'#C4DCE3');
shape(s,68,414,1100,2,'#47636E');txt(s,'47.5%',64,445,355,100,76,'#7BC7D9',true);txt(s,'more train movements\nin FY2024–25',70,548,420,74,26,WHITE);
txt(s,'Growth is clear.\nReliable interfaces need investigation.',560,456,610,116,34,WHITE,true);
txt(s,'Student name: __________________   Roll: ____________   |   4 October 2026',70,662,1120,30,18,'#C4DCE3');
notes(s,'Introduce yourself. This study audits DFC growth, tests forecasting methods and examines conditional capacity relief. The main recommendation is a measured EDFC interchange pilot. Counts:130116/88225−1=47.482%.',['S1']);
}
// 2: Operational problem, not a causal before-and-after claim.
{
let s=base('Capacity must translate into reliable journeys','Problem and decision','Framework: capacity management and bottleneck diagnosis');
txt(s,'Conventional network',66,217,400,35,25,INK,true);txt(s,'DFC system',66,381,350,35,25,INK,true);
shape(s,66,270,324,70,PALE);txt(s,'Passenger + freight',88,288,286,45,25);shape(s,425,287,100,28,BLUE,'rightArrow');shape(s,560,270,600,70,PALE);txt(s,'Compete for shared paths and junctions',581,288,560,45,25);
shape(s,66,431,255,75,PALE);txt(s,'Freight flow',90,452,220,40,25);shape(s,345,451,65,26,BLUE,'rightArrow');shape(s,435,431,312,75,PALE);txt(s,'Dedicated corridor',455,452,276,40,25);shape(s,771,451,65,26,BLUE,'rightArrow');shape(s,861,431,300,75,PALE);txt(s,'Interchange / terminal',879,452,275,40,24);
txt(s,'Decision: identify and measure the limiting interface before scaling investment.',66,565,1110,68,29,BLUE,true);
notes(s,'Separating freight changes the capacity structure, but end-to-end performance also depends on interfaces. Little’s Law is not used to estimate fleets because public throughput and turnround metrics have incompatible boundaries. No matched national causal before/after effect is claimed.',['S3','S6','S10']);
}
// 3: Audit and workflow.
{
let s=base('Public data is usable after an explicit audit','Method and evidence','Sources: DFCCIL reports; World Bank ICR; source register');
let nodes=[['Collect','Official public sources'],['Audit','Totals and report vintages'],['Analyze','Trends, forecasts, scenarios'],['Review','Managerial implications']];
nodes.forEach((a,i)=>{let x=64+i*294;shape(s,x,221,252,125,i===1?BLUE:PALE);txt(s,a[0],x+18,235,220,36,28,i===1?WHITE:INK,true);txt(s,a[1],x+18,278,220,61,18,i===1?WHITE:GRAY);if(i<3)shape(s,x+260,258,27,23,BLUE,'rightArrow')});
[['52','monthly train counts'],['96','corridor-month records'],['3','disputed cells excluded']].forEach((a,i)=>{let x=74+i*397;txt(s,a[0],x,381,300,87,64,i===2?ORANGE:BLUE,true);txt(s,a[1],x,478,337,44,24,INK)});
txt(s,'Raw cells retained · No synthetic observations · Ten public sources',74,579,1090,48,27,INK,true);
notes(s,'444 metric cells were extracted alongside52 total train counts. Three excluded observed cells are two February2023 corridor train rates and one March2023 WDFC speed. The earlier twelve months of corridor train-rate data are outside the selected Table2 coverage, not zero. All five annual train sums reconcile.',['S1','S2','S3','S5']);
}
// 4: Throughput.
{
let s=base('DFC train movements increased by 47.5%','Finding one','Source: DFCCIL 2024–25, printed p48, Tables3–4');
let a=D.annual.filter(r=>r.fy_start>=2021);chart(s,'bar',62,204,775,385,a.map(r=>`FY${r.fy_start}–${String(r.fy_start+1).slice(2)}`),[{name:'Train movements',values:a.map(r=>r.trains),fill:BLUE}],{yAxis:{min:0,max:150000,majorUnit:50000,numberFormatCode:'#,##0',textStyle:{fontSize:18,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:22,fill:INK}}});
txt(s,'61.3%',887,229,300,97,64,BLUE,true);txt(s,'Gross tonne-km growth\nFY2024–25',885,340,310,100,25,INK);
txt(s,'Growth includes network expansion. It is not a same-network productivity estimate.',890,464,302,145,24,GRAY);
notes(s,'Totals23544,62277,88225,130116. Growth47.482%. GTKMs119128 to192144million, growth61.292%. GTKM incorporates gross weight and distance; it is not net cargo tonnes. December2020–March2021 is excluded from this annual comparison because it is partial.',['S1']);
}
// 5: Service performance.
{
let s=base('EDFC speed fell as wagon turnround increased','Finding two','Source: DFCCIL 2024–25, Tables 5–6; unweighted means of 12 months');
txt(s,'Mean speed in km/h',70,209,540,38,25,INK,true);txt(s,'Mean wagon turnround in days',685,209,535,38,25,INK,true);
chart(s,'bar',60,258,550,290,['EDFC','WDFC'],[{name:'FY2023–24',values:[45.11,54.11],fill:GRAY},{name:'FY2024–25',values:[41.65,51.97],fill:BLUE}],{yAxis:{min:0,max:65,numberFormatCode:'0.0',textStyle:{fontSize:17,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:18,fill:INK}}});
chart(s,'bar',675,258,545,290,['EDFC','WDFC'],[{name:'FY2023–24',values:[1.22,.80],fill:GRAY},{name:'FY2024–25',values:[1.64,.78],fill:ORANGE}],{yAxis:{min:0,max:2,numberFormatCode:'0.00',textStyle:{fontSize:17,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:18,fill:INK}}});
txt(s,'EDFC turnround +34.2%  →  investigate journey mix and interface delays',70,581,1135,55,29,ORANGE,true);
notes(s,'Speed45.11 to41.65; turnround1.22 to1.64. Monthly arithmetic means are not official weighted annual metrics. WTR is not terminal dwell. EDFC traffic-speed correlation is−.86 in levels but−.31 in monthly changes, warning against trend-driven causal claims.',['S1','S2','S4']);
}
// 6: Forecasting.
{
let s=base('The simple forecast outperformed random forest','Model evaluation','Retrospective test: April 2024–March 2025 ·12 rolling one-month forecasts');
let names=['Day adjusted','Naive','12m drift','Random forest','Seasonal naive'];let vals=[4.66,7.42,7.80,9.94,32.20];chart(s,'bar',65,214,790,366,names,[{name:'Test WAPE %',values:vals,fill:BLUE,points:[{idx:3,fill:ORANGE}]}],{yAxis:{min:0,max:36,numberFormatCode:'0.0',textStyle:{fontSize:18,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:21,fill:INK}}});
txt(s,'4.66%',899,225,286,96,65,BLUE,true);txt(s,'test WAPE',900,331,276,43,27);txt(s,'Model selected using\nthe preceding validation year.',900,409,288,112,26,GRAY);
txt(s,'Last month’s daily rate × days in next month',77,596,1070,46,28,INK,true);
notes(s,'ValidationMAE298 for day-adjusted naive vs586 forRF. TestMAE505 vs1078. RF parameters200trees,max_depth3,min_samples_leaf3,seed42. All prediction origins use strictly prior data. WAPE=sum absolute errors /sum actuals. Experimental80th percentile residual band covers only5/12test values. No reliable operating interval is claimed.',['S8','S9']);
}
// 7: Scenarios.
{
let s=base('Diversion can relieve pressure unevenly','Capacity scenario','World Bank ICR 2024, Annex 4 Table 5 · FY2022–23 historical base');
chart(s,'bar',56,211,826,390,['DDU–Allahabad','Kanpur–Tundla','Khurja–Dadri'],[{name:'Reported historical',values:[148,129,126],fill:GRAY},{name:'50% more freight diverted',values:[119.8,118.0,109.6],fill:BLUE}],{barOptions:{direction:'bar',grouping:'clustered',gapWidth:85},yAxis:{min:0,max:175,numberFormatCode:'0.0',textStyle:{fontSize:18,fill:GRAY},majorGridlines:{fill:'#E1E8EB',width:1}},dataLabels:{showValue:true,position:'outEnd',textStyle:{fontSize:18,fill:INK}}});
txt(s,'148% → 120%',909,240,295,74,40,BLUE,true);txt(s,'DDU–Allahabad\nnormalized utilization',911,331,288,91,25);
txt(s,'Equal train weights.\nPassenger demand fixed.\nNot current observed relief.',911,466,286,142,24,GRAY);
notes(s,'Normalization=reported utilization*(total−d*freight)/total. Nominal capacity and reported utilization have different maintenance conventions; do not use them interchangeably. Base period is already partly post-DFC. Kanpur–Tundla still107% at100% diversion; DDU–Allahabad requires85.0% to reach100. No causal or current-capacity interpretation.',['S3']);
}
// 8: Tool demonstration and reproducible code.
{
let s=base('The dashboard makes assumptions inspectable','AI tools and demonstration','Seven visuals · Local source retrieval · No external API or operational connection');
const imageBytes=await fs.readFile(ROOT+'/screenshots/dashboard_top.png');s.images.add({blob:imageBytes,contentType:'image/png',alt:'Screenshot of the completed DFC dashboard with filters and operating charts',fit:'contain',position:{left:62,top:210,width:690,height:420}});
txt(s,'Three useful interactions',796,216,420,52,29,INK,true);
txt(s,'1  Filter corridor and period\n\n2  Change diversion and cost inputs\n\n3  Retrieve a cited evidence card',796,281,425,210,25,INK);
shape(s,793,530,422,67,INK);txt(s,'history = y[:t]',811,543,390,44,29,WHITE,true);
txt(s,'Only earlier observations enter each forecast.',797,608,418,45,19,GRAY);
notes(s,'Demonstrate year and corridor filters, forecast model switch and scenario slider. The code uses y[:t] and lagged features. TF-IDF ranks curated summaries; the local chatbot retrieves cited cards and abstains on weak matches. It cannot access live operational data. The screenshot is an actual browser capture of the delivered HTML dashboard.',['S8','S9']);
}
// 9: Pilot timeline and cost comparison.
{
let s=base('Test a twelve week coordination pilot','Recommendation and economics','All monetary inputs are hypothetical · INR crore');
nativeTable(s,[['Case','Hours saved','Cash share','Year 1 net'],['Low','0.25','20%','−0.55'],['Base','1.00','40%','0.50'],['High','1.50','60%','2.00']],64,209,740,246,[225,175,165,175]);
txt(s,'35 minutes',868,220,355,80,46,BLUE,true);txt(s,'saved per pilot train\nto break even in year one\nat 40% realization',874,322,335,145,26,INK);
[['Weeks 1–4','Define KPIs and baseline'],['Weeks 5–9','Pilot joint coordination'],['Weeks 10–12','Verify gains and decide']].forEach((a,i)=>{let x=64+i*390;shape(s,x,522,363,5,i===1?ORANGE:BLUE);txt(s,a[0],x,548,345,38,24,INK,true);txt(s,a[1],x,591,354,46,23,GRAY)});
notes(s,'Assume20trains/day,300days,INR5000/train-hour,setup0.4cr,annualopex0.3cr. Base1hour saved,40%cash realization:3crgross,1.2crrealized,.9crannualnet,.5crfirstyearnet. Simplepayback5.3months after steady state starts. Year1 breakeven35minutes. Does not include ramp-up,discounting,tax,finance or DFC construction. Monitor median and90th percentile dwell, safety, maintenance and downstream displacement.',['S6','S10']);
}
// 10: Close with the managerial decision and limits.
{
let s=base('Measure the interface before expanding the solution','Decision and responsible use','Research prepared 4 October 2026 · Full APA references in the report',true);
[['Recommend','A limited EDFC interchange coordination pilot'],['Measure','Timestamped dwell, matched trips and verified cash value'],['Retain','Human control, maintenance access and explicit uncertainty']].forEach((a,i)=>{let y=232+i*119;txt(s,a[0].toUpperCase(),68,y,260,35,18,'#8EC8D6',true);txt(s,a[1],357,y-3,810,78,31,WHITE)});
txt(s,'No national causal claim. No invented operational observations.',70,607,1090,38,25,'#C0D9E1');
notes(s,'Conclude: the dataset is sufficient for a defensible academic monitoring and scenario project, not nationwide causal attribution. The student should explain the audit, why ML did not win, and why costs remain assumptions. All sources follow. '+sources.map(a=>`${a.id} ${a.author} (${a.year}). ${a.title}. ${a.url}`).join('\n'),[]);
}

await fs.mkdir(ROOT+'/build/slides_preview',{recursive:true});
const candidate=ROOT+'/build/candidate.pptx';await(await PresentationFile.exportPptx(p)).save(candidate);
const slideList=p.slides.items;
for(let i=0;i<slideList.length;i++){
  const b=await p.export({slide:slideList[i],format:'png',scale:1});await fs.writeFile(`${ROOT}/build/slides_preview/slide-${i+1}.png`,new Uint8Array(await b.arrayBuffer()));
}
const out=process.env.DECK_OUTPUT||ROOT+'/submission/WAI_DFC_Presentation_Rebuilt.pptx';
const result=await finalizePresentation({workspaceDir:ROOT,candidatePath:candidate,finalPath:out,pythonExecutable:process.env.CODEX_PRIMARY_RUNTIME_PYTHON,integrityValidatorPath:SKILL+'/container_tools/inspect_presentation_package_integrity.py',layoutValidatorPath:SKILL+'/container_tools/inspect_presentation_layout_geometry.py',layoutArgs:['--expected-slide-size-emu','12192000,6858000','--validate-bullet-geometry','--validate-heading-fit','--require-native-table-slide','9'],explicitTotalSlideCount:10,requiredNativeTableOwnerSlides:[9],requiredNativeChartOwnerSlides:[4,5,6,7],materializeLiteralChartWorkbooks:true,fontPolicy:{basis:'design',families:[font]},verifyArtifactToolImport:true,receiptPath:ROOT+'/build/presentation_rebuilt_validation.json'});
console.log(JSON.stringify(result));
