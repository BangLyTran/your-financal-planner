from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')

if 'id="savingsForm"' in html and 'financial-planner-secure-v8-savings-investments' in SW.read_text(encoding='utf-8'):
    print('v8 savings and investment planner is already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

# ---------- CSS ----------
css_anchor = """    .planner-protection-note { grid-column:1 / -1; color:#7f1d1d; font-size:.8rem; line-height:1.45; }

    @media (max-width: 1100px) {"""
css_new = """    .planner-protection-note { grid-column:1 / -1; color:#7f1d1d; font-size:.8rem; line-height:1.45; }
    .chart-mode-toggle { display:inline-flex; gap:3px; padding:4px; border:1px solid #bfdbfe; background:#eff6ff; border-radius:11px; }
    .chart-mode-toggle button { border:0; border-radius:8px; padding:7px 10px; background:transparent; color:#475569; font-size:.78rem; font-weight:800; }
    .chart-mode-toggle button.active { background:#2563eb; color:#fff; box-shadow:0 4px 10px rgba(37,99,235,.2); }
    .chart-legend { display:flex; align-items:center; gap:14px; flex-wrap:wrap; margin-top:9px; color:var(--muted); font-size:.78rem; }
    .legend-line { display:inline-block; width:24px; height:3px; border-radius:999px; background:#2563eb; vertical-align:middle; margin-right:5px; }
    .legend-band { display:inline-block; width:24px; height:10px; border-radius:4px; background:rgba(96,165,250,.22); border:1px solid rgba(96,165,250,.38); vertical-align:middle; margin-right:5px; }
    .savings-hero { border:1px solid #bae6fd; background:linear-gradient(135deg,#effaff,#fff); }
    .savings-status { display:inline-flex; align-items:center; padding:4px 8px; border-radius:999px; font-size:.74rem; font-weight:850; }
    .savings-status.good { background:#dcfce7; color:#166534; }
    .savings-status.warn { background:#fef3c7; color:#92400e; }
    .savings-status.bad { background:#fee2e2; color:#991b1b; }
    .savings-guidance { margin-top:14px; padding:13px 14px; border-radius:12px; border:1px solid #bae6fd; background:#f0f9ff; color:#0c4a6e; line-height:1.5; }
    .historical-reference { margin-top:12px; padding:12px 14px; border-radius:12px; background:#f8fafc; border:1px solid var(--line); color:#475569; font-size:.8rem; line-height:1.5; }
    .investment-value { color:#0369a1; }
    .shortfall-value { color:#b45309; }

    @media (max-width: 1100px) {"""
html = replace_once(html, css_anchor, css_new, 'savings CSS')

# ---------- Header / navigation / dashboard ----------
html = replace_once(
    html,
    'Cash-flow forecasting, Texas take-home estimates, recurring bills, debt planning, and vehicle scenarios.',
    'Cash-flow forecasting, income, spending, debt, savings, investments, and vehicle scenarios.',
    'header subtitle'
)

nav_old = """    <button class="tab-btn" data-tab="bills">Bills & payments</button>
    <button class="tab-btn" data-tab="debts">Debts</button>"""
nav_new = """    <button class="tab-btn" data-tab="bills">Bills & payments</button>
    <button class="tab-btn" data-tab="savings">Savings & investments</button>
    <button class="tab-btn" data-tab="debts">Debts</button>"""
html = replace_once(html, nav_old, nav_new, 'savings nav tab')

net_card_old = """        <div class="card">
          <div class="label">Cash less debt</div>
          <div class="value" id="netPosition">$0</div>
          <div class="detail">Cash minus projected debt balances</div>
        </div>"""
net_card_new = """        <div class="card">
          <div class="label">Net financial position</div>
          <div class="value" id="netPosition">$0</div>
          <div class="detail">Liquid cash + projected investments − debt</div>
        </div>"""
html = replace_once(html, net_card_old, net_card_new, 'net position card')

chart_head_old = """          <div class="panel-head">
            <div>
              <h2>Projected cash balance</h2>
              <div class="muted small">Every income, bill, debt payment, and enabled vehicle cost through the target date.</div>
            </div>
          </div>
          <canvas id="cashChart" width="1000" height="330"></canvas>"""
chart_head_new = """          <div class="panel-head">
            <div>
              <h2>Projected cash and investments</h2>
              <div class="muted small" id="chartModeDetail">Spendable cash plus saved principal, without market growth.</div>
              <div class="chart-legend" id="chartLegend"><span><span class="legend-line"></span>Cash + investment principal</span></div>
            </div>
            <div class="chart-mode-toggle" id="chartModeToggle" aria-label="Investment chart mode">
              <button type="button" data-chart-mode="principal">Principal only</button>
              <button type="button" data-chart-mode="growth">With investment growth</button>
            </div>
          </div>
          <canvas id="cashChart" width="1000" height="330"></canvas>"""
html = replace_once(html, chart_head_old, chart_head_new, 'investment chart controls')

# ---------- Savings section ----------
savings_section = """
    <section id="savings" class="tab">
      <div class="panel savings-hero">
        <div class="panel-head">
          <div>
            <h2>Smart savings and investment plan</h2>
            <div class="muted small">Contributions are scheduled immediately after paychecks. They reduce spendable cash, while the planner reserves upcoming bills, protects a checking floor, and defers investing when expensive or urgent debt should come first.</div>
          </div>
          <label class="switch"><input id="savingsEnabled" type="checkbox" /> Enable savings plan</label>
        </div>
        <form id="savingsForm">
          <div class="form-grid">
            <div><label>Monthly savings / investment target</label><input id="savingsMonthlyTarget" type="number" step="50" min="0" /></div>
            <div><label>Starting investment balance</label><input id="savingsStartingBalance" type="number" step="100" min="0" /></div>
            <div><label>Contribution timing</label><select id="savingsTiming"><option value="eachPaycheck">Split across paychecks in the month</option><option value="firstPaycheck">Try the full target after the first paycheck</option></select></div>
            <div><label>Minimum spendable-cash floor</label><input id="savingsCashFloor" type="number" step="100" min="0" /></div>
            <div><label>Essential-cost safety buffer %</label><input id="savingsEssentialBuffer" type="number" step="1" min="0" max="100" /></div>
            <div><label>Debt-first APR threshold</label><input id="savingsDebtFirstApr" type="number" step="0.5" min="0" /><div class="muted small">Investing is reduced while debt at or above this rate remains.</div></div>
            <div><label>Minimum monthly investment while debt comes first</label><input id="savingsMinimumWhileDebt" type="number" step="25" min="0" /></div>
            <div><label>Return assumption preset</label><select id="savingsReturnPreset"><option value="sp50010y">S&P 500 trailing 10-year reference</option><option value="longTerm">Long-term broad-market reference</option><option value="conservative">Conservative planning case</option><option value="custom">Custom</option></select></div>
            <div><label>Expected annual investment return %</label><input id="savingsExpectedReturn" type="number" step="0.1" min="-50" max="50" /></div>
            <div><label>Annual volatility %</label><input id="savingsVolatility" type="number" step="0.1" min="0" max="80" /></div>
          </div>
          <div class="actions">
            <button class="btn" type="submit">Save savings plan</button>
            <button class="btn good" type="button" id="rebuildIntegratedPlan">Rebuild debt + savings plan</button>
          </div>
        </form>
        <div class="historical-reference">Historical reference used by the preset: the S&amp;P 500 delivered approximately 14.8% annualized total return over the 10 years through 2025. The uncertainty band uses a 20.8% annual-volatility reference. Historical performance is not a promise or forecast.</div>
        <div id="savingsPlanSummary" class="savings-guidance"></div>
      </div>

      <div class="grid cards" style="margin-top:16px">
        <div class="card"><div class="label">Monthly target</div><div class="value" id="savingsTargetMetric">$0</div><div class="detail">Desired contribution each calendar month</div></div>
        <div class="card"><div class="label">Projected contributions</div><div class="value positive" id="savingsContributionMetric">$0</div><div class="detail" id="savingsContributionDetail"></div></div>
        <div class="card"><div class="label">Investment at target</div><div class="value investment-value" id="savingsInvestmentMetric">$0</div><div class="detail" id="savingsInvestmentDetail"></div></div>
        <div class="card"><div class="label">Unfunded target</div><div class="value shortfall-value" id="savingsShortfallMetric">$0</div><div class="detail">Target reduced by debt or cash-flow constraints</div></div>
      </div>

      <div class="panel" style="margin-top:16px">
        <div class="panel-head"><div><h2>Monthly savings feasibility</h2><div class="muted small">The planner never forces savings that would violate the cash floor or leave insufficient money for scheduled costs before the next paycheck.</div></div></div>
        <div class="table-wrap"><table><thead><tr><th>Month</th><th>Target</th><th>Contributed</th><th>Shortfall</th><th>Essential costs</th><th>Flexible spending</th><th>Planner response</th></tr></thead><tbody id="savingsMonthlyTable"></tbody></table></div>
      </div>
    </section>

"""
html = replace_once(html, '    <section id="debts" class="tab">', savings_section + '    <section id="debts" class="tab">', 'savings section')

# ---------- State ----------
state_old = """    incomes: [],
    bills: [],
    debts: [],
    debtPlanner: {"""
state_new = """    incomes: [],
    bills: [],
    debts: [],
    savings: {
      enabled: false,
      monthlyTarget: 1000,
      startingBalance: 0,
      timing: 'eachPaycheck',
      cashFloor: 2500,
      essentialBufferPct: 10,
      debtFirstApr: 10,
      minimumWhileDebt: 0,
      returnPreset: 'sp50010y',
      expectedReturn: 14.8,
      volatility: 20.8,
      chartMode: 'principal'
    },
    debtPlanner: {"""
html = replace_once(html, state_old, state_new, 'savings default state')

normalize_old = """      vehicle: Object.assign({}, defaultState.vehicle, parsed?.vehicle || {}),
      debtPlanner: Object.assign({}, defaultState.debtPlanner, parsed?.debtPlanner || {}),
      incomes: Array.isArray(parsed?.incomes) ? parsed.incomes : clone(defaultState.incomes),"""
normalize_new = """      vehicle: Object.assign({}, defaultState.vehicle, parsed?.vehicle || {}),
      debtPlanner: Object.assign({}, defaultState.debtPlanner, parsed?.debtPlanner || {}),
      savings: Object.assign({}, defaultState.savings, parsed?.savings || {}),
      incomes: Array.isArray(parsed?.incomes) ? parsed.incomes : clone(defaultState.incomes),"""
html = replace_once(html, normalize_old, normalize_new, 'savings normalization')

# ---------- Utility helpers ----------
utils_anchor = """  function recurrenceLabel(v) { return ({none:'One time',weekly:'Weekly',biweekly:'Every 2 weeks',monthly:'Monthly',quarterly:'Quarterly',annual:'Annual'})[v] || v; }
  function scheduleLabel(item) { return `${fmtDate(item.startDate)} · ${recurrenceLabel(item.recurrence)}${item.endDate ? ` through ${fmtDate(item.endDate)}`:''}`; }
"""
utils_new = """  function recurrenceLabel(v) { return ({none:'One time',weekly:'Weekly',biweekly:'Every 2 weeks',monthly:'Monthly',quarterly:'Quarterly',annual:'Annual'})[v] || v; }
  function scheduleLabel(item) { return `${fmtDate(item.startDate)} · ${recurrenceLabel(item.recurrence)}${item.endDate ? ` through ${fmtDate(item.endDate)}`:''}`; }
  function monthKey(date) { return String(date||'').slice(0,7); }
  function monthLabel(key) { return parseDate(`${key}-01`).toLocaleDateString('en-US',{month:'long',year:'numeric'}); }
  function monthKeysBetween(startDate,endDate) {
    const out=[]; let d=parseDate(`${monthKey(startDate)}-01`); const end=parseDate(`${monthKey(endDate)}-01`); let guard=0;
    while(d<=end&&guard++<600){out.push(toISO(d).slice(0,7));d=addMonths(d,1);} return out;
  }
  function shiftIncomeDateOneYear(date,recurrence) {
    if(!date)return '';
    return ['weekly','biweekly'].includes(recurrence)?toISO(addDays(parseDate(date),364)):toISO(addMonths(parseDate(date),12));
  }
  function eventPriority(event) {
    if(event.source==='income')return 0;
    if(event.source==='savings')return 1;
    if(event.type==='Debt payment')return 2;
    return 3;
  }
  function sortForecastEvents(events) { return events.sort((a,b)=>a.date.localeCompare(b.date)||eventPriority(a)-eventPriority(b)||(b.amountUSD-a.amountUSD)); }
  function finalizeForecastEvents(events) {
    sortForecastEvents(events);
    let balance=Number(state.settings.startingCash)||0;
    let principal=Math.max(0,Number(state.savings?.startingBalance)||0);
    events.forEach(e=>{balance+=e.amountUSD;e.runningBalance=balance;if(e.source==='savings')principal+=Math.abs(e.amountUSD);e.investmentPrincipalUSD=principal;});
    return events;
  }
"""
html = replace_once(html, utils_anchor, utils_new, 'savings utility helpers')

# ---------- Savings simulation and event engine ----------
build_events_old = """  function buildEvents(targetDate=state.settings.targetDate, includeDebtPayments=true, suppliedDebtSimulation=null) {
    const events=[];
    state.incomes.filter(x=>x.active).forEach(item=>{
      const netUSD=toUSD(estimateIncomeNet(item),item.currency);
      const grossUSD=toUSD(Number(item.gross)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:'Income',amountUSD:netUSD,grossUSD,source:'income',sourceId:item.id}));
    });
    state.bills.filter(x=>x.active && !x.debtId).forEach(item=>{
      const amountUSD=toUSD(Number(item.amount)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:item.category,amountUSD:-amountUSD,source:'bill',sourceId:item.id,debtId:''}));
    });
    if(includeDebtPayments) events.push(...(suppliedDebtSimulation||simulateDebtPayments(targetDate)).events);
    events.push(...buildVehicleEvents(targetDate));
    events.sort((a,b)=> a.date.localeCompare(b.date) || (b.amountUSD-a.amountUSD));
    let balance=Number(state.settings.startingCash)||0;
    events.forEach(e=>{ balance+=e.amountUSD; e.runningBalance=balance; });
    return events;
  }
"""

build_events_new = """  function isEssentialForecastEvent(event) {
    return ['Housing','Food','Utilities','Health','Transportation','Vehicle'].includes(event.type);
  }

  function buildSavingsProjection(baseEvents,targetDate=state.settings.targetDate) {
    const cfg=Object.assign({},defaultState.savings,state.savings||{});
    const paydays=[...new Set(baseEvents.filter(e=>e.source==='income').map(e=>e.date))].sort();
    const firstMonth=paydays.length?monthKey(paydays[0]):monthKey(state.settings.forecastStart);
    const keys=monthKeysBetween(`${firstMonth}-01`,targetDate);
    const monthMap=new Map(keys.map(key=>[key,{key,target:cfg.enabled?Math.max(0,Number(cfg.monthlyTarget)||0):0,contributed:0,essential:0,flexible:0,reasons:new Set(),paydays:paydays.filter(d=>monthKey(d)===key)}]));
    baseEvents.filter(e=>e.amountUSD<0).forEach(e=>{const m=monthMap.get(monthKey(e.date));if(!m)return;if(isEssentialForecastEvent(e))m.essential+=Math.abs(e.amountUSD);else if(['Discretionary','Other'].includes(e.type))m.flexible+=Math.abs(e.amountUSD);});
    const emptyResult={events:[],months:[...monthMap.values()].map(m=>({...m,shortfall:m.target,status:m.target?'No contributions scheduled':'Disabled',reasons:[...m.reasons]})),totalTarget:[...monthMap.values()].reduce((s,m)=>s+m.target,0),totalContributed:0,totalShortfall:[...monthMap.values()].reduce((s,m)=>s+m.target,0),endingPrincipal:Math.max(0,Number(cfg.startingBalance)||0)};
    if(!cfg.enabled||Number(cfg.monthlyTarget)<=0||!paydays.length)return emptyResult;

    const eventDates=[...new Set(baseEvents.map(e=>e.date))].sort();
    const eventsByDate=new Map();
    baseEvents.forEach(e=>{if(!eventsByDate.has(e.date))eventsByDate.set(e.date,[]);eventsByDate.get(e.date).push(e);});
    let cash=Number(state.settings.startingCash)||0;
    let principal=Math.max(0,Number(cfg.startingBalance)||0);
    let totalContributed=0;
    const savingsEvents=[];

    for(const day of eventDates){
      const dayEvents=sortForecastEvents([...(eventsByDate.get(day)||[])]);
      const incomeEvents=dayEvents.filter(e=>e.source==='income');
      const nonIncomeEvents=dayEvents.filter(e=>e.source!=='income');
      incomeEvents.forEach(e=>cash+=e.amountUSD);

      if(paydays.includes(day)){
        const m=monthMap.get(monthKey(day));
        const paydayIndex=paydays.indexOf(day);
        const nextPayday=paydays[paydayIndex+1]||'9999-12-31';
        const remainingPaydays=m.paydays.filter(d=>d>=day).length||1;
        const remainingTarget=Math.max(0,m.target-m.contributed);
        const normalDesired=cfg.timing==='firstPaycheck'?remainingTarget:remainingTarget/remainingPaydays;
        const debtSnapshot=simulateDebtPayments(day).projections;
        const urgentDebt=state.debts.some(d=>isUrgentDebt(d)&&(debtSnapshot[d.id]?.balanceUSD||0)>.01);
        const highCostDebt=state.debts.some(d=>(debtSnapshot[d.id]?.balanceUSD||0)>.01&&debtPlannerRate(d,day)>=Math.max(0,Number(cfg.debtFirstApr)||0));
        let desired=normalDesired;
        if(urgentDebt||highCostDebt){
          const minimumMonthly=Math.min(m.target,Math.max(0,Number(cfg.minimumWhileDebt)||0));
          const minimumRemaining=Math.max(0,minimumMonthly-m.contributed);
          desired=Math.min(normalDesired,cfg.timing==='firstPaycheck'?minimumRemaining:minimumRemaining/remainingPaydays);
          m.reasons.add(urgentDebt?'Urgent debt takes priority':'High-interest debt takes priority');
        }
        const upcoming=baseEvents.filter(e=>e.amountUSD<0&&e.date>=day&&e.date<nextPayday);
        const upcomingOutflows=upcoming.reduce((s,e)=>s+Math.abs(e.amountUSD),0);
        const upcomingEssential=upcoming.filter(isEssentialForecastEvent).reduce((s,e)=>s+Math.abs(e.amountUSD),0);
        const buffer=upcomingEssential*Math.max(0,Number(cfg.essentialBufferPct)||0)/100;
        const safeAvailable=Math.max(0,cash-upcomingOutflows-buffer-Math.max(0,Number(cfg.cashFloor)||0));
        const contribution=Math.max(0,Math.min(desired,safeAvailable));
        if(contribution+.01<desired)m.reasons.add('Cash reserved for bills and living costs');
        if(normalDesired>desired+.01)m.reasons.add('Savings target reduced to favor debt');
        if(contribution>.005){
          cash-=contribution;principal+=contribution;m.contributed+=contribution;totalContributed+=contribution;
          savingsEvents.push({date:day,name:'Automatic savings / investment',type:'Savings / investment',amountUSD:-contribution,source:'savings',sourceId:`savings_${day}`,investmentContributionUSD:contribution});
        }
      }
      nonIncomeEvents.forEach(e=>cash+=e.amountUSD);
    }

    const months=[...monthMap.values()].map(m=>{
      const shortfall=Math.max(0,m.target-m.contributed);
      if(!m.paydays.length&&m.target>0)m.reasons.add('No paycheck scheduled this month');
      const status=shortfall<=.01?'Target met':m.contributed>0?'Partially funded':'Not funded';
      return {...m,shortfall,status,reasons:[...m.reasons]};
    });
    const totalTarget=months.reduce((s,m)=>s+m.target,0);
    return {events:savingsEvents,months,totalTarget,totalContributed,totalShortfall:Math.max(0,totalTarget-totalContributed),endingPrincipal:principal};
  }

  function seededRandom(seedText) {
    let seed=2166136261;
    for(const ch of String(seedText)){seed^=ch.charCodeAt(0);seed=Math.imul(seed,16777619);}
    return ()=>{seed+=0x6D2B79F5;let t=seed;t=Math.imul(t^t>>>15,t|1);t^=t+Math.imul(t^t>>>7,t|61);return((t^t>>>14)>>>0)/4294967296;};
  }
  function normalRandom(rand) { const u=Math.max(1e-12,rand()),v=Math.max(1e-12,rand());return Math.sqrt(-2*Math.log(u))*Math.cos(2*Math.PI*v); }
  function percentile(sorted,q) { if(!sorted.length)return 0;const pos=(sorted.length-1)*q,base=Math.floor(pos),rest=pos-base;return sorted[base+1]!==undefined?sorted[base]+rest*(sorted[base+1]-sorted[base]):sorted[base]; }

  function buildInvestmentProjection(events) {
    const cfg=Object.assign({},defaultState.savings,state.savings||{});
    const paths=320;
    const rand=seededRandom(`${state.settings.forecastStart}|${state.settings.targetDate}|${cfg.expectedReturn}|${cfg.volatility}|${events.length}`);
    const balances=Array(paths).fill(Math.max(0,Number(cfg.startingBalance)||0));
    const rate=Math.max(-.95,Number(cfg.expectedReturn)||0)/100;
    const sigma=Math.max(0,Number(cfg.volatility)||0)/100;
    const mu=Math.log1p(rate);
    let previousDate=state.settings.forecastStart;
    let principal=Math.max(0,Number(cfg.startingBalance)||0);
    const points=[{date:state.settings.forecastStart,cash:Number(state.settings.startingCash)||0,principalInvestment:principal,principalTotal:(Number(state.settings.startingCash)||0)+principal,low:(Number(state.settings.startingCash)||0)+principal,median:(Number(state.settings.startingCash)||0)+principal,high:(Number(state.settings.startingCash)||0)+principal}];
    for(const event of events){
      const years=daysBetween(previousDate,event.date)/365;
      if(years>0&&cfg.enabled){
        const vol=sigma*Math.sqrt(years),drift=mu*years;
        for(let i=0;i<paths;i++)balances[i]*=Math.exp(drift+vol*normalRandom(rand));
      }
      if(event.source==='savings'){
        const contribution=Math.abs(event.amountUSD);principal+=contribution;for(let i=0;i<paths;i++)balances[i]+=contribution;
      }
      const sorted=[...balances].sort((a,b)=>a-b);
      const cash=event.runningBalance;
      points.push({date:event.date,cash,principalInvestment:principal,principalTotal:cash+principal,low:cash+percentile(sorted,.25),median:cash+percentile(sorted,.5),high:cash+percentile(sorted,.75)});
      previousDate=event.date;
    }
    const last=points[points.length-1];
    return {points,endingPrincipalInvestment:last.principalInvestment,endingLowInvestment:last.low-last.cash,endingMedianInvestment:last.median-last.cash,endingHighInvestment:last.high-last.cash};
  }

  function buildEvents(targetDate=state.settings.targetDate, includeDebtPayments=true, suppliedDebtSimulation=null, includeSavings=true) {
    const events=[];
    state.incomes.filter(x=>x.active).forEach(item=>{
      const netUSD=toUSD(estimateIncomeNet(item),item.currency);
      const grossUSD=toUSD(Number(item.gross)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:'Income',amountUSD:netUSD,grossUSD,source:'income',sourceId:item.id}));
    });
    state.bills.filter(x=>x.active && !x.debtId).forEach(item=>{
      const amountUSD=toUSD(Number(item.amount)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:item.category,amountUSD:-amountUSD,source:'bill',sourceId:item.id,debtId:''}));
    });
    if(includeDebtPayments) events.push(...(suppliedDebtSimulation||simulateDebtPayments(targetDate)).events);
    events.push(...buildVehicleEvents(targetDate));
    if(includeSavings)events.push(...buildSavingsProjection(events,targetDate).events);
    return finalizeForecastEvents(events);
  }
"""
html = replace_once(html, build_events_old, build_events_new, 'savings event engine')

# ---------- Summary ----------
summary_old = """  function getSummary() {
    const debtSimulation=simulateDebtPayments(state.settings.targetDate);
    const events=buildEvents(state.settings.targetDate,true,debtSimulation);
    const income=events.filter(e=>e.amountUSD>0).reduce((s,e)=>s+e.amountUSD,0);
    const gross=events.filter(e=>e.source==='income').reduce((s,e)=>s+(e.grossUSD||0),0);
    const outflows=-events.filter(e=>e.amountUSD<0).reduce((s,e)=>s+e.amountUSD,0);
    const cash=(Number(state.settings.startingCash)||0)+income-outflows;
    const payoffHorizon=toISO(addMonths(parseDate(state.settings.targetDate),360));"""
summary_new = """  function getSummary() {
    const debtSimulation=simulateDebtPayments(state.settings.targetDate);
    const baseEvents=buildEvents(state.settings.targetDate,true,debtSimulation,false);
    const savingsProjection=buildSavingsProjection(baseEvents,state.settings.targetDate);
    const events=finalizeForecastEvents([...baseEvents.map(e=>({...e})),...savingsProjection.events.map(e=>({...e}))]);
    const income=events.filter(e=>e.amountUSD>0).reduce((s,e)=>s+e.amountUSD,0);
    const gross=events.filter(e=>e.source==='income').reduce((s,e)=>s+(e.grossUSD||0),0);
    const outflows=-events.filter(e=>e.amountUSD<0&&e.source!=='savings').reduce((s,e)=>s+e.amountUSD,0);
    const savingsContributions=events.filter(e=>e.source==='savings').reduce((s,e)=>s+Math.abs(e.amountUSD),0);
    const cash=events.length?events[events.length-1].runningBalance:(Number(state.settings.startingCash)||0);
    const investmentProjection=buildInvestmentProjection(events);
    const payoffHorizon=toISO(addMonths(parseDate(state.settings.targetDate),360));"""
html = replace_once(html, summary_old, summary_new, 'savings summary setup')

summary_return_old = """    return {events,income,gross,outflows,cash,totalDebt,revolvingDebt,interest,deadlineMarkup,debtProjections};"""
summary_return_new = """    return {events,income,gross,outflows,savingsContributions,cash,totalDebt,revolvingDebt,interest,deadlineMarkup,debtProjections,savingsProjection,investmentProjection};"""
html = replace_once(html, summary_return_old, summary_return_new, 'savings summary return')

# ---------- Render all / dashboard ----------
render_all_old = """    renderDashboard(); renderIncome(); renderBills(); renderDebts(); renderVehicle(); renderSettings(); populateDebtOptions(); renderDebtPlannerControls();"""
render_all_new = """    renderDashboard(); renderIncome(); renderBills(); renderSavings(); renderDebts(); renderVehicle(); renderSettings(); populateDebtOptions(); renderDebtPlannerControls();"""
html = replace_once(html, render_all_old, render_all_new, 'render savings tab')

cash_detail_old = """    document.getElementById('cashTargetDetail').textContent=`Starting cash ${money(state.settings.startingCash)} · ${fmtDate(state.settings.targetDate)}`;"""
cash_detail_new = """    document.getElementById('cashTargetDetail').textContent=`Spendable cash only · starting cash ${money(state.settings.startingCash)} · ${fmtDate(state.settings.targetDate)}`;"""
html = replace_once(html, cash_detail_old, cash_detail_new, 'cash target detail')

outflow_old = """    document.getElementById('outflowDetail').textContent=`Includes scheduled debt and vehicle payments`;"""
outflow_new = """    document.getElementById('outflowDetail').textContent=s.savingsContributions>0?`Excludes ${money(s.savingsContributions)} transferred into savings / investments`:`Includes scheduled debt and vehicle payments`;"""
html = replace_once(html, outflow_old, outflow_new, 'outflow savings detail')

np_old = """    const np=s.cash-s.totalDebt;
    const npEl=document.getElementById('netPosition'); npEl.textContent=money(np); npEl.className=`value ${np>=0?'positive':'negative'}`;"""
np_new = """    const np=s.cash+s.investmentProjection.endingMedianInvestment-s.totalDebt;
    const npEl=document.getElementById('netPosition'); npEl.textContent=money(np); npEl.className=`value ${np>=0?'positive':'negative'}`;"""
html = replace_once(html, np_old, np_new, 'net financial position')

snapshot_old = """      <div class="metric-row"><span>24%–27% debt remaining</span><strong class="warning">${money(highApr)}</strong></div>
      <div class="metric-row"><span>CAD conversion assumption</span><strong>C$${Number(state.settings.cadPerUsd).toFixed(4)} / US$1</strong></div>`;"""
snapshot_new = """      <div class="metric-row"><span>24%–27% debt remaining</span><strong class="warning">${money(highApr)}</strong></div>
      <div class="metric-row"><span>Projected investment value</span><strong class="investment-value">${money(s.investmentProjection.endingMedianInvestment)}</strong></div>
      <div class="metric-row"><span>Savings target funded</span><strong>${s.savingsProjection.totalTarget>0?Math.round(s.savingsProjection.totalContributed/s.savingsProjection.totalTarget*100):0}%</strong></div>
      <div class="metric-row"><span>CAD conversion assumption</span><strong>C$${Number(state.settings.cadPerUsd).toFixed(4)} / US$1</strong></div>`;"""
html = replace_once(html, snapshot_old, snapshot_new, 'savings dashboard metrics')

notice_old = """    else if (s.cash<2500) notice.innerHTML=`<div class="notice warn"><strong>Thin liquidity:</strong> projected cash on ${fmtDate(state.settings.targetDate)} is below a $2,500 starter reserve.</div>`;
    else notice.innerHTML=`<div class="notice"><strong>Forecast is cash-positive.</strong> Review the debt balance and ledger before treating the ending cash as spendable savings.</div>`;"""
notice_new = """    else if (s.cash<2500) notice.innerHTML=`<div class="notice warn"><strong>Thin liquidity:</strong> projected cash on ${fmtDate(state.settings.targetDate)} is below a $2,500 starter reserve.</div>`;
    else if(state.savings.enabled&&s.savingsProjection.totalShortfall>.01)notice.innerHTML=`<div class="notice warn"><strong>Savings target adjusted:</strong> the smart plan leaves ${money(s.savingsProjection.totalShortfall)} unfunded because debt, scheduled living costs, or the cash floor take priority.</div>`;
    else notice.innerHTML=`<div class="notice"><strong>Forecast is cash-positive.</strong> Savings contributions are removed from spendable cash and tracked separately as an investment asset.</div>`;"""
html = replace_once(html, notice_old, notice_new, 'savings risk notice')

ledger_draw_old = """    drawCashChart(s.events);
  }

  function drawCashChart(events) {"""
ledger_draw_new = """    const chartMode=state.savings?.chartMode||'principal';
    document.querySelectorAll('[data-chart-mode]').forEach(btn=>btn.classList.toggle('active',btn.dataset.chartMode===chartMode));
    document.getElementById('chartModeDetail').textContent=chartMode==='growth'?'Cash plus a simulated investment-value range. The blue line is the median path; the shaded area spans the 25th–75th percentiles.':'Spendable cash plus investment principal, without assuming any market growth.';
    document.getElementById('chartLegend').innerHTML=chartMode==='growth'?'<span><span class="legend-line"></span>Median cash + investments</span><span><span class="legend-band"></span>25th–75th percentile range</span>':'<span><span class="legend-line"></span>Cash + investment principal</span>';
    drawCashChart(s);
  }

  function drawCashChart(summary) {"""
html = replace_once(html, ledger_draw_old, ledger_draw_new, 'chart render mode')

# Replace complete old chart body.
chart_old = """  function drawCashChart(summary) {
    const canvas=document.getElementById('cashChart');
    const rect=canvas.getBoundingClientRect();
    const dpr=window.devicePixelRatio||1;
    canvas.width=Math.max(700,rect.width*dpr); canvas.height=330*dpr;
    const ctx=canvas.getContext('2d'); ctx.scale(dpr,dpr);
    const w=canvas.width/dpr,h=canvas.height/dpr,p={l:60,r:22,t:20,b:42};
    ctx.clearRect(0,0,w,h);
    const points=[{date:state.settings.forecastStart,balance:Number(state.settings.startingCash)||0},...summary.map(e=>({date:e.date,balance:e.runningBalance}))];
    const vals=points.map(x=>x.balance); let min=Math.min(...vals,0),max=Math.max(...vals,0); if(max===min){max+=1;min-=1;} const pad=(max-min)*.12; max+=pad;min-=pad;
    const x=i=>p.l+(w-p.l-p.r)*(points.length===1?0:i/(points.length-1));
    const y=v=>p.t+(h-p.t-p.b)*(max-v)/(max-min);
    ctx.strokeStyle='#dce3ec';ctx.lineWidth=1;ctx.fillStyle='#64748b';ctx.font='12px system-ui';
    for(let i=0;i<=4;i++){const val=max-(max-min)*i/4;const yy=y(val);ctx.beginPath();ctx.moveTo(p.l,yy);ctx.lineTo(w-p.r,yy);ctx.stroke();ctx.fillText(money(val).replace('.00',''),4,yy+4);}
    if(min<0&&max>0){ctx.strokeStyle='#ef4444';ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(p.l,y(0));ctx.lineTo(w-p.r,y(0));ctx.stroke();ctx.setLineDash([]);}
    ctx.beginPath();points.forEach((pt,i)=>{if(i===0)ctx.moveTo(x(i),y(pt.balance));else{ctx.lineTo(x(i),y(points[i-1].balance));ctx.lineTo(x(i),y(pt.balance));}});ctx.strokeStyle='#2563eb';ctx.lineWidth=3;ctx.stroke();
    points.forEach((pt,i)=>{ctx.beginPath();ctx.arc(x(i),y(pt.balance),3.5,0,Math.PI*2);ctx.fillStyle=pt.balance<0?'#c62828':'#2563eb';ctx.fill();});
    const labels=[0,Math.floor((points.length-1)/2),points.length-1];ctx.fillStyle='#64748b';ctx.textAlign='center';labels.forEach(i=>ctx.fillText(new Date(points[i].date+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric'}),x(i),h-14));ctx.textAlign='left';
  }
"""
chart_new = """  function drawCashChart(summary) {
    const canvas=document.getElementById('cashChart');
    const rect=canvas.getBoundingClientRect();
    const dpr=window.devicePixelRatio||1;
    canvas.width=Math.max(700,rect.width*dpr); canvas.height=330*dpr;
    const ctx=canvas.getContext('2d'); ctx.scale(dpr,dpr);
    const w=canvas.width/dpr,h=canvas.height/dpr,p={l:68,r:22,t:20,b:42};
    ctx.clearRect(0,0,w,h);
    const mode=state.savings?.chartMode||'principal';
    const investmentPoints=summary.investmentProjection.points;
    const points=investmentPoints.map(pt=>({date:pt.date,balance:mode==='growth'?pt.median:pt.principalTotal,low:mode==='growth'?pt.low:null,high:mode==='growth'?pt.high:null}));
    const vals=points.flatMap(pt=>mode==='growth'?[pt.low,pt.high]:[pt.balance]);
    let min=Math.min(...vals,0),max=Math.max(...vals,0);if(max===min){max+=1;min-=1;}const pad=(max-min)*.12;max+=pad;min-=pad;
    const x=i=>p.l+(w-p.l-p.r)*(points.length===1?0:i/(points.length-1));
    const y=v=>p.t+(h-p.t-p.b)*(max-v)/(max-min);
    ctx.strokeStyle='#dce3ec';ctx.lineWidth=1;ctx.fillStyle='#64748b';ctx.font='12px system-ui';
    for(let i=0;i<=4;i++){const val=max-(max-min)*i/4,yy=y(val);ctx.beginPath();ctx.moveTo(p.l,yy);ctx.lineTo(w-p.r,yy);ctx.stroke();ctx.fillText(money(val).replace('.00',''),4,yy+4);}
    if(min<0&&max>0){ctx.strokeStyle='#ef4444';ctx.setLineDash([5,5]);ctx.beginPath();ctx.moveTo(p.l,y(0));ctx.lineTo(w-p.r,y(0));ctx.stroke();ctx.setLineDash([]);}
    if(mode==='growth'&&points.length>1){
      ctx.beginPath();points.forEach((pt,i)=>{if(i===0)ctx.moveTo(x(i),y(pt.high));else ctx.lineTo(x(i),y(pt.high));});
      for(let i=points.length-1;i>=0;i--)ctx.lineTo(x(i),y(points[i].low));ctx.closePath();ctx.fillStyle='rgba(96,165,250,.22)';ctx.fill();
    }
    ctx.beginPath();points.forEach((pt,i)=>{if(i===0)ctx.moveTo(x(i),y(pt.balance));else{ctx.lineTo(x(i),y(points[i-1].balance));ctx.lineTo(x(i),y(pt.balance));}});ctx.strokeStyle='#2563eb';ctx.lineWidth=3;ctx.stroke();
    points.forEach((pt,i)=>{ctx.beginPath();ctx.arc(x(i),y(pt.balance),3.2,0,Math.PI*2);ctx.fillStyle=pt.balance<0?'#c62828':'#2563eb';ctx.fill();});
    const labels=[0,Math.floor((points.length-1)/2),points.length-1];ctx.fillStyle='#64748b';ctx.textAlign='center';[...new Set(labels)].forEach(i=>ctx.fillText(new Date(points[i].date+'T00:00:00').toLocaleDateString('en-US',{month:'short',day:'numeric',year:points.length>60?'2-digit':undefined}),x(i),h-14));ctx.textAlign='left';
  }
"""
html = replace_once(html, chart_old, chart_new, 'investment chart function')

# ---------- Income copy + savings rendering ----------
income_render_old = """  function renderIncome() {
    document.getElementById('incomeTable').innerHTML=state.incomes.map(i=>`<tr><td>${escapeHtml(i.name)}${!i.active?' <span class="muted">(off)</span>':''}</td><td>${scheduleLabel(i)}</td><td>${money2(i.gross,i.currency)}</td><td>${money2(estimateIncomeNet(i),i.currency)}</td><td>${i.netOverride!==null&&i.netOverride!==''?'Net override':escapeHtml(i.taxMode)}</td><td><button class="btn sm secondary" data-action="edit-income" data-id="${i.id}">Edit</button> <button class="btn sm danger" data-action="delete-income" data-id="${i.id}">Delete</button></td></tr>`).join('');
  }
"""
income_render_new = """  function renderIncome() {
    document.getElementById('incomeTable').innerHTML=state.incomes.map(i=>`<tr><td>${escapeHtml(i.name)}${!i.active?' <span class="muted">(off)</span>':''}</td><td>${scheduleLabel(i)}</td><td>${money2(i.gross,i.currency)}</td><td>${money2(estimateIncomeNet(i),i.currency)}</td><td>${i.netOverride!==null&&i.netOverride!==''?'Net override':escapeHtml(i.taxMode)}</td><td><button class="btn sm secondary" data-action="edit-income" data-id="${i.id}">Edit</button> <button class="btn sm good" data-action="copy-income" data-id="${i.id}">Copy to next year</button> <button class="btn sm danger" data-action="delete-income" data-id="${i.id}">Delete</button></td></tr>`).join('');
  }

  function renderSavings() {
    const cfg=Object.assign({},defaultState.savings,state.savings||{}),summary=getSummary(),plan=summary.savingsProjection,investment=summary.investmentProjection;
    savingsEnabled.checked=!!cfg.enabled;savingsMonthlyTarget.value=cfg.monthlyTarget;savingsStartingBalance.value=cfg.startingBalance;savingsTiming.value=cfg.timing;savingsCashFloor.value=cfg.cashFloor;savingsEssentialBuffer.value=cfg.essentialBufferPct;savingsDebtFirstApr.value=cfg.debtFirstApr;savingsMinimumWhileDebt.value=cfg.minimumWhileDebt;savingsReturnPreset.value=cfg.returnPreset;savingsExpectedReturn.value=cfg.expectedReturn;savingsVolatility.value=cfg.volatility;
    document.getElementById('savingsTargetMetric').textContent=money(cfg.monthlyTarget);
    document.getElementById('savingsContributionMetric').textContent=money(plan.totalContributed);
    document.getElementById('savingsContributionDetail').textContent=plan.totalTarget>0?`${Math.round(plan.totalContributed/plan.totalTarget*100)}% of ${money(plan.totalTarget)} cumulative target`:'Enable the plan and enter a monthly target.';
    document.getElementById('savingsInvestmentMetric').textContent=money(investment.endingMedianInvestment);
    document.getElementById('savingsInvestmentDetail').textContent=`Principal ${money(investment.endingPrincipalInvestment)} · modeled 25%–75% range ${money(investment.endingLowInvestment)}–${money(investment.endingHighInvestment)}`;
    document.getElementById('savingsShortfallMetric').textContent=money(plan.totalShortfall);
    const debtBlocked=plan.months.filter(m=>m.reasons.some(r=>r.includes('debt'))).length;
    const cashBlocked=plan.months.filter(m=>m.reasons.some(r=>r.includes('Cash reserved'))).length;
    document.getElementById('savingsPlanSummary').innerHTML=!cfg.enabled?'<strong>Savings plan is off.</strong> Enable it to schedule contributions immediately after income arrives.':plan.totalShortfall<=.01?`<strong>Target is feasible.</strong> The forecast contributes ${money(plan.totalContributed)} while preserving scheduled bills and the ${money(cfg.cashFloor)} spendable-cash floor.`:`<strong>The requested target is not fully affordable under current assumptions.</strong> ${money(plan.totalShortfall)} is deferred rather than forcing a cash shortfall.${debtBlocked?` Debt takes priority in ${debtBlocked} month${debtBlocked===1?'':'s'}.`:''}${cashBlocked?` Living costs or the cash floor constrain ${cashBlocked} month${cashBlocked===1?'':'s'}.`:''} Reduce flexible spending, lower the target, increase income, or clear expensive debt sooner.`;
    document.getElementById('savingsMonthlyTable').innerHTML=plan.months.length?plan.months.map(m=>{const cls=m.shortfall<=.01?'good':m.contributed>0?'warn':'bad';const response=m.reasons.length?m.reasons.join('; '):m.shortfall<=.01?'Target met without violating reserves':'No contribution opportunity';return `<tr><td>${monthLabel(m.key)}</td><td>${money2(m.target)}</td><td>${money2(m.contributed)}</td><td>${money2(m.shortfall)}</td><td>${money2(m.essential)}</td><td>${money2(m.flexible)}</td><td><span class="savings-status ${cls}">${m.status}</span><div class="muted small" style="margin-top:5px">${escapeHtml(response)}</div></td></tr>`}).join(''):'<tr><td colspan="7" class="muted">No forecast months available.</td></tr>';
  }
"""
html = replace_once(html, income_render_old, income_render_new, 'income copy and savings renderer')

# ---------- Resize and chart controls ----------
resize_old = """  window.addEventListener('resize',()=>{if(document.getElementById('dashboard').classList.contains('active'))drawCashChart(getSummary().events);});"""
resize_new = """  window.addEventListener('resize',()=>{if(document.getElementById('dashboard').classList.contains('active'))drawCashChart(getSummary());});
  document.getElementById('chartModeToggle').addEventListener('click',e=>{const btn=e.target.closest('[data-chart-mode]');if(!btn)return;state.savings={...defaultState.savings,...state.savings,chartMode:btn.dataset.chartMode};renderDashboard();saveState();});"""
html = replace_once(html, resize_old, resize_new, 'chart toggle listener')

# ---------- Savings form listeners ----------
income_clear_anchor = """  document.getElementById('clearIncome').addEventListener('click',clearIncomeForm);
  document.getElementById('billForm').addEventListener('submit',"""
savings_listeners = """  document.getElementById('clearIncome').addEventListener('click',clearIncomeForm);
  const applySavingsPreset=()=>{
    const preset=savingsReturnPreset.value;
    if(preset==='sp50010y'){savingsExpectedReturn.value=14.8;savingsVolatility.value=20.8;}
    else if(preset==='longTerm'){savingsExpectedReturn.value=9.8;savingsVolatility.value=20.8;}
    else if(preset==='conservative'){savingsExpectedReturn.value=7;savingsVolatility.value=15;}
  };
  document.getElementById('savingsReturnPreset').addEventListener('change',()=>{if(savingsReturnPreset.value!=='custom')applySavingsPreset();});
  ['savingsExpectedReturn','savingsVolatility'].forEach(id=>document.getElementById(id).addEventListener('input',()=>{if(document.activeElement===document.getElementById(id))savingsReturnPreset.value='custom';}));
  document.getElementById('savingsForm').addEventListener('submit',e=>{e.preventDefault();state.savings={...state.savings,enabled:savingsEnabled.checked,monthlyTarget:Math.max(0,Number(savingsMonthlyTarget.value)||0),startingBalance:Math.max(0,Number(savingsStartingBalance.value)||0),timing:savingsTiming.value,cashFloor:Math.max(0,Number(savingsCashFloor.value)||0),essentialBufferPct:Math.max(0,Number(savingsEssentialBuffer.value)||0),debtFirstApr:Math.max(0,Number(savingsDebtFirstApr.value)||0),minimumWhileDebt:Math.max(0,Number(savingsMinimumWhileDebt.value)||0),returnPreset:savingsReturnPreset.value,expectedReturn:Number(savingsExpectedReturn.value)||0,volatility:Math.max(0,Number(savingsVolatility.value)||0)};renderAll();});
  document.getElementById('savingsEnabled').addEventListener('change',()=>{state.savings={...defaultState.savings,...state.savings,enabled:savingsEnabled.checked};renderAll();});
  document.getElementById('rebuildIntegratedPlan').addEventListener('click',()=>{document.getElementById('generateAvalanche').click();setTimeout(()=>{document.querySelector('[data-tab="savings"]').click();renderSavings();},0);});
  document.getElementById('billForm').addEventListener('submit',"""
html = replace_once(html, income_clear_anchor, savings_listeners, 'savings form listeners')

# ---------- Copy income action ----------
copy_action_anchor = """    if(action==='edit-income'){const i=state.incomes.find(x=>x.id===id);if(!i)return;incomeId.value=i.id;incomeName.value=i.name;incomeStart.value=i.startDate;incomeEnd.value=i.endDate||'';incomeRecurrence.value=i.recurrence;incomeGross.value=i.gross;incomeCurrency.value=i.currency;incomeTaxMode.value=i.taxMode;incomePretax.value=i.pretax||0;incomeNetOverride.value=i.netOverride??'';incomeActive.checked=i.active;document.querySelector('[data-tab="income"]').click();window.scrollTo({top:0,behavior:'smooth'});}
    if(action==='delete-income'&&confirm('Delete this income schedule?'))"""
copy_action_new = """    if(action==='edit-income'){const i=state.incomes.find(x=>x.id===id);if(!i)return;incomeId.value=i.id;incomeName.value=i.name;incomeStart.value=i.startDate;incomeEnd.value=i.endDate||'';incomeRecurrence.value=i.recurrence;incomeGross.value=i.gross;incomeCurrency.value=i.currency;incomeTaxMode.value=i.taxMode;incomePretax.value=i.pretax||0;incomeNetOverride.value=i.netOverride??'';incomeActive.checked=i.active;document.querySelector('[data-tab="income"]').click();window.scrollTo({top:0,behavior:'smooth'});}
    if(action==='copy-income'){const i=state.incomes.find(x=>x.id===id);if(!i)return;clearIncomeForm();const shiftedStart=shiftIncomeDateOneYear(i.startDate,i.recurrence),shiftedEnd=shiftIncomeDateOneYear(i.endDate||'',i.recurrence),year=shiftedStart?parseDate(shiftedStart).getFullYear():parseDate(i.startDate).getFullYear()+1;incomeName.value=/\\b20\\d{2}\\b/.test(i.name)?i.name.replace(/\\b20\\d{2}\\b/g,String(year)):`${i.name} ${year}`;incomeStart.value=shiftedStart;incomeEnd.value=shiftedEnd;incomeRecurrence.value=i.recurrence;incomeGross.value=i.gross;incomeCurrency.value=i.currency;incomeTaxMode.value=i.taxMode;incomePretax.value=i.pretax||0;incomeNetOverride.value='';incomeActive.checked=true;document.querySelector('[data-tab="income"]').click();window.scrollTo({top:0,behavior:'smooth'});}
    if(action==='delete-income'&&confirm('Delete this income schedule?'))"""
html = replace_once(html, copy_action_anchor, copy_action_new, 'copy income action')

# ---------- Debt planner must run before savings ----------
html = replace_once(html, "const baseEvents=buildEvents(state.settings.targetDate,true);", "const baseEvents=buildEvents(state.settings.targetDate,true,null,false);", 'debt planner excludes savings')

# ---------- CSV ----------
csv_old = """  document.getElementById('downloadCsv').addEventListener('click',()=>{const rows=[['Date','Item','Type','Amount USD','Running cash USD','Debt remaining USD','Deadline markup accrued USD'],...getSummary().events.map(e=>[e.date,e.name,e.type,e.amountUSD.toFixed(2),e.runningBalance.toFixed(2),e.debtRemainingUSD===undefined?'':e.debtRemainingUSD.toFixed(2),e.debtMarkupAccruedUSD===undefined?'':e.debtMarkupAccruedUSD.toFixed(2)])];downloadBlob(rows.map(r=>r.map(csvCell).join(',')).join('\\n'),'financial_forecast_ledger.csv','text/csv');});"""
csv_new = """  document.getElementById('downloadCsv').addEventListener('click',()=>{const rows=[['Date','Item','Type','Amount USD','Running cash USD','Investment principal USD','Debt remaining USD','Deadline markup accrued USD'],...getSummary().events.map(e=>[e.date,e.name,e.type,e.amountUSD.toFixed(2),e.runningBalance.toFixed(2),e.investmentPrincipalUSD===undefined?'':e.investmentPrincipalUSD.toFixed(2),e.debtRemainingUSD===undefined?'':e.debtRemainingUSD.toFixed(2),e.debtMarkupAccruedUSD===undefined?'':e.debtMarkupAccruedUSD.toFixed(2)])];downloadBlob(rows.map(r=>r.map(csvCell).join(',')).join('\\n'),'financial_forecast_ledger.csv','text/csv');});"""
html = replace_once(html, csv_old, csv_new, 'savings CSV export')

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
sw = sw.replace("const CACHE = 'financial-planner-secure-v7-smart-priority';", "const CACHE = 'financial-planner-secure-v8-savings-investments';")
SW.write_text(sw, encoding='utf-8')
print('Applied v8 savings, investment growth, and income-copy features.')
