from pathlib import Path

INDEX = Path('index.html')
SERVICE_WORKER = Path('service-worker.js')

html = INDEX.read_text(encoding='utf-8')
service_worker = SERVICE_WORKER.read_text(encoding='utf-8')

marker = 'vehicleLoanPaymentNumber:installment+1'
if marker in html:
    print('Vehicle loan term fix is already applied.')
else:
    old = """    if (v.firstPaymentDate) {
      const paymentItem={active:true,startDate:v.firstPaymentDate,endDate:'',recurrence:'monthly'};
      generateDates(paymentItem,targetDate).forEach(date=>events.push({date,name:'GLE loan payment',type:'Vehicle',amountUSD:-calc.payment,source:'vehicle'}));
    }
"""
    new = """    if (v.firstPaymentDate) {
      const termMonths=Math.max(0,Math.floor(Number(v.termMonths)||0));
      const firstPayment=parseDate(v.firstPaymentDate);
      for(let installment=0;installment<termMonths;installment++){
        const paymentDate=addMonths(firstPayment,installment);
        if(paymentDate>target)break;
        if(paymentDate<start)continue;
        events.push({
          date:toISO(paymentDate),
          name:'GLE loan payment',
          type:'Vehicle',
          amountUSD:-calc.payment,
          source:'vehicle',
          vehicleLoanPaymentNumber:installment+1,
          vehicleLoanTermMonths:termMonths
        });
      }
    }
"""
    count = html.count(old)
    if count != 1:
        raise RuntimeError(f'Expected one open-ended vehicle-loan schedule block, found {count}.')
    html = html.replace(old, new, 1)
    INDEX.write_text(html, encoding='utf-8')
    print('Applied exact vehicle-loan installment limit.')

old_cache = "const CACHE = 'financial-planner-secure-v10-monthly-allocation-pie';"
new_cache = "const CACHE = 'financial-planner-secure-v11-vehicle-loan-term-fix';"
if new_cache not in service_worker:
    if old_cache not in service_worker:
        raise RuntimeError('Could not find the expected v10 service-worker cache marker.')
    service_worker = service_worker.replace(old_cache, new_cache, 1)
    SERVICE_WORKER.write_text(service_worker, encoding='utf-8')
    print('Updated service-worker cache to v11.')
