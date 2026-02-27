# create a zip file from lambda code
data "archive_file" "ingestion_lambda_zip" {
    type        = "zip"
    source_dir  = "${path.module}/../src/ingestion"
    output_path = "${path.module}/ingestion_lambda.zip"
}

# create the lambda function
resource "aws_lambda_function" "ingestion_lambda" {
    function_name = "stock-winners-ingestion-lambda"
    role          = aws_iam_role.lambda_execution_role.arn
    handler       = "lambda_function.lambda_handler"
    runtime       = "python3.12"
    filename      = data.archive_file.ingestion_lambda_zip.output_path
    source_code_hash = data.archive_file.ingestion_lambda_zip.output_base64sha256
    timeout = 900  # set timeout to 60 seconds to give it enough time to fetch data and write to DynamoDB
    memory_size = 256
    layers = ["arn:aws:lambda:us-east-1:770693421928:layer:Klayers-p312-requests:21"]  # add the requests layer to the Lambda function
    environment {
        variables = {
            TABLE_NAME = aws_dynamodb_table.stock_winners.name,
            MASSIVE_API_KEY = var.massive_api_key
        }
    }
}   

# still need to add second lambda function for API endpoint, but will do that in a future iteration since it's not strictly necessary for the core pipeline functionality and I want to get something working end-to-end first before adding more features