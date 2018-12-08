# dash-ticker
Web App project to display stock ticker information via Dash.
Milestone for The Data Incubator 12 Day Program.

Features:
- Retreives historic stock price using the [AlphaVantage API](https://www.alphavantage.co/documentation/)
- Search for stocks via search box with autocomplete
- Caching with expiry to Redis cache on Heroku to reduce the number of API calls (and stay within the 5 calls per minute API restriction)
- Display multiple stocks in chart
- Table of stock prices
