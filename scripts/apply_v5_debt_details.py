from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')

if 'financial-planner-secure-v5-debt-details' in SW.read_text(encoding='utf-8') and 'id="currentDebtTotals"' in html:
    print('v5 debt details are already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

css_anchor = """    .danger-text { color: var(--bad); }

    @media (max-width: 1100px) {"""
css_new = """    .danger-text { color: var(--bad); }
    .card-button {
      appearance: none;
      width: 100%;
      text-align: left;
      color: inherit;
      font: inherit;
      cursor: pointer;
      transition: transform .2s ease, box-shadow .2s ease, border-color .2s ease;
    }
    .card-button:hover { transform: translateY(-2px); border-color: #93c5fd; box-shadow: 0 16px 34px rgba(37,99,235,.13); }
    .card-button:focus-visible { outline: 3px solid rgba(37,99,235,.28); outline-offset: 3px; }
    .debt-card-detail { display:flex; align-items:center; justify-content:space-between; gap:10px; }
    .debt-card-chevron { font-size:1.15rem; color:var(--accent); transition:transform .28s ease; }
    .card-button[aria-expanded="true"] .debt-card-chevron { transform:rotate(180deg); }
    .debt-breakdown {
      grid-column: 1 / -1;
      max-height: 0;
      opacity: 0;
      overflow: hidden;
      transform: translateY(-10px);
      transition: max-height .42s cubic-bezier(.2,.8,.2,1), opacity .26s ease, transform .32s ease, margin .32s ease;
      margin-top: -16px;
    }
    .debt-breakdown.open { max-height: 900px; opacity: 1; transform: translateY(0); margin-top: 0; }
    .debt-breakdown-inner { border:1px solid #bfdbfe; background:linear-gradient(180deg,#f8fbff,#fff); border-radius:16px; padding:18px; box-shadow:0 10px 24px rgba(37,99,235,.08); }
    .debt-breakdown-head { display:flex; align-items:flex-start; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:12px; }
    .debt-breakdown-head h3 { margin:0 0 4px; }
    .debt-breakdown-total { font-size:1.15rem; font-weight:800; color:var(--warn); }
    .debt-breakdown-list { display:grid; gap:10px; }
    .debt-breakdown-row { display:grid; grid-template-columns:minmax(180px,1.4fr) repeat(3,minmax(140px,1fr)); gap:12px; align-items:center; padding:13px 14px; border:1px solid var(--line); border-radius:12px; background:#fff; }
    .debt-breakdown-name { font-weight:800; }
    .debt-breakdown-meta { color:var(--muted); font-size:.8rem; margin-top:3px; }
    .debt-stat-label { color:var(--muted); font-size:.75rem; font-weight:700; text-transform:uppercase; letter-spacing:.035em; }
    .debt-stat-value { font-weight:800; margin-top:3px; }
    .ledger-detail-toggle { border:0; border-radius:999px; padding:5px 9px; margin-left:7px; background:#e0edff; color:#1d4ed8; font-size:.74rem; font-weight:800; white-space:nowrap; }
    .ledger-detail-toggle:hover { background:#cfe2ff; }
    .debt-detail-header, .debt-detail-cell {
      width:0;
      max-width:0;
      opacity:0;
      padding-left:0;
      padding-right:0;
      overflow:hidden;
      white-space:nowrap;
      transition: width .32s ease, max-width .32s ease, opacity .22s ease, padding .32s ease;
    }
    #forecastLedger.detail-column-open .debt-detail-header,
    #forecastLedger.detail-column-open .debt-detail-cell { width:280px; max-width:280px; opacity:1; padding-left:12px; padding-right:12px; }
    .debt-detail-inner { min-width:250px; opacity:0; transform:translateX(18px); transition:opacity .24s ease .08s, transform .3s ease; }
    tr.detail-open .debt-detail-inner { opacity:1; transform:translateX(0); }
    .debt-detail-title { font-weight:800; color:#1e3a8a; }
    .debt-detail-line { display:flex; justify-content:space-between; gap:12px; margin-top:4px; font-size:.8rem; }
    .debt-detail-line span:first-child { color:var(--muted); }
    .paid-off-badge { display:inline-flex; margin-top:6px; padding:3px 7px; border-radius:999px; background:#dcfce7; color:#166534; font-size:.72rem; font-weight:800; }
    .current-debt-total { display:flex; align-items:center; justify-content:space-between; gap:16px; flex-wrap:wrap; margin-bottom:16px; padding:15px 16px; border:1px solid #fed7aa; border-radius:14px; background:linear-gradient(135deg,#fff7ed,#fff); }
    .current-debt-total-label { color:#9a3412; font-size:.78rem; font-weight:800; text-transform:uppercase; letter-spacing:.045em; }
    .current-debt-total-values { display:flex; align-items:baseline; gap:12px; flex-wrap:wrap; }
    .current-debt-total-primary { color:var(--warn); font-size:1.55rem; font-weight:850; }
    .current-debt-total-secondary { color:#475569; font-size:1rem; font-weight:750; }
    .current-debt-total-note { margin-top:4px; color:var(--muted); font-size:.78rem; }

    @media (max-width: 1100px) {
      .debt-breakdown-row { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
html = replace_once(html, css_anchor, css_new, 'CSS insertion')

mobile_anchor = """      .card { min-height: auto; }
    }
  </style>"""
mobile_new = """      .card { min-height: auto; }
      .debt-breakdown-row { grid-template-columns:1fr; }
      #forecastLedger.detail-column-open .debt-detail-header,
      #forecastLedger.detail-column-open .debt-detail-cell { width:230px; max-width:230px; }
      .debt-detail-inner { min-width:205px; }
    }
  </style>"""
html = replace_once(html, mobile_anchor, mobile_new, 'mobile CSS')

old_debt_card = """        <div class="card">
          <div class="label">Debt at target</div>
          <div class="value warning" id="debtTarget">$0</div>
          <div class="detail" id="debtInterestDetail"></div>
        </div>
        <div class="card">
          <div class="label">Cash less debt</div>
          <div class="value" id="netPosition">$0</div>
          <div class="detail">Cash minus projected debt balances</div>
        </div>
      </div>"""
new_debt_card = """        <button class="card card-button" id="debtSummaryToggle" type="button" aria-expanded="false" aria-controls="debtBreakdown">
          <div class="label">Debt at target</div>
          <div class="value warning" id="debtTarget">$0</div>
          <div class="detail debt-card-detail"><span id="debtInterestDetail"></span><span class="debt-card-chevron" aria-hidden="true">⌄</span></div>
        </button>
        <div class="card">
          <div class="label">Cash less debt</div>
          <div class="value" id="netPosition">$0</div>
          <div class="detail">Cash minus projected debt balances</div>
        </div>
        <div id="debtBreakdown" class="debt-breakdown" aria-hidden="true">
          <div class="debt-breakdown-inner">
            <div class="debt-breakdown-head">
              <div><h3>Debt remaining on target date</h3><div class="muted small" id="debtBreakdownSubtitle"></div></div>
              <div class="debt-breakdown-total" id="debtBreakdownTotal">$0</div>
            </div>
            <div id="debtBreakdownBody" class="debt-breakdown-list"></div>
          </div>
        </div>
      </div>"""
html = replace_once(html, old_debt_card, new_debt_card, 'debt target card')

old_ledger = """          <table>
            <thead><tr><th>Date</th><th>Item</th><th>Type</th><th>Amount</th><th>Running cash</th></tr></thead>
            <tbody id="ledgerBody"></tbody>
          </table>"""
new_ledger = """          <table id="forecastLedger">
            <thead><tr><th>Date</th><th>Item</th><th>Type</th><th>Amount</th><th>Running cash</th><th class="debt-detail-header">Debt after payment</th></tr></thead>
            <tbody id="ledgerBody"></tbody>
          </table>"""
html = replace_once(html, old_ledger, new_ledger, 'ledger table')

projected_anchor = """      <div class="panel">
        <h2>Projected debt balances</h2>
        <div id="debtCards" class="grid three"></div>"""
projected_new = """      <div class="panel">
        <h2>Projected debt balances</h2>
        <div id="currentDebtTotals" class="current-debt-total"></div>
        <div id="debtCards" class="grid three"></div>"""
html = replace_once(html, projected_anchor, projected_new, 'current debt total container')

state_anchor = """  let cloudBusy = false;
  let reconcilingCloud = false;
"""
state_new = """  let cloudBusy = false;
  let reconcilingCloud = false;
  let debtBreakdownOpen = false;
"""
html = replace_once(html, state_anchor, state_new, 'dashboard state')

old_engine = """  function buildEvents(targetDate=state.settings.targetDate, includeDebtPayments=true) {
    const events=[];
    state.incomes.filter(x=>x.active).forEach(item=>{
      const netUSD=toUSD(estimateIncomeNet(item),item.currency);
      const grossUSD=toUSD(Number(item.gross)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:'Income',amountUSD:netUSD,grossUSD,source:'income',sourceId:item.id}));
    });
    state.bills.filter(x=>x.active && (includeDebtPayments || !x.debtId)).forEach(item=>{
      const amountUSD=toUSD(Number(item.amount)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:item.debtId?'Debt payment':item.category,amountUSD:-amountUSD,source:'bill',sourceId:item.id,debtId:item.debtId||''}));
    });
    events.push(...buildVehicleEvents(targetDate));
    events.sort((a,b)=> a.date.localeCompare(b.date) || (b.amountUSD-a.amountUSD));
    let balance=Number(state.settings.startingCash)||0;
    events.forEach(e=>{ balance+=e.amountUSD; e.runningBalance=balance; });
    return events;
  }

  function projectDebt(debt, targetDate=state.settings.targetDate) {
    let balanceUSD=toUSD(Number(debt.balance)||0,debt.currency);
    let currentDate=state.settings.forecastStart;
    let interest=0, payments=0;
    const paymentEvents=buildEvents(targetDate,true).filter(e=>e.debtId===debt.id).sort((a,b)=>a.date.localeCompare(b.date));
    for (const p of paymentEvents) {
      const days=daysBetween(currentDate,p.date);
      const accrued=balanceUSD*(Number(debt.apr)/100)*days/365;
      balanceUSD+=accrued; interest+=accrued;
      const paid=Math.min(balanceUSD,Math.abs(p.amountUSD));
      balanceUSD-=paid; payments+=paid;
      currentDate=p.date;
    }
    const finalDays=daysBetween(currentDate,targetDate);
    const finalInterest=balanceUSD*(Number(debt.apr)/100)*finalDays/365;
    balanceUSD+=finalInterest; interest+=finalInterest;
    return {balanceUSD,interestUSD:interest,paymentsUSD:payments};
  }

  function getSummary() {
    const events=buildEvents();
    const income=events.filter(e=>e.amountUSD>0).reduce((s,e)=>s+e.amountUSD,0);
    const gross=events.filter(e=>e.source==='income').reduce((s,e)=>s+(e.grossUSD||0),0);
    const outflows=-events.filter(e=>e.amountUSD<0).reduce((s,e)=>s+e.amountUSD,0);
    const cash=(Number(state.settings.startingCash)||0)+income-outflows;
    const debtProjections=state.debts.map(d=>({debt:d,...projectDebt(d)}));"""
new_engine = """  function buildDebtPaymentEvents(targetDate=state.settings.targetDate) {
    const events=[];
    state.bills.filter(x=>x.active && x.debtId).forEach(item=>{
      const amountUSD=toUSD(Number(item.amount)||0,item.currency);
      generateDates(item,targetDate).forEach(date=>events.push({date,name:item.name,type:'Debt payment',amountUSD:-amountUSD,source:'bill',sourceId:item.id,debtId:item.debtId,autoGenerated:!!item.autoGenerated}));
    });
    state.debts.forEach(debt=>{
      const minimum=Number(debt.minimum)||0;
      if(minimum<=0) return;
      const minimumSchedule={active:true,startDate:debt.deferredUntil||state.settings.forecastStart,endDate:'',recurrence:'monthly'};
      generateDates(minimumSchedule,targetDate).forEach(date=>events.push({date,name:`Minimum payment: ${debt.name}`,type:'Debt payment',amountUSD:-toUSD(minimum,debt.currency),source:'debt-minimum',sourceId:`minimum_${debt.id}`,debtId:debt.id,autoMinimum:true}));
    });
    return events.sort((a,b)=>a.date.localeCompare(b.date)||String(a.sourceId).localeCompare(String(b.sourceId)));
  }

  function simulateDebtPayments(targetDate=state.settings.targetDate) {
    const ledger={};
    state.debts.forEach(debt=>ledger[debt.id]={debt,balanceUSD:toUSD(Number(debt.balance)||0,debt.currency),interestUSD:0,paymentsUSD:0,currentDate:state.settings.forecastStart,payoffDate:null});
    const events=buildDebtPaymentEvents(targetDate);
    const actualEvents=[];
    for(const event of events){
      const entry=ledger[event.debtId];
      if(!entry) continue;
      const days=daysBetween(entry.currentDate,event.date);
      const accrued=entry.balanceUSD*(Number(entry.debt.apr)/100)*days/365;
      entry.balanceUSD+=accrued;
      entry.interestUSD+=accrued;
      entry.currentDate=event.date;
      const requestedUSD=Math.abs(event.amountUSD);
      const paidUSD=Math.min(entry.balanceUSD,requestedUSD);
      if(paidUSD<=.005) continue;
      entry.balanceUSD=Math.max(0,entry.balanceUSD-paidUSD);
      entry.paymentsUSD+=paidUSD;
      if(entry.balanceUSD<=.005 && !entry.payoffDate) entry.payoffDate=event.date;
      actualEvents.push({...event,amountUSD:-paidUSD,requestedAmountUSD:requestedUSD,debtName:entry.debt.name,debtCurrency:entry.debt.currency,debtRemainingUSD:entry.balanceUSD,debtInterestAccruedUSD:entry.interestUSD,debtPaidOff:entry.balanceUSD<=.005});
    }
    Object.values(ledger).forEach(entry=>{
      const finalDays=daysBetween(entry.currentDate,targetDate);
      const finalInterest=entry.balanceUSD*(Number(entry.debt.apr)/100)*finalDays/365;
      entry.balanceUSD+=finalInterest;
      entry.interestUSD+=finalInterest;
      entry.currentDate=targetDate;
    });
    const projections={};
    Object.values(ledger).forEach(entry=>projections[entry.debt.id]={balanceUSD:entry.balanceUSD,interestUSD:entry.interestUSD,paymentsUSD:entry.paymentsUSD,payoffDate:entry.payoffDate});
    return {events:actualEvents,projections};
  }

  function buildEvents(targetDate=state.settings.targetDate, includeDebtPayments=true, suppliedDebtSimulation=null) {
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

  function projectDebt(debt, targetDate=state.settings.targetDate) {
    return simulateDebtPayments(targetDate).projections[debt.id]||{balanceUSD:0,interestUSD:0,paymentsUSD:0,payoffDate:null};
  }

  function getSummary() {
    const debtSimulation=simulateDebtPayments(state.settings.targetDate);
    const events=buildEvents(state.settings.targetDate,true,debtSimulation);
    const income=events.filter(e=>e.amountUSD>0).reduce((s,e)=>s+e.amountUSD,0);
    const gross=events.filter(e=>e.source==='income').reduce((s,e)=>s+(e.grossUSD||0),0);
    const outflows=-events.filter(e=>e.amountUSD<0).reduce((s,e)=>s+e.amountUSD,0);
    const cash=(Number(state.settings.startingCash)||0)+income-outflows;
    const payoffHorizon=toISO(addMonths(parseDate(state.settings.targetDate),360));
    const longSimulation=simulateDebtPayments(payoffHorizon);
    const debtProjections=state.debts.map(d=>{
      const targetProjection=debtSimulation.projections[d.id]||{balanceUSD:0,interestUSD:0,paymentsUSD:0,payoffDate:null};
      const longProjection=longSimulation.projections[d.id]||{};
      return {debt:d,...targetProjection,projectedPayoffDate:targetProjection.payoffDate||longProjection.payoffDate||null};
    });"""
html = replace_once(html, old_engine, new_engine, 'debt engine')

summary_anchor = """    document.getElementById('debtTarget').textContent=money(s.totalDebt);
    document.getElementById('debtInterestDetail').textContent=`About ${money(s.interest)} interest accrued in forecast`;
    const np=s.cash-s.totalDebt;"""
summary_new = """    document.getElementById('debtTarget').textContent=money(s.totalDebt);
    document.getElementById('debtInterestDetail').textContent=`About ${money(s.interest)} interest accrued in forecast`;
    const breakdown=document.getElementById('debtBreakdown');
    breakdown.classList.toggle('open',debtBreakdownOpen);
    breakdown.setAttribute('aria-hidden',String(!debtBreakdownOpen));
    document.getElementById('debtSummaryToggle').setAttribute('aria-expanded',String(debtBreakdownOpen));
    const np=s.cash-s.totalDebt;"""
html = replace_once(html, summary_anchor, summary_new, 'breakdown state rendering')

old_ledger_render = """    document.getElementById('ledgerBody').innerHTML=s.events.length?s.events.map(e=>`<tr><td>${fmtDate(e.date)}</td><td>${escapeHtml(e.name)}</td><td><span class="pill">${escapeHtml(e.type)}</span></td><td class="amount ${e.amountUSD>=0?'in':'out'}">${e.amountUSD>=0?'+':''}${money2(e.amountUSD)}</td><td>${money2(e.runningBalance)}</td></tr>`).join(''):`<tr><td colspan="5" class="muted">No transactions in this period.</td></tr>`;
    drawCashChart(s.events);"""
new_ledger_render = """    const remaining=s.debtProjections.filter(x=>x.balanceUSD>.005).sort((a,b)=>b.balanceUSD-a.balanceUSD);
    document.getElementById('debtBreakdownTotal').textContent=money(s.totalDebt);
    document.getElementById('debtBreakdownSubtitle').textContent=remaining.length?`${remaining.length} debt${remaining.length===1?'':'s'} remain on ${fmtDate(state.settings.targetDate)}.`:`All tracked debts are projected to be paid by ${fmtDate(state.settings.targetDate)}.`;
    document.getElementById('debtBreakdownBody').innerHTML=remaining.length?remaining.map(x=>{
      const originalBalance=fromUSD(x.balanceUSD,x.debt.currency);
      const originalInterest=fromUSD(x.interestUSD,x.debt.currency);
      const payoff=x.projectedPayoffDate?fmtDate(x.projectedPayoffDate):'No payoff date under current schedule';
      return `<div class="debt-breakdown-row"><div><div class="debt-breakdown-name">${escapeHtml(x.debt.name)}</div><div class="debt-breakdown-meta">${Number(x.debt.apr).toFixed(2).replace(/\\.00$/,'')}% APR · ${x.debt.currency}</div></div><div><div class="debt-stat-label">Balance at target</div><div class="debt-stat-value">${money2(originalBalance,x.debt.currency)}</div>${x.debt.currency==='CAD'?`<div class="debt-breakdown-meta">${money2(x.balanceUSD)} USD equivalent</div>`:''}</div><div><div class="debt-stat-label">Interest accrued</div><div class="debt-stat-value">${money2(originalInterest,x.debt.currency)}</div></div><div><div class="debt-stat-label">Projected payoff</div><div class="debt-stat-value">${payoff}</div></div></div>`;
    }).join(''):`<div class="notice" style="margin:0"><strong>No debt remaining.</strong> The current payment schedule clears every tracked balance by the target date.</div>`;

    document.getElementById('forecastLedger').classList.remove('detail-column-open');
    document.getElementById('ledgerBody').innerHTML=s.events.length?s.events.map((e,index)=>{const isDebt=e.type==='Debt payment'&&e.debtId;const debt=state.debts.find(d=>d.id===e.debtId);const remainingOriginal=isDebt&&debt?fromUSD(e.debtRemainingUSD||0,debt.currency):0;const interestOriginal=isDebt&&debt?fromUSD(e.debtInterestAccruedUSD||0,debt.currency):0;return `<tr data-ledger-row="${index}"><td>${fmtDate(e.date)}</td><td>${escapeHtml(e.name)}</td><td><span class="pill">${escapeHtml(e.type)}</span>${isDebt?`<button class="ledger-detail-toggle" type="button" data-ledger-toggle="${index}" aria-expanded="false">Show balance →</button>`:''}</td><td class="amount ${e.amountUSD>=0?'in':'out'}">${e.amountUSD>=0?'+':''}${money2(e.amountUSD)}</td><td>${money2(e.runningBalance)}</td><td class="debt-detail-cell"><div class="debt-detail-inner">${isDebt&&debt?`<div class="debt-detail-title">${escapeHtml(debt.name)}</div><div class="debt-detail-line"><span>Remaining</span><strong>${money2(remainingOriginal,debt.currency)}</strong></div><div class="debt-detail-line"><span>Interest accrued</span><strong>${money2(interestOriginal,debt.currency)}</strong></div>${e.debtPaidOff?'<span class="paid-off-badge">Paid off with this payment</span>':''}`:''}</div></td></tr>`}).join(''):`<tr><td colspan="6" class="muted">No transactions in this period.</td></tr>`;
    drawCashChart(s.events);"""
html = replace_once(html, old_ledger_render, new_ledger_render, 'ledger detail rendering')

render_debts_anchor = """  function renderDebts() {
    const projections=state.debts.map(d=>({d,p:projectDebt(d)}));
    document.getElementById('debtCards').innerHTML="""
render_debts_new = """  function renderDebts() {
    const projections=state.debts.map(d=>({d,p:projectDebt(d)}));
    const currentUSD=state.debts.reduce((sum,d)=>sum+toUSD(Number(d.balance)||0,d.currency),0);
    const currentCAD=fromUSD(currentUSD,'CAD');
    document.getElementById('currentDebtTotals').innerHTML=`<div><div class="current-debt-total-label">Total current debt</div><div class="current-debt-total-note">Sum of the balances entered below, before forecast interest and future payments.</div></div><div class="current-debt-total-values"><span class="current-debt-total-primary">${money2(currentUSD,'USD')}</span><span class="current-debt-total-secondary">${money2(currentCAD,'CAD')}</span></div>`;
    document.getElementById('debtCards').innerHTML="""
html = replace_once(html, render_debts_anchor, render_debts_new, 'current debt totals rendering')

listener_anchor = """  document.getElementById('headerTarget').addEventListener('change',e=>{state.settings.targetDate=e.target.value;renderAll();});
  window.addEventListener('resize',()=>{if(document.getElementById('dashboard').classList.contains('active'))drawCashChart(getSummary().events);});

  document.getElementById('incomeForm').addEventListener('submit',"""
listener_new = """  document.getElementById('headerTarget').addEventListener('change',e=>{state.settings.targetDate=e.target.value;renderAll();});
  window.addEventListener('resize',()=>{if(document.getElementById('dashboard').classList.contains('active'))drawCashChart(getSummary().events);});

  document.getElementById('debtSummaryToggle').addEventListener('click',()=>{
    debtBreakdownOpen=!debtBreakdownOpen;
    const panel=document.getElementById('debtBreakdown');
    panel.classList.toggle('open',debtBreakdownOpen);
    panel.setAttribute('aria-hidden',String(!debtBreakdownOpen));
    document.getElementById('debtSummaryToggle').setAttribute('aria-expanded',String(debtBreakdownOpen));
  });
  document.getElementById('ledgerBody').addEventListener('click',e=>{
    const btn=e.target.closest('[data-ledger-toggle]');if(!btn)return;
    const row=btn.closest('tr');row.classList.toggle('detail-open');
    const open=row.classList.contains('detail-open');
    btn.setAttribute('aria-expanded',String(open));btn.textContent=open?'Hide balance ←':'Show balance →';
    document.getElementById('forecastLedger').classList.toggle('detail-column-open',!!document.querySelector('#ledgerBody tr.detail-open'));
  });

  document.getElementById('incomeForm').addEventListener('submit',"""
html = replace_once(html, listener_anchor, listener_new, 'dashboard listeners')

old_csv = """  document.getElementById('downloadCsv').addEventListener('click',()=>{const rows=[['Date','Item','Type','Amount USD','Running cash USD'],...getSummary().events.map(e=>[e.date,e.name,e.type,e.amountUSD.toFixed(2),e.runningBalance.toFixed(2)])];downloadBlob(rows.map(r=>r.map(csvCell).join(',')).join('\\n'),'financial_forecast_ledger.csv','text/csv');});"""
new_csv = """  document.getElementById('downloadCsv').addEventListener('click',()=>{const rows=[['Date','Item','Type','Amount USD','Running cash USD','Debt remaining USD'],...getSummary().events.map(e=>[e.date,e.name,e.type,e.amountUSD.toFixed(2),e.runningBalance.toFixed(2),e.debtRemainingUSD===undefined?'':e.debtRemainingUSD.toFixed(2)])];downloadBlob(rows.map(r=>r.map(csvCell).join(',')).join('\\n'),'financial_forecast_ledger.csv','text/csv');});"""
html = replace_once(html, old_csv, new_csv, 'CSV export')

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
sw = sw.replace("const CACHE = 'financial-planner-secure-v4-balanced';", "const CACHE = 'financial-planner-secure-v5-debt-details';")
SW.write_text(sw, encoding='utf-8')
print('Applied v5 debt details, minimum payment cash flow, and current debt totals.')
