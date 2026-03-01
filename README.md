# stocks-serverless-pipeline
Serverless AWS pipeline that tracks daily stock market movers and displays a 7-day history using Lambda, DynamoDB, and Terraform

# setup

## prerequisites
- Terraform >= 1.0 installed
- AWS CLI installed and configured (`aws configure`)
- Python 3.12
- A Massive API key (massiveapi.com)

## deploy
1. Clone the repo
```
   git clone https://github.com/AST103/stocks-serverless-pipeline
```

2. Go to the terraform directory
```
   cd terraform
```

3. Create a terraform.tfvars file (don't commit this)
```
   massive_api_key = "your_api_key_here"
   aws_region = "us-east-1"
```

4. Initialize and deploy
```
   terraform init
   terraform apply
```

5. Grab the API endpoint from the output
```
   api_endpoint = "https://xxxx.execute-api.us-east-1.amazonaws.com/prod/movers"
```

6. Update the API_URL in frontend/app.js with the endpoint from step 5

7. Deploy to S3

## tear down
```
   terraform destroy
```

# data architecture

# security
- API key stored as Terraform variable marked sensitive = true
- Never committed to GitHub
- Each Lambda has its own IAM role with least privilege permissions
- Ingestion Lambda: write-only to DynamoDB
- API Lambda: read-only from DynamoDB

# tech stack
- Terraform, AWS Lambda, AWS EventBridge, DynamoDB
- Massive API (real-time market data)

# features
- Automated daily analysis using EventBridge cron
- REST API returning last 7 days of top moving stocks
- Auto-backfill on first deploy so the dashboard is immediately useful
- Green/red color coded frontend showing gain vs loss
- Duplicate write protection so the same date is never overwritten

# backfilling logic
On first run (or if table has < 7 records), Lambda #1 automatically backfills historical data:
1. Checks DynamoDB record count
2. If < 7, fetches missing days using Daily Ticker Summary endpoint
3. Writes each day's winner to DynamoDB
4. Future runs execute normally with daily API endpoint

# data schema

# data schema
- `date` (String): Trading date in YYYY-MM-DD format (partition key)
- `ticker` (String): Stock symbol
- `percentChange` (Decimal): Percent change from open to close, signed for frontend use
- `closePrice` (Decimal): Closing price

# trade-offs and challenges 
  
Challenge: Free tier API limits ~5 requests/minute. 
Solution: Added 12-second delays between API calls to stay within limits.    
Trade-off: Backfill takes ~10 minutes but never fails due to rate limiting. 
 
Challenge: Empty dashboard on first deploy. 
Solution: Automatic backfill populates last 7 trading days on first run. 
Trade-off: First execution takes longer, but dashboard is immediately useful. 

Challenge: Market closed on weekends. 
Solution: Backfill checks weekday() and skips Saturdays/Sundays before making API calls. 
Trade-off: May look back 15 days to find 7 trading days, but saves wasted API calls.

Challenge: Determining best EventBridge schedule time given the API free tier limitations.
Solution: Runs at 12:30 AM PST TUES-SAT, when the free-tier API finishes processing the previous trading day's closing data.
Trade-off: Rather than being able to see update right after market close, you have to wait until at least 12:30 AM the next day or next morning.

Challenge: Two different endpoints needed. 
Solution: Use Daily Ticker Summary for backfill (specific dates), Previous Day Bar for daily runs (simpler). 
Trade-off: Slightly more complex code, but optimized for each use case. 

Challenge: Choosing DynamoDB partition key.
Solution: Used date as key since primary access pattern is "retrieve last 7 days." Trade-off: Can't efficiently query "all TSLA history," but that's not a requirement.

Challenge: Simplified deployment for others. 
Solution: Removed AWS profile requirement—uses default credential
Trade-off: Less control over AWS account selection, but drastically simpler setup.