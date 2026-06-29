from pathlib import Path

index=Path('index.html')
sw=Path('service-worker.js')
html=index.read_text(encoding='utf-8')

if 'financial-planner-secure-v8-1-savings-refinements' in sw.read_text(encoding='utf-8'):
    print('v8.1 refinements already applied.')
    raise SystemExit(0)

old="if(years>0&&cfg.enabled){"
new="if(years>0){"
if html.count(old)!=1:
    raise RuntimeError(f'investment growth match count: {html.count(old)}')
html=html.replace(old,new,1)

old="shiftedEnd=shiftIncomeDateOneYear(i.endDate||'',i.recurrence)"
new="shiftedEnd=i.endDate?toISO(addMonths(parseDate(i.endDate),12)):''"
if html.count(old)!=1:
    raise RuntimeError(f'income end-date match count: {html.count(old)}')
html=html.replace(old,new,1)

index.write_text(html,encoding='utf-8')
service=sw.read_text(encoding='utf-8')
service=service.replace("const CACHE = 'financial-planner-secure-v8-savings-investments';","const CACHE = 'financial-planner-secure-v8-1-savings-refinements';")
sw.write_text(service,encoding='utf-8')
print('Applied v8.1 savings refinements.')
