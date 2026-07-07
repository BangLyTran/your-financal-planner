from pathlib import Path

INDEX = Path('index.html')
SW = Path('service-worker.js')
html = INDEX.read_text(encoding='utf-8')
service = SW.read_text(encoding='utf-8')

if 'id="financialAssetsBeforeDebt"' in html and 'financial-planner-secure-v13-financial-assets-bridge' in service:
    print('v13 financial-assets bridge is already applied.')
    raise SystemExit(0)


def replace_once(text: str, old: str, new: str, label: str) -> str:
    count = text.count(old)
    if count != 1:
        raise RuntimeError(f'{label}: expected exactly one match, found {count}')
    return text.replace(old, new, 1)

# Add a prominent bridge between gross financial assets and after-debt net position.
css_old = """    .cash-equivalent { margin-top:7px; color:#1e40af; font-size:.8rem; font-weight:750; }
    .cash-field-note { margin-top:5px; color:var(--muted); font-size:.76rem; line-height:1.4; }

    @media (max-width: 1100px) {"""
css_new = """    .cash-equivalent { margin-top:7px; color:#1e40af; font-size:.8rem; font-weight:750; }
    .cash-field-note { margin-top:5px; color:var(--muted); font-size:.76rem; line-height:1.4; }
    .wealth-overview-panel { margin-bottom:16px; border-color:#a7f3d0; background:linear-gradient(135deg,#ecfdf5 0%,#ffffff 58%,#eff6ff 100%); }
    .wealth-overview-head { display:flex; justify-content:space-between; align-items:flex-start; gap:20px; flex-wrap:wrap; }
    .wealth-overview-main { min-width:250px; }
    .wealth-overview-main .label { color:#047857; font-size:.8rem; font-weight:800; text-transform:uppercase; letter-spacing:.045em; }
    .wealth-overview-value { margin-top:7px; font-size:clamp(2rem,4.2vw,3.35rem); line-height:1; font-weight:900; color:#047857; letter-spacing:-.035em; }
    .wealth-overview-detail { margin-top:9px; color:#475569; font-size:.88rem; line-height:1.45; }
    .wealth-principal-note { max-width:420px; padding:11px 13px; border:1px solid #bfdbfe; border-radius:12px; background:rgba(239,246,255,.8); color:#1e3a8a; font-size:.8rem; line-height:1.45; }
    .wealth-overview-grid { display:grid; grid-template-columns:repeat(4,minmax(150px,1fr)); gap:10px; margin-top:17px; }
    .wealth-mini { padding:12px 13px; border:1px solid rgba(148,163,184,.35); border-radius:12px; background:rgba(255,255,255,.82); }
    .wealth-mini span { display:block; color:var(--muted); font-size:.73rem; font-weight:800; text-transform:uppercase; letter-spacing:.035em; }
    .wealth-mini strong { display:block; margin-top:5px; font-size:1.08rem; font-weight:850; }
    .wealth-mini.asset { border-color:#a7f3d0; background:#f0fdf4; }
    .wealth-mini.debt { border-color:#fed7aa; background:#fff7ed; }
    .wealth-mini.net { border-color:#bfdbfe; background:#eff6ff; }
    .wealth-equation { margin-top:12px; padding-top:11px; border-top:1px dashed #94a3b8; color:#334155; font-size:.82rem; line-height:1.5; }

    @media (max-width: 1100px) {"""
html = replace_once(html, css_old, css_new, 'financial assets bridge CSS')

responsive_old = """      .cash-balance-layout { grid-template-columns:1fr; }
      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
responsive_new = """      .cash-balance-layout { grid-template-columns:1fr; }
      .wealth-overview-grid { grid-template-columns:repeat(2,minmax(150px,1fr)); }
      .debt-deadline-grid { grid-template-columns:repeat(2,minmax(0,1fr)); }"""
html = replace_once(html, responsive_old, responsive_new, 'bridge responsive layout')

mobile_old = """      .cash-balance-entry { grid-template-columns:1fr; }
      .target-box { width: 100%; }"""
mobile_new = """      .cash-balance-entry { grid-template-columns:1fr; }
      .wealth-overview-grid { grid-template-columns:1fr; }
      .wealth-overview-value { font-size:2.25rem; }
      .target-box { width: 100%; }"""
html = replace_once(html, mobile_old, mobile_new, 'bridge mobile layout')

# Insert the bridge immediately below the current-cash entry and above the legacy KPI cards.
insert_old = """            <div class="cash-equivalent" id="currentCashEquivalent"></div>
          </form>
        </div>
      </div>
      <div class="grid cards">"""
insert_new = """            <div class="cash-equivalent" id="currentCashEquivalent"></div>
          </form>
        </div>
      </div>
      <div class="panel wealth-overview-panel" id="financialAssetsOverview">
        <div class="wealth-overview-head">
          <div class="wealth-overview-main">
            <div class="label">Financial assets before debt</div>
            <div class="wealth-overview-value" id="financialAssetsBeforeDebt">$0.00</div>
            <div class="wealth-overview-detail" id="financialAssetsBeforeDebtDetail">Spendable cash plus projected investments, before subtracting debt.</div>
          </div>
          <div class="wealth-principal-note" id="principalFinancialAssets">Principal-only assets will appear here.</div>
        </div>
        <div class="wealth-overview-grid">
          <div class="wealth-mini"><span>Spendable cash</span><strong id="wealthBridgeCash">$0.00</strong></div>
          <div class="wealth-mini asset"><span>Projected investments</span><strong id="wealthBridgeInvestments">$0.00</strong></div>
          <div class="wealth-mini debt"><span>Debt at target</span><strong id="wealthBridgeDebt">$0.00</strong></div>
          <div class="wealth-mini net"><span>After-debt net position</span><strong id="wealthBridgeNet">$0.00</strong></div>
        </div>
        <div class="wealth-equation" id="wealthBridgeEquation"></div>
      </div>
      <div class="grid cards">"""
html = replace_once(html, insert_old, insert_new, 'financial assets bridge HTML')

# Clarify that the old cash KPI excludes investments, and make the net-position explanation dynamic.
html = replace_once(
    html,
    '<div class="label">Cash on target date</div>',
    '<div class="label">Spendable cash at target</div>',
    'cash KPI label',
)
html = replace_once(
    html,
    '<div class="detail">Liquid cash + projected investments − debt</div>',
    '<div class="detail" id="netPositionDetail">Financial assets − debt</div>',
    'net position detail id',
)

# Render both before-debt financial assets and the after-debt result using the same investment assumptions.
render_old = """    refreshCashEquivalentLabels();
    const cashEl=document.getElementById('cashTarget');"""
render_new = """    refreshCashEquivalentLabels();
    const medianInvestment=Number(s.investmentProjection.endingMedianInvestment)||0;
    const principalInvestment=Number(s.investmentProjection.endingPrincipalInvestment)||0;
    const financialAssets=s.cash+medianInvestment;
    const principalAssets=s.cash+principalInvestment;
    const netFinancialPosition=financialAssets-s.totalDebt;
    document.getElementById('financialAssetsBeforeDebt').textContent=money2(financialAssets);
    document.getElementById('financialAssetsBeforeDebtDetail').textContent=`${money2(s.cash)} spendable cash + ${money2(medianInvestment)} median projected investments. Debt has not been deducted.`;
    document.getElementById('principalFinancialAssets').innerHTML=`<strong>Principal-only view: ${money2(principalAssets)}</strong><br>${money2(s.cash)} cash + ${money2(principalInvestment)} contributed investment principal, before market growth and before debt.`;
    document.getElementById('wealthBridgeCash').textContent=money2(s.cash);
    document.getElementById('wealthBridgeInvestments').textContent=money2(medianInvestment);
    document.getElementById('wealthBridgeDebt').textContent=money2(s.totalDebt);
    const bridgeNet=document.getElementById('wealthBridgeNet');
    bridgeNet.textContent=money2(netFinancialPosition);
    bridgeNet.className=netFinancialPosition>=0?'positive':'negative';
    document.getElementById('wealthBridgeEquation').innerHTML=`<strong>${money2(s.cash)} cash + ${money2(medianInvestment)} investments = ${money2(financialAssets)} financial assets before debt.</strong> Subtracting ${money2(s.totalDebt)} of debt produces an after-debt net financial position of ${money2(netFinancialPosition)}.`;
    const cashEl=document.getElementById('cashTarget');"""
html = replace_once(html, render_old, render_new, 'financial assets render logic')

np_old = """    const np=s.cash+s.investmentProjection.endingMedianInvestment-s.totalDebt;
    const npEl=document.getElementById('netPosition'); npEl.textContent=money(np); npEl.className=`value ${np>=0?'positive':'negative'}`;"""
np_new = """    const np=netFinancialPosition;
    const npEl=document.getElementById('netPosition'); npEl.textContent=money(np); npEl.className=`value ${np>=0?'positive':'negative'}`;
    document.getElementById('netPositionDetail').textContent=`${money(financialAssets)} financial assets − ${money(s.totalDebt)} debt`;"""
html = replace_once(html, np_old, np_new, 'net position bridge calculation')

# Add the gross financial-assets figure to the planning snapshot as well.
snapshot_old = """      <div class="metric-row"><span>Projected investment value</span><strong class="investment-value">${money(s.investmentProjection.endingMedianInvestment)}</strong></div>
      <div class="metric-row"><span>Savings target funded</span><strong>${s.savingsProjection.totalTarget>0?Math.round(s.savingsProjection.totalContributed/s.savingsProjection.totalTarget*100):0}%</strong></div>"""
snapshot_new = """      <div class="metric-row"><span>Projected investment value</span><strong class="investment-value">${money(s.investmentProjection.endingMedianInvestment)}</strong></div>
      <div class="metric-row"><span>Financial assets before debt</span><strong class="positive">${money(financialAssets)}</strong></div>
      <div class="metric-row"><span>Savings target funded</span><strong>${s.savingsProjection.totalTarget>0?Math.round(s.savingsProjection.totalContributed/s.savingsProjection.totalTarget*100):0}%</strong></div>"""
html = replace_once(html, snapshot_old, snapshot_new, 'planning snapshot assets row')

INDEX.write_text(html, encoding='utf-8')

old_cache = "const CACHE = 'financial-planner-secure-v12-current-cash-currency';"
new_cache = "const CACHE = 'financial-planner-secure-v13-financial-assets-bridge';"
if new_cache not in service:
    if old_cache not in service:
        raise RuntimeError('Expected v12 service-worker cache marker was not found.')
    service = service.replace(old_cache, new_cache, 1)
    SW.write_text(service, encoding='utf-8')

print('Applied v13 financial-assets-before-debt overview and bridge.')
