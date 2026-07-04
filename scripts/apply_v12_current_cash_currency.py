from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')
service = SW.read_text(encoding='utf-8')

if 'id="quickCashForm"' in html and 'financial-planner-secure-v12-current-cash-currency' in service:
    print('v12 current-cash currency feature is already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

# Styles for a prominent, responsive current-cash control on the dashboard.
css_old = """    .allocation-note { margin-top:9px; color:var(--muted); font-size:.76rem; line-height:1.45; }

    @media (max-width: 1100px) {"""
css_new = """    .allocation-note { margin-top:9px; color:var(--muted); font-size:.76rem; line-height:1.45; }
    .cash-balance-panel { margin-bottom:16px; border-color:#bfdbfe; background:linear-gradient(135deg,#eff6ff,#fff); }
    .cash-balance-layout { display:grid; grid-template-columns:minmax(220px,.75fr) minmax(420px,1.25fr); gap:18px; align-items:end; }
    .cash-balance-title { margin:0 0 5px; }
    .cash-balance-entry { display:grid; grid-template-columns:minmax(180px,1fr) 120px auto; gap:10px; align-items:end; }
    .cash-equivalent { margin-top:7px; color:#1e40af; font-size:.8rem; font-weight:750; }
    .cash-field-note { margin-top:5px; color:var(--muted); font-size:.76rem; line-height:1.4; }

    @media (max-width: 1100px) {"""
html = replace_once(html, css_old, css_new, 'cash entry CSS')

responsive_old = """      .monthly-allocation-layout { grid-template-columns:1fr; }
      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
responsive_new = """      .monthly-allocation-layout { grid-template-columns:1fr; }
      .cash-balance-layout { grid-template-columns:1fr; }
      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
html = replace_once(html, responsive_old, responsive_new, 'cash entry responsive layout')

mobile_old = """      .cards, form .form-grid { grid-template-columns: 1fr; }
      .target-box { width: 100%; }"""
mobile_new = """      .cards, form .form-grid { grid-template-columns: 1fr; }
      .cash-balance-entry { grid-template-columns:1fr; }
      .target-box { width: 100%; }"""
html = replace_once(html, mobile_old, mobile_new, 'cash entry mobile layout')

# Dashboard quick entry.
dashboard_old = """    <section id="dashboard" class="tab active">
      <div id="riskNotice"></div>
      <div class="grid cards">"""
dashboard_new = """    <section id="dashboard" class="tab active">
      <div id="riskNotice"></div>
      <div class="panel cash-balance-panel">
        <div class="cash-balance-layout">
          <div>
            <h2 class="cash-balance-title">Current cash balance</h2>
            <div class="muted small">Enter the cash available at the forecast start date. Choose USD or CAD; the planner converts CAD using your saved exchange-rate assumption.</div>
          </div>
          <form id="quickCashForm">
            <div class="cash-balance-entry">
              <div><label for="quickCashAmount">Cash amount</label><input id="quickCashAmount" type="number" step="0.01" inputmode="decimal" /></div>
              <div><label for="quickCashCurrency">Currency</label><select id="quickCashCurrency"><option value="USD">USD</option><option value="CAD">CAD</option></select></div>
              <button class="btn" type="submit">Update cash</button>
            </div>
            <div class="cash-equivalent" id="currentCashEquivalent"></div>
          </form>
        </div>
      </div>
      <div class="grid cards">"""
html = replace_once(html, dashboard_old, dashboard_new, 'dashboard cash entry')

# Settings entry keeps the same internal USD balance but lets the user choose the input/display currency.
settings_old = """            <div><label>Starting available cash</label><input id="startingCash" type="number" step="0.01" /></div>
            <div><label>CAD per USD</label><input id="cadPerUsd" type="number" step="0.0001" /></div>"""
settings_new = """            <div><label>Current / starting cash balance</label><input id="startingCash" type="number" step="0.01" inputmode="decimal" /><div class="cash-field-note">Opening cash available on the forecast start date.</div><div class="cash-equivalent" id="startingCashEquivalent"></div></div>
            <div><label>Cash balance currency</label><select id="startingCashCurrency"><option value="USD">USD</option><option value="CAD">CAD</option></select><div class="cash-field-note">CAD is converted to USD for all calculations.</div></div>
            <div><label>CAD per USD</label><input id="cadPerUsd" type="number" step="0.0001" /></div>"""
html = replace_once(html, settings_old, settings_new, 'settings cash currency field')

# Backward-compatible state field. Existing balances remain USD and existing plans default to USD display.
default_old = """      targetDate: '2026-08-31',
      startingCash: 0,
      cadPerUsd: 1.42,"""
default_new = """      targetDate: '2026-08-31',
      startingCash: 0,
      startingCashCurrency: 'USD',
      cadPerUsd: 1.42,"""
html = replace_once(html, default_old, default_new, 'starting cash currency default')

# Currency helpers. startingCash remains normalized in USD so every existing forecast calculation stays correct.
helper_old = """  function loadState() {
"""
helper_new = """  function cashCurrencyOf(settings=state?.settings||defaultState.settings) {
    return settings?.startingCashCurrency==='CAD'?'CAD':'USD';
  }
  function cashAmountToUSD(amount,currency,rate=state?.settings?.cadPerUsd||defaultState.settings.cadPerUsd) {
    const value=Number(amount)||0;
    const fx=Math.max(.000001,Number(rate)||1.42);
    return currency==='CAD'?value/fx:value;
  }
  function cashAmountFromUSD(amountUSD,currency,rate=state?.settings?.cadPerUsd||defaultState.settings.cadPerUsd) {
    const value=Number(amountUSD)||0;
    const fx=Math.max(.000001,Number(rate)||1.42);
    return currency==='CAD'?value*fx:value;
  }
  function roundedCashInput(value) {
    return Number((Number(value)||0).toFixed(2));
  }
  function cashEquivalentLabel(amount,currency,rate) {
    const usd=cashAmountToUSD(amount,currency,rate);
    const fx=Math.max(.000001,Number(rate)||1.42);
    return currency==='CAD'
      ? `${money2(usd,'USD')} used as the opening USD balance`
      : `${money2(usd*fx,'CAD')} equivalent at C$${fx.toFixed(4)} per US$1`;
  }
  function convertCashEntry(amountElement,currencyElement,rate) {
    const previous=currencyElement.dataset.previousCurrency||'USD';
    const next=currencyElement.value==='CAD'?'CAD':'USD';
    const usd=cashAmountToUSD(amountElement.value,previous,rate);
    amountElement.value=roundedCashInput(cashAmountFromUSD(usd,next,rate));
    currencyElement.dataset.previousCurrency=next;
  }
  function refreshCashEquivalentLabels() {
    const quickAmount=document.getElementById('quickCashAmount');
    const quickCurrency=document.getElementById('quickCashCurrency');
    if(quickAmount&&quickCurrency)document.getElementById('currentCashEquivalent').textContent=cashEquivalentLabel(quickAmount.value,quickCurrency.value,state.settings.cadPerUsd);
    const settingsAmount=document.getElementById('startingCash');
    const settingsCurrency=document.getElementById('startingCashCurrency');
    const settingsRate=document.getElementById('cadPerUsd');
    if(settingsAmount&&settingsCurrency&&settingsRate)document.getElementById('startingCashEquivalent').textContent=cashEquivalentLabel(settingsAmount.value,settingsCurrency.value,settingsRate.value);
  }

  function loadState() {
"""
html = replace_once(html, helper_old, helper_new, 'cash currency helpers')

# Populate both the dashboard quick entry and the settings fields from the normalized USD balance.
render_settings_old = """  function renderSettings() {
    const s=state.settings;
    document.getElementById('forecastStart').value=s.forecastStart;document.getElementById('targetDate').value=s.targetDate;document.getElementById('startingCash').value=s.startingCash;document.getElementById('cadPerUsd').value=s.cadPerUsd;document.getElementById('payPeriods').value=s.payPeriods;document.getElementById('standardDeduction').value=s.standardDeduction;document.getElementById('ssRate').value=s.ssRate;document.getElementById('medicareRate').value=s.medicareRate;document.getElementById('ssWageBase').value=s.ssWageBase;document.getElementById('stateTaxRate').value=s.stateTaxRate;document.getElementById('supplementalRate').value=s.supplementalRate;
  }"""
render_settings_new = """  function renderSettings() {
    const s=state.settings;
    const currency=cashCurrencyOf(s);
    const displayAmount=roundedCashInput(cashAmountFromUSD(s.startingCash,currency,s.cadPerUsd));
    document.getElementById('forecastStart').value=s.forecastStart;
    document.getElementById('targetDate').value=s.targetDate;
    document.getElementById('startingCash').value=displayAmount;
    document.getElementById('startingCashCurrency').value=currency;
    document.getElementById('startingCashCurrency').dataset.previousCurrency=currency;
    document.getElementById('cadPerUsd').value=s.cadPerUsd;
    document.getElementById('payPeriods').value=s.payPeriods;
    document.getElementById('standardDeduction').value=s.standardDeduction;
    document.getElementById('ssRate').value=s.ssRate;
    document.getElementById('medicareRate').value=s.medicareRate;
    document.getElementById('ssWageBase').value=s.ssWageBase;
    document.getElementById('stateTaxRate').value=s.stateTaxRate;
    document.getElementById('supplementalRate').value=s.supplementalRate;
    refreshCashEquivalentLabels();
  }"""
html = replace_once(html, render_settings_old, render_settings_new, 'render cash currency settings')

# Dashboard render: keep the quick controls synchronized and explain the selected entry currency.
dashboard_render_old = """  function renderDashboard() {
    const s=getSummary();
    const cashEl=document.getElementById('cashTarget');"""
dashboard_render_new = """  function renderDashboard() {
    const s=getSummary();
    const openingCurrency=cashCurrencyOf();
    const openingDisplay=roundedCashInput(cashAmountFromUSD(state.settings.startingCash,openingCurrency,state.settings.cadPerUsd));
    document.getElementById('quickCashAmount').value=openingDisplay;
    document.getElementById('quickCashCurrency').value=openingCurrency;
    document.getElementById('quickCashCurrency').dataset.previousCurrency=openingCurrency;
    refreshCashEquivalentLabels();
    const cashEl=document.getElementById('cashTarget');"""
html = replace_once(html, dashboard_render_old, dashboard_render_new, 'render dashboard cash controls')

cash_detail_old = """    document.getElementById('cashTargetDetail').textContent=`Spendable cash only · starting cash ${money(state.settings.startingCash)} · ${fmtDate(state.settings.targetDate)}`;"""
cash_detail_new = """    document.getElementById('cashTargetDetail').textContent=`Spendable cash only · opening cash ${money(state.settings.startingCash)} USD${openingCurrency==='CAD'?` (entered as ${money2(openingDisplay,'CAD')})`:''} · ${fmtDate(state.settings.targetDate)}`;"""
html = replace_once(html, cash_detail_old, cash_detail_new, 'dashboard opening cash detail')

# Save from Settings: convert the selected currency to normalized USD using the rate entered on the same form.
settings_submit_old = """  document.getElementById('settingsForm').addEventListener('submit',e=>{e.preventDefault();state.settings={forecastStart:forecastStart.value,targetDate:targetDate.value,startingCash:Number(startingCash.value)||0,cadPerUsd:Number(cadPerUsd.value)||1.42,payPeriods:Number(payPeriods.value)||26,standardDeduction:Number(standardDeduction.value)||16100,ssRate:Number(ssRate.value)||0,medicareRate:Number(medicareRate.value)||0,ssWageBase:Number(ssWageBase.value)||184500,stateTaxRate:Number(stateTaxRate.value)||0,supplementalRate:Number(supplementalRate.value)||22};renderAll();});"""
settings_submit_new = """  document.getElementById('settingsForm').addEventListener('submit',e=>{e.preventDefault();const rate=Number(cadPerUsd.value)||1.42;const currency=startingCashCurrency.value==='CAD'?'CAD':'USD';state.settings={forecastStart:forecastStart.value,targetDate:targetDate.value,startingCash:cashAmountToUSD(startingCash.value,currency,rate),startingCashCurrency:currency,cadPerUsd:rate,payPeriods:Number(payPeriods.value)||26,standardDeduction:Number(standardDeduction.value)||16100,ssRate:Number(ssRate.value)||0,medicareRate:Number(medicareRate.value)||0,ssWageBase:Number(ssWageBase.value)||184500,stateTaxRate:Number(stateTaxRate.value)||0,supplementalRate:Number(supplementalRate.value)||22};renderAll();});"""
html = replace_once(html, settings_submit_old, settings_submit_new, 'save settings cash currency')

# Quick dashboard save and intuitive currency switching without changing the real USD value.
listener_old = """  document.getElementById('headerTarget').addEventListener('change',e=>{state.settings.targetDate=e.target.value;renderAll();});
  window.addEventListener('resize',"""
listener_new = """  document.getElementById('headerTarget').addEventListener('change',e=>{state.settings.targetDate=e.target.value;renderAll();});
  document.getElementById('quickCashForm').addEventListener('submit',e=>{e.preventDefault();const currency=quickCashCurrency.value==='CAD'?'CAD':'USD';state.settings.startingCash=cashAmountToUSD(quickCashAmount.value,currency,state.settings.cadPerUsd);state.settings.startingCashCurrency=currency;renderAll();});
  document.getElementById('quickCashCurrency').addEventListener('change',()=>{convertCashEntry(quickCashAmount,quickCashCurrency,state.settings.cadPerUsd);refreshCashEquivalentLabels();});
  document.getElementById('quickCashAmount').addEventListener('input',refreshCashEquivalentLabels);
  document.getElementById('startingCashCurrency').addEventListener('change',()=>{convertCashEntry(startingCash,startingCashCurrency,Number(cadPerUsd.value)||state.settings.cadPerUsd);refreshCashEquivalentLabels();});
  document.getElementById('startingCash').addEventListener('input',refreshCashEquivalentLabels);
  document.getElementById('cadPerUsd').addEventListener('input',refreshCashEquivalentLabels);
  window.addEventListener('resize',"""
html = replace_once(html, listener_old, listener_new, 'cash entry event listeners')

INDEX.write_text(html, encoding='utf-8')

old_cache = "const CACHE = 'financial-planner-secure-v11-vehicle-loan-term-fix';"
new_cache = "const CACHE = 'financial-planner-secure-v12-current-cash-currency';"
if new_cache not in service:
    if old_cache not in service:
        raise RuntimeError('Expected v11 service-worker cache marker was not found.')
    service = service.replace(old_cache, new_cache, 1)
    SW.write_text(service, encoding='utf-8')

print('Applied v12 current cash balance with USD/CAD entry and cloud-compatible storage.')
