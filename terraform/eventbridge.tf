# Create an EventBridge rule to trigger the Lambda function on a schedule
resource "aws_cloudwatch_event_rule" "stock_check" {
    name                = "stock-check-schedule"
    description         = "Triggers the stock winners ingestion Lambda daily"
    schedule_expression = "cron(30 21 ? * MON-FRI *)"  
}

# Create the event bridge target to link the rule to the Lambda function
resource "aws_cloudwatch_event_target" "stock_check_target" {
    rule      = aws_cloudwatch_event_rule.stock_check.name
    target_id = "IngestStockData"
    arn       = aws_lambda_function.ingestion_lambda.arn
}

# allow event bridge to invoke the lambda function
resource "aws_lambda_permission" "allow_eventbridge" {
    statement_id  = "AllowExecutionFromEventBridge"
    action        = "lambda:InvokeFunction"
    function_name = aws_lambda_function.ingestion_lambda.function_name
    principal     = "events.amazonaws.com"
    source_arn    = aws_cloudwatch_event_rule.stock_check.arn
}