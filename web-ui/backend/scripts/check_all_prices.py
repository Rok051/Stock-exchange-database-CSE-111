import sys
sys.path.insert(0, '.')
from database import execute_query

securities = execute_query('SELECT security_id, ticker FROM Security')
prices = execute_query('SELECT DISTINCT security_id FROM DailyPrice')
price_ids = {p['security_id'] for p in prices}
missing = [s['ticker'] for s in securities if s['security_id'] not in price_ids]

print(f'Total securities: {len(securities)}')
print(f'Securities with price data: {len(price_ids)}')
print(f'Securities WITHOUT price data: {len(missing)}')
if missing:
    print(f'Missing: {", ".join(missing)}')
else:
    print('✅ All stocks have price data!')
