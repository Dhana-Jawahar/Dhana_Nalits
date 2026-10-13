# Yahoo Finance field dictionary
| Field | Meaning |
|-------|--------|
| price | Last / regular market price |
| shares_outstanding | Shares currently outstanding |
| market_cap | Approx. price × shares |
| trailing_pe | Price / trailing EPS |
| volume | Shares traded today |
| fifty_two_week_* | 52-week low / high |
| sector / industry | Company classification |
## Notes- Some fields can be null (ETFs, new listings).- Prefer script output over memorized numbers.- Check currency for non-US tickers.