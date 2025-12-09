import sys
sys.path.insert(0, '.')
from database import execute_query

prices = execute_query("""
    SELECT s.ticker, dp.close, dp.price_date
    FROM Security s 
    JOIN DailyPrice dp ON s.security_id = dp.security_id 
    WHERE s.ticker IN ('AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN')
    AND dp.price_date = (SELECT MAX(price_date) FROM DailyPrice WHERE security_id = s.security_id)
""")

print('Latest prices:')
for p in prices:
    print(f"  {p['ticker']}: ${p['close']:.2f} (date: {p['price_date']})")
