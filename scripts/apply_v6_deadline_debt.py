from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')

if 'id="debtType"' in html and 'financial-planner-secure-v6-deadline-debt' in SW.read_text(encoding='utf-8'):
    print('v6 deadline debt feature is already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

css_anchor = """    .current-debt-total-note { margin-top:4px; color:var(--muted); font-size:.78rem; }

    @media (max-width: 1100px) {"""
css_new = """    .current-debt-total-note { margin-top:4px; color:var(--muted); font-size:.78rem; }
    .debt-deadline-panel { grid-column:1 / -1; border:1px solid #fcd34d; border-radius:14px; padding:14px; background:linear-gradient(135deg,#fffbeb,#fff); }
    .debt-deadline-panel-title { color:#92400e; font-weight:850; margin-bottom:4px; }
    .debt-deadline-grid { display:grid; grid-template-columns:repeat(4,minmax(0,1fr)); gap:12px; margin-top:12px; }
    .debt-term-badge { display:inline-flex; align-items:center; padding:3px 7px; border-radius:999px; background:#fef3c7; color:#92400e; font-size:.72rem; font-weight:800; margin-top:5px; }
    .deadline-warning { color:#b45309; font-weight:750; }

    @media (max-width: 1100px) {
      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
html = replace_once(html, css_anchor, css_new, 'deadline CSS')

mobile_anchor = """      .debt-detail-inner { min-width:205px; }
    }
  </style>"""
mobile_new = """      .debt-detail-inner { min-width:205px; }
      .debt-deadline-grid { grid-template-columns:1fr; }
    }
  </style>"""
html = replace_once(html, mobile_anchor, mobile_new, 'deadline mobile CSS')

form_old = """          <div class="form-grid">
            <div><label>Name</label><input id="debtName" required /></div>
            <div><label>Opening balance</label><input id="debtBalance" type="number" step="0.01" min="0" required /></div>
            <div><label>Currency</label><select id="debtCurrency"><option>USD</option><option>CAD</option></select></div>
            <div><label>APR %</label><input id="debtApr" type="number" step="0.01" min="0" required /></div>
            <div><label>Minimum monthly payment</label><input id="debtMinimum" type="number" step="0.01" min="0" value="0" /></div>
            <div><label>Deferred until</label><input id="debtDeferredUntil" type="date" /></div>
            <div><label>Revolving/high-interest</label><div class="check-row"><input id="debtRevolving" type="checkbox" checked /> Mark as revolving/high-interest for optional planner filtering</div></div>
          </div>"""
form_new = """          <div class="form-grid">
            <div><label>Name</label><input id="debtName" required /></div>
            <div><label>Opening balance</label><input id="debtBalance" type="number" step="0.01" min="0" required /></div>
            <div><label>Currency</label><select id="debtCurrency"><option>USD</option><option>CAD</option></select></div>
            <div><label>Debt type</label><select id="debtType"><option value="standard">Standard APR debt</option><option value="deadline">Deadline debt with missed-payment markup</option></select></div>
            <div><label>APR before deadline %</label><input id="debtApr" type="number" step="0.01" min="0" required /></div>
            <div><label>Minimum monthly payment</label><input id="debtMinimum" type="number" step="0.01" min="0" value="0" /></div>
            <div><label>Deferred until</label><input id="debtDeferredUntil" type="date" /></div>
            <div><label>Revolving/high-interest</label><div class="check-row"><input id="debtRevolving" type="checkbox" checked /> Mark as revolving/high-interest for optional planner filtering</div></div>
            <div id="debtDeadlineFields" class="debt-deadline-panel hidden">
              <div class="debt-deadline-panel-title">Deadline and missed-payment terms</div>
              <div class="muted small">If any balance remains after the deadline date, the planner applies the markup once to that remaining balance. Optional ongoing growth is treated as an annual APR after the deadline.</div>
              <div class="debt-deadline-grid">
                <div><label>Must be paid by</label><input id="debtDeadlineDate" type="date" /></div>
                <div><label>One-time markup if missed %</label><input id="debtDeadlineMarkup" type="number" step="0.01" min="0" value="0" /></div>
                <div><label>Continue accumulating after deadline</label><div class="check-row"><input id="debtContinueAfterDeadline" type="checkbox" /> Apply ongoing annual interest after markup</div></div>
                <div id="debtPostModeWrap" class="hidden"><label>Post-deadline rate</label><select id="debtPostDeadlineMode"><option value="same">Same percentage as markup</option><option value="custom">Different annual APR</option></select></div>
                <div id="debtPostAprWrap" class="hidden"><label>Different post-deadline APR %</label><input id="debtPostDeadlineApr" type="number" step="0.01" min="0" value="0" /></div>
              </div>
            </div>
          </div>"""
html = replace_once(html, form_old, form_new, 'deadline debt form')

header_old = """<div class="table-wrap" style="margin-top:16px"><table><thead><tr><th>Debt</th><th>Opening</th><th>APR</th><th>Payments by target</th><th>Interest accrued</th><th>Projected balance</th><th>Actions</th></tr></thead><tbody id="debtTable"></tbody></table></div>"""
header_new = """<div class="table-wrap" style="margin-top:16px"><table><thead><tr><th>Debt</th><th>Opening</th><th>Terms</th><th>Payments by target</th><th>Interest accrued</th><th>Deadline markup</th><th>Projected balance</th><th>Actions</th></tr></thead><tbody id="debtTable"></tbody></table></div>"""
html = replace_once(html, header_old, header_new, 'debt table header')

engine_anchor = """  function buildDebtPaymentEvents(targetDate=state.settings.targetDate) {"""
engine_helpers = """  function debtTypeOf(debt) { return debt?.debtType === 'deadline' ? 'deadline' : 'standard'; }
  function postDeadlineApr(debt) {
    if (debtTypeOf(debt)!=='deadline' || !debt.continueAfterDeadline) return 0;
    return debt.postDeadlineMode==='custom' ? Math.max(0,Number(debt.postDeadlineApr)||0) : Math.max(0,Number(debt.deadlineMarkupPct)||0);
  }
  function debtPlannerRate(debt,date) {
    if (debtTypeOf(debt)!=='deadline' || !debt.deadlineDate) return Math.max(0,Number(debt.apr)||0);
    if (date<=debt.deadlineDate) return Math.max(Number(debt.apr)||0,Number(debt.deadlineMarkupPct)||0);
    return postDeadlineApr(debt);
  }
  function debtTermsText(debt) {
    if (debtTypeOf(debt)!=='deadline') return `${Number(debt.apr)||0}% APR`;
    const ongoing=!debt.continueAfterDeadline?'no ongoing interest':debt.postDeadlineMode==='custom'?`${Number(debt.postDeadlineApr)||0}% APR afterward`:`${Number(debt.deadlineMarkupPct)||0}% APR afterward`;
    return `Due ${debt.deadlineDate?fmtDate(debt.deadlineDate):'date not set'} · ${Number(debt.deadlineMarkupPct)||0}% one-time markup · ${ongoing}`;
  }
  function accrueDebtEntry(entry,toDate) {
    if (!entry || !toDate || toDate<=entry.currentDate || entry.balanceUSD<=0) { if(entry&&toDate>entry.currentDate)entry.currentDate=toDate; return; }
    const debt=entry.debt;
    const addInterest=(days,rate)=>{
      if(days<=0 || rate<=0 || entry.balanceUSD<=0) return;
      const amount=entry.balanceUSD*(rate/100)*days/365;
      entry.balanceUSD+=amount;
      entry.interestUSD=(entry.interestUSD||0)+amount;
    };
    if(debtTypeOf(debt)==='deadline' && debt.deadlineDate && !entry.deadlineMarkupApplied && entry.currentDate<=debt.deadlineDate && toDate>debt.deadlineDate){
      addInterest(daysBetween(entry.currentDate,debt.deadlineDate),Math.max(0,Number(debt.apr)||0));
      entry.currentDate=debt.deadlineDate;
      if(entry.balanceUSD>.005){
        const markup=entry.balanceUSD*(Math.max(0,Number(debt.deadlineMarkupPct)||0)/100);
        entry.balanceUSD+=markup;
        entry.markupUSD=(entry.markupUSD||0)+markup;
      }
      entry.deadlineMarkupApplied=true;
      addInterest(daysBetween(entry.currentDate,toDate),postDeadlineApr(debt));
      entry.currentDate=toDate;
      return;
    }
    const rate=debtTypeOf(debt)==='deadline' && debt.deadlineDate && (entry.deadlineMarkupApplied || entry.currentDate>debt.deadlineDate) ? postDeadlineApr(debt) : Math.max(0,Number(debt.apr)||0);
    addInterest(daysBetween(entry.currentDate,toDate),rate);
    entry.currentDate=toDate;
  }

  function buildDebtPaymentEvents(targetDate=state.settings.targetDate) {"""
html = replace_once(html, engine_anchor, engine_helpers, 'deadline engine helpers')

init_old = """    state.debts.forEach(debt=>ledger[debt.id]={debt,balanceUSD:toUSD(Number(debt.balance)||0,debt.currency),interestUSD:0,paymentsUSD:0,currentDate:state.settings.forecastStart,payoffDate:null});"""
init_new = """    state.debts.forEach(debt=>ledger[debt.id]={debt,balanceUSD:toUSD(Number(debt.balance)||0,debt.currency),interestUSD:0,markupUSD:0,paymentsUSD:0,currentDate:state.settings.forecastStart,payoffDate:null,deadlineMarkupApplied:false});"""
html = replace_once(html, init_old, init_new, 'debt simulation initialization')

accrual_old = """      const days=daysBetween(entry.currentDate,event.date);
      const accrued=entry.balanceUSD*(Number(entry.debt.apr)/100)*days/365;
      entry.balanceUSD+=accrued;
      entry.interestUSD+=accrued;
      entry.currentDate=event.date;"""
accrual_new = """      accrueDebtEntry(entry,event.date);"""
html = replace_once(html, accrual_old, accrual_new, 'event debt accrual')

event_old = """      actualEvents.push({...event,amountUSD:-paidUSD,requestedAmountUSD:requestedUSD,debtName:entry.debt.name,debtCurrency:entry.debt.currency,debtRemainingUSD:entry.balanceUSD,debtInterestAccruedUSD:entry.interestUSD,debtPaidOff:entry.balanceUSD<=.005});"""
event_new = """      actualEvents.push({...event,amountUSD:-paidUSD,requestedAmountUSD:requestedUSD,debtName:entry.debt.name,debtCurrency:entry.debt.currency,debtRemainingUSD:entry.balanceUSD,debtInterestAccruedUSD:entry.interestUSD,debtMarkupAccruedUSD:entry.markupUSD||0,debtPaidOff:entry.balanceUSD<=.005});"""
html = replace_once(html, event_old, event_new, 'ledger debt event metadata')

final_old = """    Object.values(ledger).forEach(entry=>{
      const finalDays=daysBetween(entry.currentDate,targetDate);
      const finalInterest=entry.balanceUSD*(Number(entry.debt.apr)/100)*finalDays/365;
      entry.balanceUSD+=finalInterest;
      entry.interestUSD+=finalInterest;
      entry.currentDate=targetDate;
    });
    const projections={};
    Object.values(ledger).forEach(entry=>projections[entry.debt.id]={balanceUSD:entry.balanceUSD,interestUSD:entry.interestUSD,paymentsUSD:entry.paymentsUSD,payoffDate:entry.payoffDate});"""
final_new = """    Object.values(ledger).forEach(entry=>accrueDebtEntry(entry,targetDate));
    const projections={};
    Object.values(ledger).forEach(entry=>projections[entry.debt.id]={balanceUSD:entry.balanceUSD,interestUSD:entry.interestUSD,markupUSD:entry.markupUSD||0,paymentsUSD:entry.paymentsUSD,payoffDate:entry.payoffDate,deadlineMarkupApplied:entry.deadlineMarkupApplied});"""
html = replace_once(html, final_old, final_new, 'final debt accrual')

project_default_old = """    return simulateDebtPayments(targetDate).projections[debt.id]||{balanceUSD:0,interestUSD:0,paymentsUSD:0,payoffDate:null};"""
project_default_new = """    return simulateDebtPayments(targetDate).projections[debt.id]||{balanceUSD:0,interestUSD:0,markupUSD:0,paymentsUSD:0,payoffDate:null};"""
html = replace_once(html, project_default_old, project_default_new, 'project debt default')

target_default_old = """      const targetProjection=debtSimulation.projections[d.id]||{balanceUSD:0,interestUSD:0,paymentsUSD:0,payoffDate:null};"""
target_default_new = """      const targetProjection=debtSimulation.projections[d.id]||{balanceUSD:0,interestUSD:0,markupUSD:0,paymentsUSD:0,payoffDate:null};"""
html = replace_once(html, target_default_old, target_default_new, 'summary projection default')

summary_old = """    const interest=debtProjections.reduce((s,d)=>s+d.interestUSD,0);
    return {events,income,gross,outflows,cash,totalDebt,revolvingDebt,interest,debtProjections};"""
summary_new = """    const interest=debtProjections.reduce((s,d)=>s+d.interestUSD,0);
    const deadlineMarkup=debtProjections.reduce((s,d)=>s+(d.markupUSD||0),0);
    return {events,income,gross,outflows,cash,totalDebt,revolvingDebt,interest,deadlineMarkup,debtProjections};"""
html = replace_once(html, summary_old, summary_new, 'summary deadline markup')

interest_detail_old = """    document.getElementById('debtInterestDetail').textContent=`About ${money(s.interest)} interest accrued in forecast`;"""
interest_detail_new = """    document.getElementById('debtInterestDetail').textContent=s.deadlineMarkup>0?`About ${money(s.interest)} interest + ${money(s.deadlineMarkup)} missed-deadline markup`:`About ${money(s.interest)} interest accrued in forecast`;"""
html = replace_once(html, interest_detail_old, interest_detail_new, 'dashboard markup summary')

breakdown_old = """      return `<div class="debt-breakdown-row"><div><div class="debt-breakdown-name">${escapeHtml(x.debt.name)}</div><div class="debt-breakdown-meta">${Number(x.debt.apr).toFixed(2).replace(/\.00$/,'')}% APR · ${x.debt.currency}</div></div><div><div class="debt-stat-label">Balance at target</div><div class="debt-stat-value">${money2(originalBalance,x.debt.currency)}</div>${x.debt.currency==='CAD'?`<div class="debt-breakdown-meta">${money2(x.balanceUSD)} USD equivalent</div>`:''}</div><div><div class="debt-stat-label">Interest accrued</div><div class="debt-stat-value">${money2(originalInterest,x.debt.currency)}</div></div><div><div class="debt-stat-label">Projected payoff</div><div class="debt-stat-value">${payoff}</div></div></div>`;"""
breakdown_new = """      const originalMarkup=fromUSD(x.markupUSD||0,x.debt.currency);
      return `<div class="debt-breakdown-row"><div><div class="debt-breakdown-name">${escapeHtml(x.debt.name)}</div><div class="debt-breakdown-meta">${escapeHtml(debtTermsText(x.debt))} · ${x.debt.currency}</div>${debtTypeOf(x.debt)==='deadline'?'<span class="debt-term-badge">Deadline debt</span>':''}</div><div><div class="debt-stat-label">Balance at target</div><div class="debt-stat-value">${money2(originalBalance,x.debt.currency)}</div>${x.debt.currency==='CAD'?`<div class="debt-breakdown-meta">${money2(x.balanceUSD)} USD equivalent</div>`:''}</div><div><div class="debt-stat-label">Interest and markup</div><div class="debt-stat-value">${money2(originalInterest,x.debt.currency)} interest</div>${originalMarkup>0?`<div class="debt-breakdown-meta deadline-warning">${money2(originalMarkup,x.debt.currency)} deadline markup</div>`:''}</div><div><div class="debt-stat-label">Projected payoff</div><div class="debt-stat-value">${payoff}</div></div></div>`;"""
html = replace_once(html, breakdown_old, breakdown_new, 'deadline debt breakdown')

ledger_old = """const interestOriginal=isDebt&&debt?fromUSD(e.debtInterestAccruedUSD||0,debt.currency):0;return `<tr data-ledger-row="${index}"><td>${fmtDate(e.date)}</td><td>${escapeHtml(e.name)}</td><td><span class="pill">${escapeHtml(e.type)}</span>${isDebt?`<button class="ledger-detail-toggle" type="button" data-ledger-toggle="${index}" aria-expanded="false">Show balance →</button>`:''}</td><td class="amount ${e.amountUSD>=0?'in':'out'}">${e.amountUSD>=0?'+':''}${money2(e.amountUSD)}</td><td>${money2(e.runningBalance)}</td><td class="debt-detail-cell"><div class="debt-detail-inner">${isDebt&&debt?`<div class="debt-detail-title">${escapeHtml(debt.name)}</div><div class="debt-detail-line"><span>Remaining</span><strong>${money2(remainingOriginal,debt.currency)}</strong></div><div class="debt-detail-line"><span>Interest accrued</span><strong>${money2(interestOriginal,debt.currency)}</strong></div>${e.debtPaidOff?'<span class="paid-off-badge">Paid off with this payment</span>':''}`:''}</div></td></tr>`"""
ledger_new = """const interestOriginal=isDebt&&debt?fromUSD(e.debtInterestAccruedUSD||0,debt.currency):0;const markupOriginal=isDebt&&debt?fromUSD(e.debtMarkupAccruedUSD||0,debt.currency):0;return `<tr data-ledger-row="${index}"><td>${fmtDate(e.date)}</td><td>${escapeHtml(e.name)}</td><td><span class="pill">${escapeHtml(e.type)}</span>${isDebt?`<button class="ledger-detail-toggle" type="button" data-ledger-toggle="${index}" aria-expanded="false">Show balance →</button>`:''}</td><td class="amount ${e.amountUSD>=0?'in':'out'}">${e.amountUSD>=0?'+':''}${money2(e.amountUSD)}</td><td>${money2(e.runningBalance)}</td><td class="debt-detail-cell"><div class="debt-detail-inner">${isDebt&&debt?`<div class="debt-detail-title">${escapeHtml(debt.name)}</div><div class="debt-detail-line"><span>Remaining</span><strong>${money2(remainingOriginal,debt.currency)}</strong></div><div class="debt-detail-line"><span>Interest accrued</span><strong>${money2(interestOriginal,debt.currency)}</strong></div>${markupOriginal>0?`<div class="debt-detail-line"><span>Deadline markup</span><strong class="deadline-warning">${money2(markupOriginal,debt.currency)}</strong></div>`:''}${e.debtPaidOff?'<span class="paid-off-badge">Paid off with this payment</span>':''}`:''}</div></td></tr>`"""
html = replace_once(html, ledger_old, ledger_new, 'ledger markup details')

render_debts_old = """    document.getElementById('debtCards').innerHTML=projections.map(({d,p})=>{const opening=toUSD(d.balance,d.currency);const pct=opening?Math.min(100,p.balanceUSD/opening*100):0;return `<div class="card"><div class="label">${escapeHtml(d.name)}</div><div class="value ${d.apr>=20?'warning':''}">${money(p.balanceUSD)}</div><div class="detail">${d.apr}% APR · ${money(p.paymentsUSD)} paid</div><div class="debt-bar"><div class="bar-bg"><div class="bar-fill" style="width:${pct}%"></div></div></div></div>`}).join('');
    document.getElementById('debtTable').innerHTML=projections.map(({d,p})=>`<tr><td>${escapeHtml(d.name)}</td><td>${money2(d.balance,d.currency)}</td><td>${d.apr}%</td><td>${money2(p.paymentsUSD)}</td><td>${money2(p.interestUSD)}</td><td><strong>${money2(p.balanceUSD)}</strong></td><td><button class="btn sm secondary" data-action="edit-debt" data-id="${d.id}">Edit</button> <button class="btn sm danger" data-action="delete-debt" data-id="${d.id}">Delete</button></td></tr>`).join('');"""
render_debts_new = """    document.getElementById('debtCards').innerHTML=projections.map(({d,p})=>{const opening=toUSD(d.balance,d.currency);const pct=opening?Math.min(100,p.balanceUSD/opening*100):0;return `<div class="card"><div class="label">${escapeHtml(d.name)}</div><div class="value ${debtPlannerRate(d,state.settings.targetDate)>=20?'warning':''}">${money(p.balanceUSD)}</div><div class="detail">${escapeHtml(debtTermsText(d))} · ${money(p.paymentsUSD)} paid</div>${debtTypeOf(d)==='deadline'?'<span class="debt-term-badge">Deadline debt</span>':''}<div class="debt-bar"><div class="bar-bg"><div class="bar-fill" style="width:${pct}%"></div></div></div></div>`}).join('');
    document.getElementById('debtTable').innerHTML=projections.map(({d,p})=>`<tr><td>${escapeHtml(d.name)}${debtTypeOf(d)==='deadline'?'<br><span class="debt-term-badge">Deadline debt</span>':''}</td><td>${money2(d.balance,d.currency)}</td><td>${escapeHtml(debtTermsText(d))}</td><td>${money2(p.paymentsUSD)}</td><td>${money2(p.interestUSD)}</td><td>${money2(p.markupUSD||0)}</td><td><strong>${money2(p.balanceUSD)}</strong></td><td><button class="btn sm secondary" data-action="edit-debt" data-id="${d.id}">Edit</button> <button class="btn sm danger" data-action="delete-debt" data-id="${d.id}">Delete</button></td></tr>`).join('');"""
html = replace_once(html, render_debts_old, render_debts_new, 'deadline debt cards and table')

clear_old = """  function clearDebtForm(){document.getElementById('debtForm').reset();document.getElementById('debtId').value='';document.getElementById('debtRevolving').checked=true;document.getElementById('debtMinimum').value=0;}"""
clear_new = """  function updateDebtDeadlineVisibility(){
    const isDeadline=document.getElementById('debtType').value==='deadline';
    const continuing=document.getElementById('debtContinueAfterDeadline').checked;
    const custom=document.getElementById('debtPostDeadlineMode').value==='custom';
    document.getElementById('debtDeadlineFields').classList.toggle('hidden',!isDeadline);
    document.getElementById('debtPostModeWrap').classList.toggle('hidden',!isDeadline||!continuing);
    document.getElementById('debtPostAprWrap').classList.toggle('hidden',!isDeadline||!continuing||!custom);
    document.getElementById('debtDeadlineDate').required=isDeadline;
  }
  function clearDebtForm(){document.getElementById('debtForm').reset();document.getElementById('debtId').value='';document.getElementById('debtRevolving').checked=true;document.getElementById('debtMinimum').value=0;document.getElementById('debtType').value='standard';document.getElementById('debtDeadlineMarkup').value=0;document.getElementById('debtPostDeadlineApr').value=0;updateDebtDeadlineVisibility();}"""
html = replace_once(html, clear_old, clear_new, 'deadline form clear and visibility')

listener_anchor = """  document.getElementById('clearDebt').addEventListener('click',clearDebtForm);

  document.body.addEventListener('click',e=>{"""
listener_new = """  document.getElementById('clearDebt').addEventListener('click',clearDebtForm);
  document.getElementById('debtType').addEventListener('change',updateDebtDeadlineVisibility);
  document.getElementById('debtContinueAfterDeadline').addEventListener('change',updateDebtDeadlineVisibility);
  document.getElementById('debtPostDeadlineMode').addEventListener('change',updateDebtDeadlineVisibility);

  document.body.addEventListener('click',e=>{"""
html = replace_once(html, listener_anchor, listener_new, 'deadline form listeners')

submit_old = """  document.getElementById('debtForm').addEventListener('submit',e=>{e.preventDefault();const id=document.getElementById('debtId').value||uid('debt');const obj={id,name:debtName.value,balance:Number(debtBalance.value),currency:debtCurrency.value,apr:Number(debtApr.value),minimum:Number(debtMinimum.value)||0,deferredUntil:debtDeferredUntil.value,revolving:debtRevolving.checked};const idx=state.debts.findIndex(x=>x.id===id);if(idx>=0)state.debts[idx]=obj;else state.debts.push(obj);clearDebtForm();renderAll();});"""
submit_new = """  document.getElementById('debtForm').addEventListener('submit',e=>{e.preventDefault();const type=debtType.value;if(type==='deadline'&&!debtDeadlineDate.value){alert('Choose the date by which this debt must be paid.');return;}const id=document.getElementById('debtId').value||uid('debt');const obj={id,name:debtName.value,balance:Number(debtBalance.value),currency:debtCurrency.value,debtType:type,apr:Number(debtApr.value),minimum:Number(debtMinimum.value)||0,deferredUntil:debtDeferredUntil.value,revolving:debtRevolving.checked,deadlineDate:type==='deadline'?debtDeadlineDate.value:'',deadlineMarkupPct:type==='deadline'?(Number(debtDeadlineMarkup.value)||0):0,continueAfterDeadline:type==='deadline'&&debtContinueAfterDeadline.checked,postDeadlineMode:type==='deadline'?debtPostDeadlineMode.value:'same',postDeadlineApr:type==='deadline'?(Number(debtPostDeadlineApr.value)||0):0};const idx=state.debts.findIndex(x=>x.id===id);if(idx>=0)state.debts[idx]=obj;else state.debts.push(obj);clearDebtForm();renderAll();});"""
html = replace_once(html, submit_old, submit_new, 'deadline debt save')

edit_old = """    if(action==='edit-debt'){const d=state.debts.find(x=>x.id===id);if(!d)return;debtId.value=d.id;debtName.value=d.name;debtBalance.value=d.balance;debtCurrency.value=d.currency;debtApr.value=d.apr;debtMinimum.value=d.minimum||0;debtDeferredUntil.value=d.deferredUntil||'';debtRevolving.checked=d.revolving;document.querySelector('[data-tab="debts"]').click();window.scrollTo({top:0,behavior:'smooth'});}"""
edit_new = """    if(action==='edit-debt'){const d=state.debts.find(x=>x.id===id);if(!d)return;debtId.value=d.id;debtName.value=d.name;debtBalance.value=d.balance;debtCurrency.value=d.currency;debtType.value=debtTypeOf(d);debtApr.value=d.apr;debtMinimum.value=d.minimum||0;debtDeferredUntil.value=d.deferredUntil||'';debtRevolving.checked=d.revolving;debtDeadlineDate.value=d.deadlineDate||'';debtDeadlineMarkup.value=d.deadlineMarkupPct||0;debtContinueAfterDeadline.checked=!!d.continueAfterDeadline;debtPostDeadlineMode.value=d.postDeadlineMode||'same';debtPostDeadlineApr.value=d.postDeadlineApr||0;updateDebtDeadlineVisibility();document.querySelector('[data-tab="debts"]').click();window.scrollTo({top:0,behavior:'smooth'});}"""
html = replace_once(html, edit_old, edit_new, 'deadline debt edit')

avalanche_init_old = """    state.debts.forEach(d=>debtState[d.id]={balanceUSD:toUSD(Number(d.balance)||0,d.currency),debt:d});
    let cash=Number(state.settings.startingCash)||0;
    let lastDate=state.settings.forecastStart;"""
avalanche_init_new = """    state.debts.forEach(d=>debtState[d.id]={balanceUSD:toUSD(Number(d.balance)||0,d.currency),debt:d,interestUSD:0,markupUSD:0,currentDate:state.settings.forecastStart,deadlineMarkupApplied:false});
    let cash=Number(state.settings.startingCash)||0;"""
html = replace_once(html, avalanche_init_old, avalanche_init_new, 'avalanche debt initialization')

avalanche_accrue_old = """    const accrueTo=date=>{
      const days=Math.max(0,daysBetween(lastDate,date));
      if(days>0){
        Object.values(debtState).forEach(x=>{
          if(x.balanceUSD>0 && Number(x.debt.apr)>0) x.balanceUSD += x.balanceUSD*(Number(x.debt.apr)/100)*days/365;
        });
      }
      lastDate=date;
    };"""
avalanche_accrue_new = """    const accrueTo=date=>{Object.values(debtState).forEach(x=>accrueDebtEntry(x,date));};"""
html = replace_once(html, avalanche_accrue_old, avalanche_accrue_new, 'avalanche deadline accrual')

avalanche_apr_old = """        const aprOk=Number(d.apr)>=cfg.minApr;"""
avalanche_apr_new = """        const aprOk=debtPlannerRate(d,day)>=cfg.minApr;"""
html = replace_once(html, avalanche_apr_old, avalanche_apr_new, 'avalanche effective rate eligibility')

avalanche_sort_old = """      }).sort((a,b)=>Number(b.apr)-Number(a.apr)||(debtState[a.id].balanceUSD-debtState[b.id].balanceUSD));"""
avalanche_sort_new = """      }).sort((a,b)=>debtPlannerRate(b,day)-debtPlannerRate(a,day)||((a.deadlineDate||'9999-12-31').localeCompare(b.deadlineDate||'9999-12-31'))||(debtState[a.id].balanceUSD-debtState[b.id].balanceUSD));"""
html = replace_once(html, avalanche_sort_old, avalanche_sort_new, 'avalanche deadline priority')

csv_old = """['Date','Item','Type','Amount USD','Running cash USD','Debt remaining USD']"""
csv_new = """['Date','Item','Type','Amount USD','Running cash USD','Debt remaining USD','Deadline markup accrued USD']"""
html = replace_once(html, csv_old, csv_new, 'CSV header deadline markup')

csv_row_old = """e.debtRemainingUSD===undefined?'':e.debtRemainingUSD.toFixed(2)])"""
csv_row_new = """e.debtRemainingUSD===undefined?'':e.debtRemainingUSD.toFixed(2),e.debtMarkupAccruedUSD===undefined?'':e.debtMarkupAccruedUSD.toFixed(2)])"""
html = replace_once(html, csv_row_old, csv_row_new, 'CSV row deadline markup')

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
sw = sw.replace("const CACHE = 'financial-planner-secure-v5-debt-details';", "const CACHE = 'financial-planner-secure-v6-deadline-debt';")
SW.write_text(sw, encoding='utf-8')
print('Applied v6 deadline debt feature.')
