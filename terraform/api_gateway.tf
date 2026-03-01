# container for the API
resource "aws_api_gateway_rest_api" "movers_api" {
  name        = "movers-api"
  description = "API for fetching stock movers data"
}

# define a path segment /movers
resource "aws_api_gateway_resource" "movers_resource" {
  rest_api_id = aws_api_gateway_rest_api.movers_api.id
  parent_id   = aws_api_gateway_rest_api.movers_api.root_resource_id
  path_part   = "movers"
}

# define the HTTP verb (GET) for the /movers path
resource "aws_api_gateway_method" "get_movers" {
  rest_api_id   = aws_api_gateway_rest_api.movers_api.id
  resource_id   = aws_api_gateway_resource.movers_resource.id
  http_method   = "GET"
  authorization = "NONE"
}

# connects the method to the lambda function
resource "aws_api_gateway_integration" "get_movers_integration" {
  rest_api_id = aws_api_gateway_rest_api.movers_api.id
  resource_id = aws_api_gateway_resource.movers_resource.id
  http_method = aws_api_gateway_method.get_movers.http_method

  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = aws_lambda_function.api_lambda.invoke_arn
}

# allow lambda to be invoked by API Gateway
resource "aws_lambda_permission" "allow_api_gateway" {
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.api_lambda.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "${aws_api_gateway_rest_api.movers_api.execution_arn}/*/*"
}

# captures current state of API to make it callable
resource "aws_api_gateway_deployment" "movers_api_deployment" {
  depends_on  = [aws_api_gateway_integration.get_movers_integration]
  rest_api_id = aws_api_gateway_rest_api.movers_api.id

  # this is important to force redeployment when API changes, 
  # otherwise we'd have to manually redeploy from AWS console after every change

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_rest_api.movers_api,
      aws_api_gateway_resource.movers_resource,
      aws_api_gateway_method.get_movers,
      aws_api_gateway_integration.get_movers_integration
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}

# creates a named environment for deployment
resource "aws_api_gateway_stage" "prod" {
  stage_name    = "prod"
  rest_api_id   = aws_api_gateway_rest_api.movers_api.id
  deployment_id = aws_api_gateway_deployment.movers_api_deployment.id
}
