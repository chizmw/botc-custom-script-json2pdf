# https://mrponath.medium.com/terraform-and-aws-api-gateway-a137ee48a8ac

locals {
  pdf_api_name        = "pdf-api"
  pdf_api_description = "JSON-to-PDF API for custom BotC scripts"
  pdf_render_path     = "render"
  api_stage           = (terraform.workspace == "prod") ? "prod" : "dev"
  python_runtime      = "python3.10"
}

# SETUP and "OPTIONS

resource "aws_api_gateway_rest_api" "cors_api" {
  provider    = aws.default
  name        = local.pdf_api_name
  description = local.pdf_api_description
}

resource "aws_api_gateway_resource" "cors_resource" {
  provider    = aws.default
  path_part   = local.pdf_render_path
  parent_id   = aws_api_gateway_rest_api.cors_api.root_resource_id
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
}

resource "aws_api_gateway_method" "options_method" {
  provider      = aws.default
  rest_api_id   = aws_api_gateway_rest_api.cors_api.id
  resource_id   = aws_api_gateway_resource.cors_resource.id
  http_method   = "OPTIONS"
  authorization = "NONE"
}

resource "aws_api_gateway_method_response" "options_200" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  resource_id = aws_api_gateway_resource.cors_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = 200
  response_models = {
    "application/json" = "Empty"
  }
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = true,
    "method.response.header.Access-Control-Allow-Methods" = true,
    "method.response.header.Access-Control-Allow-Origin"  = true
  }
  depends_on = [aws_api_gateway_method.options_method]
}

resource "aws_api_gateway_integration" "options_integration" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  resource_id = aws_api_gateway_resource.cors_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  type        = "MOCK"
  depends_on  = [aws_api_gateway_method.options_method]
  request_templates = {
    "application/json" = jsonencode(
      {
        statusCode = 200
      }
    )
  }
}

resource "aws_api_gateway_integration_response" "options_integration_response" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  resource_id = aws_api_gateway_resource.cors_resource.id
  http_method = aws_api_gateway_method.options_method.http_method
  status_code = aws_api_gateway_method_response.options_200.status_code
  response_parameters = {
    "method.response.header.Access-Control-Allow-Headers" = "'X-Chisel-Info,access-control-allow-origin,cache-control,x-requested-with,Content-Type,X-Amz-Date,Authorization,X-Api-Key,X-Amz-Security-Token'",
    "method.response.header.Access-Control-Allow-Methods" = "'OPTIONS,POST'",
    "method.response.header.Access-Control-Allow-Origin"  = "'*'"
  }
  depends_on = [aws_api_gateway_method_response.options_200]
}

# POST method

# a request validator is required for API Gateway to accept the request body
resource "aws_api_gateway_request_validator" "cors_request_validator" {
  provider                    = aws.default
  name                        = "cors_request_validator"
  rest_api_id                 = aws_api_gateway_rest_api.cors_api.id
  validate_request_body       = true
  validate_request_parameters = false
}

resource "aws_api_gateway_method" "cors_method" {
  provider         = aws.default
  rest_api_id      = aws_api_gateway_rest_api.cors_api.id
  resource_id      = aws_api_gateway_resource.cors_resource.id
  http_method      = "POST"
  authorization    = "NONE"
  api_key_required = true
  # I know, hard coded is bad; we'll come back to this
  # just wanted to get past this:
  #     - request_validator_id = "io70c1" -> null
  request_validator_id = "io70c1"
}

resource "aws_api_gateway_method_response" "cors_method_response_200" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  resource_id = aws_api_gateway_resource.cors_resource.id
  http_method = aws_api_gateway_method.cors_method.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  depends_on = [aws_api_gateway_method.cors_method]
}

resource "aws_api_gateway_integration" "integration" {
  provider                = aws.default
  rest_api_id             = aws_api_gateway_rest_api.cors_api.id
  resource_id             = aws_api_gateway_resource.cors_resource.id
  http_method             = aws_api_gateway_method.cors_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:${var.aws_region}:lambda:path/2015-03-31/functions/${aws_lambda_function.lambda.arn}/invocations"
  depends_on              = [aws_api_gateway_method.cors_method, aws_lambda_function.lambda]
}

resource "aws_api_gateway_deployment" "deployment" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  stage_name  = local.api_stage
  depends_on = [
    aws_api_gateway_gateway_response.cors_gateway_response,
    aws_api_gateway_integration.integration,
    aws_api_gateway_integration.options_integration,
    aws_api_gateway_integration_response.options_integration_response,
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_gateway_response.cors_gateway_response.id,
      aws_api_gateway_integration.integration.id,
      aws_api_gateway_integration.options_integration.id,
      aws_api_gateway_integration_response.options_integration_response.id,
      aws_api_gateway_integration_response.options_integration_response.response_templates,
      aws_api_gateway_integration_response.options_integration_response.response_parameters,
    ]))
  }
}

resource "aws_lambda_permission" "apigw_lambda" {
  provider      = aws.default
  statement_id  = "AllowExecutionFromAPIGateway"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.lambda.arn
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:execute-api:${var.aws_region}:123456789012:${aws_api_gateway_rest_api.cors_api.id}/*/${aws_api_gateway_method.cors_method.http_method}/${local.pdf_render_path}"
}

data "archive_file" "lambda" {
  type        = "zip"
  source_file = "main.py"
  output_path = "lambda_function_payload.zip"
}

resource "aws_lambda_function" "lambda" {
  provider         = aws.default
  filename         = data.archive_file.lambda.output_path
  function_name    = "API_GATEWAY_PREPROCESS"
  role             = data.aws_iam_role.iam_for_lambda.arn
  handler          = "main.lambda_handler"
  runtime          = local.python_runtime
  timeout          = 60
  source_code_hash = data.archive_file.lambda.output_base64sha256
}


# BLOODY CORS!

# we need a gateway reaponse for default 4xx responses that add the following
# header
# Access-Control-Allow-Origin: '*'
# https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
resource "aws_api_gateway_gateway_response" "cors_gateway_response" {
  provider    = aws.default
  rest_api_id = aws_api_gateway_rest_api.cors_api.id
  # this is the default 4xx response
  # https://docs.aws.amazon.com/apigateway/latest/developerguide/supported-gateway-response-types.html
  response_type = "DEFAULT_4XX"
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
    "gatewayresponse.header.X-Chisel-Info"               = "'DEFAULT_4XX from terraform'"
  }
  response_templates = {
    "application/json" = jsonencode({
      message = "DEFAULT_4XX from terraform"
    })
  }
  depends_on = [aws_api_gateway_rest_api.cors_api]
}
