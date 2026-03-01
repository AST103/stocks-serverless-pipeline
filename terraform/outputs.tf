# outputs is important or else we'd have to go to AWS console to check for 
# the created resources and their ARNs, which we need for the event bridge setup

output "dynamodb_table_name" {
  description = "The name of the DynamoDB table"
  value       = aws_dynamodb_table.stock_winners.name
}

output "lambda_function_name" {
  description = "The name of the Lambda function"
  value       = aws_lambda_function.ingestion_lambda.function_name
}

output "eventbridge_rule_name" {
  description = "The name of the EventBridge rule"
  value       = aws_cloudwatch_event_rule.stock_check.name
}

output "lambda_execution_role_arn" {
  description = "The ARN of the Lambda execution role"
  value       = aws_iam_role.lambda_execution_role.arn
}

output "lambda_function_arn" {
  description = "The ARN of the Lambda function"
  value       = aws_lambda_function.ingestion_lambda.arn
}

output "api_endpoint" {
  description = "The API Gateway endpoint for the API Lambda function"
  value       = "${aws_api_gateway_stage.prod.invoke_url}/movers"
}
