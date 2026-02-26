# stocks-serverless-pipeline
Serverless AWS pipeline that tracks daily stock market movers and displays a 7-day history using Lambda, DynamoDB, and Terraform

# setup

# data architecture

# tech Stack
- Terraform, AWS Lambda, AWS EventBridge, DynamoDB
- Massive API (real-time market data)

# features
- REST API returning last 7 days of stocks with highest % change


# backfilling logic
On first run (or if table has < 7 records), Lambda #1 automatically backfills historical data:
1. Checks DynamoDB record count
2. If < 7, fetches missing days using Daily Ticker Summary endpoint
3. Writes each day's winner to DynamoDB
4. Future runs execute normally with daily API endpoint

# data schema

Each DynamoDB record contains:
date (String): Trading date in YYYY-MM-DD format (also the partition key)
ticker (String): Stock symbol
percentChange (Decimal): Percent change from open to close with its sign for frontend use
closePrice (Decimal): Closing price