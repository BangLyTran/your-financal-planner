from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')

if 'id="planProtectUrgent"' in html and 'financial-planner-secure-v7-smart-priority' in SW.read_text(encoding='utf-8'):
    print('v7 smart priority planner is already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

css_anchor = """    .debt-term-badge { display:inline-flex; align-items:center; padding:3px 7px; border-radius:999px; background:#fef3c7; color:#92400e; font-size:.72rem; font-weight:800; margin-top:5px; }
    .deadline-warning { color:#b45309; font-weight:750; }
"""
css_new = """    .debt-term-badge { display:inline-flex; align-items:center; padding:3px 7px; border-radius:999px; background:#fef3c7; color:#92400e; font-size:.72rem; font-weight:800; margin-top:5px; }
    .priority-badge { display:inline-flex; align-items:center; padding:3px 7px; border-radius:999px; background:#fee2e2; color:#991b1b; font-size:.72rem; font-weight:850; margin-top:5px; margin-left:5px; }
    .deadline-warning { color:#b45309; font-weight:750; }
    .planner-protection-box { flex-basis:100%; display:grid; grid-template-columns:repeat(3,minmax(180px,1fr)); gap:12px; padding:14px; border:1px solid #fecaca; border-radius:14px; background:linear-gradient(135deg,#fff1f2,#fff); }
    .planner-protection-title { grid-column:1 / -1; color:#991b1b; font-weight:850; }
    .planner-protection-note { grid-column:1 / -1; color:#7f1d1d; font-size:.8rem; line-height:1.45; }
"""
html = replace_once(html, css_anchor, css_new, 'priority planner CSS')

responsive_anchor = """      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .debt-breakdown-row { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
responsive_new = """      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }
      .planner-protection-box { grid-template-columns:1fr; }
      .planner-protection-title, .planner-protection-note { grid-column:1; }
      .debt-breakdown-row { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
html = replace_once(html, responsive_anchor, responsive_new, 'priority planner responsive CSS')

intro_old = """            <div class="muted small">Generates interest-aware payments on paydays, highest APR first. It preserves your cash floor, reserves bills until the next paycheck, and can keep part of each safe surplus as additional savings.</div>"""
intro_new = """            <div class="muted small">Builds payments on paydays using two layers: first it protects deadline and explicitly high-priority debts from avoidable penalties, then it applies the normal APR avalanche to remaining safe surplus.</div>"""
html = replace_once(html, intro_old, intro_new, 'planner description')

controls_old = """          <div><label>Debt scope</label><div class="check-row"><input id="planRevolvingOnly" type="checkbox" /> Only debts marked revolving/high-interest</div></div>
          <div><button class="btn good" id="generateAvalanche">Generate balanced avalanche</button></div>"""
controls_new = """          <div><label>Debt scope</label><div class="check-row"><input id="planRevolvingOnly" type="checkbox" /> Only ordinary avalanche debts marked revolving/high-interest</div></div>
          <div class="planner-protection-box">
            <div class="planner-protection-title">Deadline and high-priority protection</div>
            <div><label>Enable smart protection</label><div class="check-row"><input id="planProtectUrgent" type="checkbox" checked /> Pay deadline/high-priority debt before the ordinary avalanche</div></div>
            <div><label>Urgent-payment hard cash floor</label><input id="planUrgentCashFloor" type="number" step="100" min="0" value="2500" /><div class="muted small">The planner may dip below your normal cash floor, but not below this emergency floor.</div></div>
            <div><label>Override per-payday maximum when required</label><div class="check-row"><input id="planUrgentOverrideMax" type="checkbox" checked /> Allow a larger payment when needed and affordable before a deadline</div></div>
            <div class="planner-protection-note">Deadline and high-priority debts ignore the minimum-APR and revolving-only filters. The system pays them as early as practical while reserving bills until the next paycheck and preserving the urgent hard floor.</div>
          </div>
          <div><button class="btn good" id="generateAvalanche">Generate smart payoff plan</button></div>"""
html = replace_once(html, controls_old, controls_new, 'priority planner controls')

footer_old = """        <div id="avalancheSummary" class="footer-note">Recommended starting point: $20,000 floor, 50% of safe surplus, and minimum APR of 10%. This pays costly debt while allowing cash to rise above the floor.</div>"""
footer_new = """        <div id="avalancheSummary" class="footer-note">Smart protection uses a lower hard emergency floor only for deadline and explicitly high-priority debts. Ordinary debts still follow your normal cash floor, allocation percentage, APR threshold, and scope settings.</div>"""
html = replace_once(html, footer_old, footer_new, 'planner footer')

priority_form_anchor = """            <div><label>Revolving/high-interest</label><div class="check-row"><input id="debtRevolving" type="checkbox" checked /> Mark as revolving/high-interest for optional planner filtering</div></div>
            <div id="debtDeadlineFields" class="debt-deadline-panel hidden">"""
priority_form_new = """            <div><label>Revolving/high-interest</label><div class="check-row"><input id="debtRevolving" type="checkbox" checked /> Mark as revolving/high-interest for optional ordinary-avalanche filtering</div></div>
            <div><label>High priority</label><div class="check-row"><input id="debtPriority" type="checkbox" /> Pay as soon as practical using the urgent-payment safety floor</div><div class="muted small">Deadline debts are automatically treated as high priority.</div></div>
            <div id="debtDeadlineFields" class="debt-deadline-panel hidden">"""
html = replace_once(html, priority_form_anchor, priority_form_new, 'priority debt toggle')

state_old = """      minApr: 10,
      revolvingOnly: false
"""
state_new = """      minApr: 10,
      revolvingOnly: false,
      protectUrgent: true,
      urgentCashFloor: 2500,
      urgentOverrideMax: true
"""
html = replace_once(html, state_old, state_new, 'priority planner defaults')

helper_anchor = """  function debtTypeOf(debt) { return debt?.debtType === 'deadline' ? 'deadline' : 'standard'; }
"""
helper_new = """  function debtTypeOf(debt) { return debt?.debtType === 'deadline' ? 'deadline' : 'standard'; }
  function isUrgentDebt(debt) { return debtTypeOf(debt)==='deadline' || Boolean(debt?.priority); }
"""
html = replace_once(html, helper_anchor, helper_new, 'urgent debt helper')

render_controls_old = """    document.getElementById('planMinApr').value = Number(p.minApr) || 0;
    document.getElementById('planRevolvingOnly').checked = Boolean(p.revolvingOnly);
"""
render_controls_new = """    document.getElementById('planMinApr').value = Number(p.minApr) || 0;
    document.getElementById('planRevolvingOnly').checked = Boolean(p.revolvingOnly);
    document.getElementById('planProtectUrgent').checked = p.protectUrgent !== false;
    document.getElementById('planUrgentCashFloor').value = Number.isFinite(Number(p.urgentCashFloor)) ? Number(p.urgentCashFloor) : 2500;
    document.getElementById('planUrgentOverrideMax').checked = p.urgentOverrideMax !== false;
"""
html = replace_once(html, render_controls_old, render_controls_new, 'render priority planner controls')

cards_old = """${debtTypeOf(d)==='deadline'?'<span class="debt-term-badge">Deadline debt</span>':''}<div class="debt-bar">"""
cards_new = """${debtTypeOf(d)==='deadline'?'<span class="debt-term-badge">Deadline debt</span>':''}${d.priority&&debtTypeOf(d)!=='deadline'?'<span class="priority-badge">High priority</span>':''}<div class="debt-bar">"""
html = replace_once(html, cards_old, cards_new, 'priority debt card badge')

table_old = """${debtTypeOf(d)==='deadline'?'<br><span class="debt-term-badge">Deadline debt</span>':''}</td><td>${money2(d.balance,d.currency)}"""
table_new = """${debtTypeOf(d)==='deadline'?'<br><span class="debt-term-badge">Deadline debt</span>':''}${d.priority&&debtTypeOf(d)!=='deadline'?'<br><span class="priority-badge">High priority</span>':''}</td><td>${money2(d.balance,d.currency)}"""
html = replace_once(html, table_old, table_new, 'priority debt table badge')

clear_old = """function clearDebtForm(){document.getElementById('debtForm').reset();document.getElementById('debtId').value='';document.getElementById('debtRevolving').checked=true;document.getElementById('debtMinimum').value=0;document.getElementById('debtType').value='standard';document.getElementById('debtDeadlineMarkup').value=0;document.getElementById('debtPostDeadlineApr').value=0;updateDebtDeadlineVisibility();}"""
clear_new = """function clearDebtForm(){document.getElementById('debtForm').reset();document.getElementById('debtId').value='';document.getElementById('debtRevolving').checked=true;document.getElementById('debtPriority').checked=false;document.getElementById('debtMinimum').value=0;document.getElementById('debtType').value='standard';document.getElementById('debtDeadlineMarkup').value=0;document.getElementById('debtPostDeadlineApr').value=0;updateDebtDeadlineVisibility();}"""
html = replace_once(html, clear_old, clear_new, 'clear priority debt form')

submit_old = """revolving:debtRevolving.checked,deadlineDate:type==='deadline'?debtDeadlineDate.value:''"""
submit_new = """revolving:debtRevolving.checked,priority:debtPriority.checked,deadlineDate:type==='deadline'?debtDeadlineDate.value:''"""
html = replace_once(html, submit_old, submit_new, 'save priority debt')

edit_old = """debtDeferredUntil.value=d.deferredUntil||'';debtRevolving.checked=d.revolving;debtDeadlineDate.value=d.deadlineDate||'';"""
edit_new = """debtDeferredUntil.value=d.deferredUntil||'';debtRevolving.checked=d.revolving;debtPriority.checked=!!d.priority;debtDeadlineDate.value=d.deadlineDate||'';"""
html = replace_once(html, edit_old, edit_new, 'edit priority debt')

read_old = """      minApr: Math.max(0, Number(document.getElementById('planMinApr').value) || 0),
      revolvingOnly: document.getElementById('planRevolvingOnly').checked
"""
read_new = """      minApr: Math.max(0, Number(document.getElementById('planMinApr').value) || 0),
      revolvingOnly: document.getElementById('planRevolvingOnly').checked,
      protectUrgent: document.getElementById('planProtectUrgent').checked,
      urgentCashFloor: Math.max(0, Number(document.getElementById('planUrgentCashFloor').value) || 0),
      urgentOverrideMax: document.getElementById('planUrgentOverrideMax').checked
"""
html = replace_once(html, read_old, read_new, 'read priority planner controls')

change_old = """  ['planCashFloor','planMaxPayment','planAllocationPct','planMinApr','planRevolvingOnly'].forEach(id=>{"""
change_new = """  ['planCashFloor','planMaxPayment','planAllocationPct','planMinApr','planRevolvingOnly','planProtectUrgent','planUrgentCashFloor','planUrgentOverrideMax'].forEach(id=>{"""
html = replace_once(html, change_old, change_new, 'priority planner control listeners')

old_listener_start = """  document.getElementById('generateAvalanche').addEventListener('click',()=>{
    state.bills=state.bills.filter(b=>!b.autoGenerated);
    state.debtPlanner = readDebtPlannerControls();
    const cfg=state.debtPlanner;
    const floor=cfg.cashFloor;
    const maxPay=cfg.maxPerPayday>0?cfg.maxPerPayday:Infinity;
    const allocation=cfg.allocationPct/100;
    const baseEvents=buildEvents(state.settings.targetDate,true);
    const paydays=[...new Set(baseEvents.filter(e=>e.source==='income').map(e=>e.date))].sort();
    const paydaySet=new Set(paydays);
    const eventsByDate=new Map();
    baseEvents.forEach(e=>{if(!eventsByDate.has(e.date))eventsByDate.set(e.date,[]);eventsByDate.get(e.date).push(e);});
    const dates=[...eventsByDate.keys()].sort();
    const debtState={};
    state.debts.forEach(d=>debtState[d.id]={balanceUSD:toUSD(Number(d.balance)||0,d.currency),debt:d,interestUSD:0,markupUSD:0,currentDate:state.settings.forecastStart,deadlineMarkupApplied:false});
    let cash=Number(state.settings.startingCash)||0;
    let totalGenerated=0;
    let paymentCount=0;
    const targeted=new Set();

    const accrueTo=date=>{Object.values(debtState).forEach(x=>accrueDebtEntry(x,date));};

    for(const day of dates){
      accrueTo(day);
      const dayEvents=eventsByDate.get(day)||[];
      dayEvents.forEach(e=>{
        cash+=e.amountUSD;
        if(e.debtId && e.amountUSD<0 && debtState[e.debtId]){
          debtState[e.debtId].balanceUSD=Math.max(0,debtState[e.debtId].balanceUSD-Math.abs(e.amountUSD));
        }
      });
      if(!paydaySet.has(day) || allocation<=0) continue;
      const idx=paydays.indexOf(day);
      const next=paydays[idx+1]||'9999-12-31';
      const futureBills=baseEvents.filter(e=>e.date>day&&e.date<next&&e.amountUSD<0).reduce((s,e)=>s+Math.abs(e.amountUSD),0);
      const safeSurplus=Math.max(0,cash-futureBills-floor);
      let available=Math.min(maxPay,safeSurplus*allocation);
      const eligible=state.debts.filter(d=>{
        const current=debtState[d.id]?.balanceUSD||0;
        const deferOk=!d.deferredUntil||d.deferredUntil<=day;
        const aprOk=debtPlannerRate(d,day)>=cfg.minApr;
        const scopeOk=!cfg.revolvingOnly||Boolean(d.revolving);
        return current>.01&&deferOk&&aprOk&&scopeOk;
      }).sort((a,b)=>debtPlannerRate(b,day)-debtPlannerRate(a,day)||((a.deadlineDate||'9999-12-31').localeCompare(b.deadlineDate||'9999-12-31'))||(debtState[a.id].balanceUSD-debtState[b.id].balanceUSD));

      for(const d of eligible){
        if(available<=.01) break;
        const p=Math.min(available,debtState[d.id].balanceUSD);
        if(p<=.01) continue;
        state.bills.push({id:uid('auto'),name:`Auto avalanche: ${d.name}`,startDate:day,endDate:'',recurrence:'none',amount:Number(fromUSD(p,d.currency).toFixed(2)),currency:d.currency,category:'Debt payment',debtId:d.id,active:true,autoGenerated:true});
        debtState[d.id].balanceUSD=Math.max(0,debtState[d.id].balanceUSD-p);
        available-=p;
        cash-=p;
        totalGenerated+=p;
        paymentCount++;
        targeted.add(d.name);
      }
    }
    renderAll();
    const scope=cfg.revolvingOnly?'marked revolving/high-interest debts':`debts at or above ${cfg.minApr.toFixed(1)}% APR`;
    document.getElementById('avalancheSummary').textContent=paymentCount
      ?`Generated ${paymentCount} payment${paymentCount===1?'':'s'} totaling ${money(totalGenerated)} across ${[...targeted].join(', ')}. The plan sends ${cfg.allocationPct}% of safe surplus to ${scope}; the remainder stays as cash above your ${money(floor)} floor.`
      :`No payment was generated. The forecast never produced eligible safe surplus above the ${money(floor)} floor, or no debt met the ${cfg.minApr.toFixed(1)}% APR threshold.`;
  });"""

new_listener = """  document.getElementById('generateAvalanche').addEventListener('click',()=>{
    state.bills=state.bills.filter(b=>!b.autoGenerated);
    state.debtPlanner = readDebtPlannerControls();
    const cfg=state.debtPlanner;
    const floor=cfg.cashFloor;
    const urgentFloor=Math.min(floor,Math.max(0,Number(cfg.urgentCashFloor)||0));
    const maxPay=cfg.maxPerPayday>0?cfg.maxPerPayday:Infinity;
    const allocation=cfg.allocationPct/100;
    const baseEvents=buildEvents(state.settings.targetDate,true);
    const paydays=[...new Set(baseEvents.filter(e=>e.source==='income').map(e=>e.date))].sort();
    const paydaySet=new Set(paydays);
    const eventsByDate=new Map();
    baseEvents.forEach(e=>{if(!eventsByDate.has(e.date))eventsByDate.set(e.date,[]);eventsByDate.get(e.date).push(e);});
    const dates=[...eventsByDate.keys()].sort();
    const debtState={};
    state.debts.forEach(d=>debtState[d.id]={balanceUSD:toUSD(Number(d.balance)||0,d.currency),debt:d,interestUSD:0,markupUSD:0,currentDate:state.settings.forecastStart,deadlineMarkupApplied:false});
    let cash=Number(state.settings.startingCash)||0;
    let totalGenerated=0;
    let urgentGenerated=0;
    let ordinaryGenerated=0;
    let paymentCount=0;
    const targeted=new Set();
    const urgentTargeted=new Set();

    const accrueTo=date=>{Object.values(debtState).forEach(x=>accrueDebtEntry(x,date));};
    const addGeneratedPayment=(d,day,p,mode)=>{
      if(p<=.01)return 0;
      state.bills.push({id:uid('auto'),name:`${mode}: ${d.name}`,startDate:day,endDate:'',recurrence:'none',amount:Number(fromUSD(p,d.currency).toFixed(2)),currency:d.currency,category:'Debt payment',debtId:d.id,active:true,autoGenerated:true,priorityGenerated:mode!=='Auto avalanche'});
      debtState[d.id].balanceUSD=Math.max(0,debtState[d.id].balanceUSD-p);
      cash-=p;totalGenerated+=p;paymentCount++;targeted.add(d.name);
      if(mode!=='Auto avalanche'){urgentGenerated+=p;urgentTargeted.add(d.name);}else ordinaryGenerated+=p;
      return p;
    };
    const urgentSort=(a,b)=>{
      const aDeadline=debtTypeOf(a)==='deadline'&&a.deadlineDate;
      const bDeadline=debtTypeOf(b)==='deadline'&&b.deadlineDate;
      if(aDeadline&&!bDeadline)return -1;
      if(!aDeadline&&bDeadline)return 1;
      if(aDeadline&&bDeadline){
        const dateOrder=a.deadlineDate.localeCompare(b.deadlineDate);
        if(dateOrder)return dateOrder;
        const penaltyOrder=(Number(b.deadlineMarkupPct)||0)-(Number(a.deadlineMarkupPct)||0);
        if(penaltyOrder)return penaltyOrder;
      }
      return debtPlannerRate(b,state.settings.forecastStart)-debtPlannerRate(a,state.settings.forecastStart)||(debtState[a.id].balanceUSD-debtState[b.id].balanceUSD);
    };

    for(const day of dates){
      accrueTo(day);
      const dayEvents=eventsByDate.get(day)||[];
      dayEvents.forEach(e=>{
        cash+=e.amountUSD;
        if(e.debtId && e.amountUSD<0 && debtState[e.debtId]) debtState[e.debtId].balanceUSD=Math.max(0,debtState[e.debtId].balanceUSD-Math.abs(e.amountUSD));
      });
      if(!paydaySet.has(day)) continue;
      const idx=paydays.indexOf(day);
      const next=paydays[idx+1]||'9999-12-31';
      const futureBills=baseEvents.filter(e=>e.date>day&&e.date<next&&e.amountUSD<0).reduce((s,e)=>s+Math.abs(e.amountUSD),0);

      if(cfg.protectUrgent){
        let urgentAvailable=Math.max(0,cash-futureBills-urgentFloor);
        if(!cfg.urgentOverrideMax)urgentAvailable=Math.min(maxPay,urgentAvailable);
        const urgentDebts=state.debts.filter(d=>{
          const current=debtState[d.id]?.balanceUSD||0;
          const deferOk=!d.deferredUntil||d.deferredUntil<=day;
          return current>.01&&deferOk&&isUrgentDebt(d);
        }).sort(urgentSort);
        for(const d of urgentDebts){
          if(urgentAvailable<=.01)break;
          const p=Math.min(urgentAvailable,debtState[d.id].balanceUSD);
          const mode=debtTypeOf(d)==='deadline'?'Deadline protection':'Priority payoff';
          urgentAvailable-=addGeneratedPayment(d,day,p,mode);
        }
      }

      if(allocation<=0)continue;
      const safeSurplus=Math.max(0,cash-futureBills-floor);
      let available=Math.min(maxPay,safeSurplus*allocation);
      const eligible=state.debts.filter(d=>{
        const current=debtState[d.id]?.balanceUSD||0;
        const deferOk=!d.deferredUntil||d.deferredUntil<=day;
        const urgencyExemption=cfg.protectUrgent&&isUrgentDebt(d);
        const aprOk=urgencyExemption||debtPlannerRate(d,day)>=cfg.minApr;
        const scopeOk=urgencyExemption||!cfg.revolvingOnly||Boolean(d.revolving);
        return current>.01&&deferOk&&aprOk&&scopeOk;
      }).sort((a,b)=>{
        if(isUrgentDebt(a)!==isUrgentDebt(b))return isUrgentDebt(a)?-1:1;
        return debtPlannerRate(b,day)-debtPlannerRate(a,day)||((a.deadlineDate||'9999-12-31').localeCompare(b.deadlineDate||'9999-12-31'))||(debtState[a.id].balanceUSD-debtState[b.id].balanceUSD);
      });
      for(const d of eligible){
        if(available<=.01)break;
        const p=Math.min(available,debtState[d.id].balanceUSD);
        available-=addGeneratedPayment(d,day,p,'Auto avalanche');
      }
    }

    const protectedDeadlines=[];
    const atRiskDeadlines=[];
    state.debts.filter(d=>debtTypeOf(d)==='deadline'&&d.deadlineDate).forEach(d=>{
      const checkDate=toISO(addDays(parseDate(d.deadlineDate),1));
      const check=simulateDebtPayments(checkDate).projections[d.id];
      if(check&&check.payoffDate&&check.payoffDate<=d.deadlineDate&&(check.markupUSD||0)<=.005) protectedDeadlines.push(`${d.name} by ${fmtDate(check.payoffDate)}`);
      else if(check&&check.balanceUSD>.005) atRiskDeadlines.push(`${d.name}: about ${money2(fromUSD(check.balanceUSD,d.currency),d.currency)} remains after ${fmtDate(d.deadlineDate)}`);
    });

    renderAll();
    const scope=cfg.revolvingOnly?'ordinary debts marked revolving/high-interest':`ordinary debts at or above ${cfg.minApr.toFixed(1)}% APR`;
    const parts=[];
    if(paymentCount)parts.push(`Generated ${paymentCount} payment${paymentCount===1?'':'s'} totaling ${money(totalGenerated)} across ${[...targeted].join(', ')}.`);
    if(urgentGenerated>0)parts.push(`Smart protection sends ${money(urgentGenerated)} to ${[...urgentTargeted].join(', ')} using the ${money(urgentFloor)} urgent hard floor instead of waiting for cash to exceed the normal ${money(floor)} floor.`);
    if(ordinaryGenerated>0)parts.push(`The ordinary avalanche sends ${cfg.allocationPct}% of normal safe surplus to ${scope}, capped at ${money(maxPay)} per payday.`);
    if(protectedDeadlines.length)parts.push(`Protected before deadline: ${protectedDeadlines.join('; ')}.`);
    if(atRiskDeadlines.length)parts.push(`Still at risk: ${atRiskDeadlines.join('; ')}. The plan could not fully avoid the penalty while preserving upcoming bills and the ${money(urgentFloor)} hard floor; lower that floor, allow the max-payment override, reduce near-term spending, or add cash.`);
    if(!parts.length)parts.push(`No payment was generated. There was no affordable surplus above the urgent ${money(urgentFloor)} floor or normal ${money(floor)} floor.`);
    document.getElementById('avalancheSummary').textContent=parts.join(' ');
  });"""
html = replace_once(html, old_listener_start, new_listener, 'smart priority payment engine')

INDEX.write_text(html, encoding='utf-8')

sw = SW.read_text(encoding='utf-8')
sw = sw.replace("const CACHE = 'financial-planner-secure-v6-deadline-debt';", "const CACHE = 'financial-planner-secure-v7-smart-priority';")
SW.write_text(sw, encoding='utf-8')
print('Applied v7 smart deadline and priority payment planner.')
