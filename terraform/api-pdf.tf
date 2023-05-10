# https://mrponath.medium.com/terraform-and-aws-api-gateway-a137ee48a8ac
# SETUP and "OPTIONS
data "aws_api_gateway_rest_api" "cors_api" {
  provider = aws.default
  name     = local.pdf_api_name
}

data "aws_api_gateway_resource" "cors_resource" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.cors_api.id
  path        = "/${local.pdf_render_path}"
}




# POST method

# a request validator is required for API Gateway to accept the request body
resource "aws_api_gateway_request_validator" "json2pdf_request_validator" {
  provider                    = aws.default
  name                        = "json2pdf_request_validator-${terraform.workspace}"
  rest_api_id                 = data.aws_api_gateway_rest_api.cors_api.id
  validate_request_body       = true
  validate_request_parameters = false
}



resource "aws_api_gateway_method" "cors_method" {
  provider             = aws.default
  rest_api_id          = data.aws_api_gateway_rest_api.cors_api.id
  resource_id          = data.aws_api_gateway_resource.cors_resource.id
  http_method          = "POST"
  authorization        = "NONE"
  api_key_required     = true
  request_validator_id = aws_api_gateway_request_validator.json2pdf_request_validator.id
}

resource "aws_api_gateway_method_response" "cors_method_response_200" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.cors_api.id
  resource_id = data.aws_api_gateway_resource.cors_resource.id
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
  rest_api_id             = data.aws_api_gateway_rest_api.cors_api.id
  resource_id             = data.aws_api_gateway_resource.cors_resource.id
  http_method             = aws_api_gateway_method.cors_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:436158765452:function:$${stageVariables.lambda}/invocations"
  depends_on              = [aws_api_gateway_method.cors_method, data.aws_lambda_function.api_render_pdf]
}


resource "aws_api_gateway_deployment" "deployment" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.cors_api.id
  stage_name  = local.api_stage

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    aws_api_gateway_gateway_response.cors_gateway_response,
    aws_api_gateway_gateway_response.cors_gateway_response,
    aws_api_gateway_integration.integration,
    #aws_api_gateway_integration.options_integration,
    #aws_api_gateway_integration_response.options_integration_response,
    data.external.poetry_version,
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_gateway_response.cors_gateway_response.id,
      aws_api_gateway_gateway_response.cors_gateway_response.response_templates,
      aws_api_gateway_integration.integration.id,
      aws_api_gateway_integration.integration.uri,
      #aws_api_gateway_integration.options_integration.id,
      #aws_api_gateway_integration_response.options_integration_response.id,
      #aws_api_gateway_integration_response.options_integration_response.response_parameters,
      #aws_api_gateway_integration_response.options_integration_response.response_templates,
      local.gatewayresponses,
      data.external.poetry_version.result.version,
    ]))
  }

  variables = {
    #"lambda_arn" = aws_lambda_function.lambda.arn
    "lambda" = local.lambda_stage_function_name
    "stage"  = local.api_stage
  }
}

# resource "aws_lambda_permission" "apigw_lambda" {
#   provider      = aws.default
#   statement_id  = "AllowExecutionFromAPIGateway"
#   action        = "lambda:InvokeFunction"
#   function_name = aws_lambda_function.lambda.arn
#   principal     = "apigateway.amazonaws.com"
#   source_arn    = "arn:aws:execute-api:${var.aws_region}:123456789012:${aws_api_gateway_rest_api.cors_api.id}/*/${aws_api_gateway_method.cors_method.http_method}/${local.pdf_render_path}"
# }

# resource "aws_lambda_function" "lambda" {
#   provider         = aws.default
#   filename         = data.archive_file.lambda.output_path
#   function_name    = "API_GATEWAY_PREPROCESS"
#   role             = data.aws_iam_role.iam_for_lambda.arn
#   handler          = "main.lambda_handler"
#   runtime          = local.python_runtime
#   timeout          = 60
#   source_code_hash = data.archive_file.lambda.output_base64sha256
# }


# BLOODY CORS!

# we need a gateway reaponse for default 4xx responses that add the following
# header
# Access-Control-Allow-Origin: '*'
# https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
resource "aws_api_gateway_gateway_response" "cors_gateway_response" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.cors_api.id
  # this is the default 4xx response
  # https://docs.aws.amazon.com/apigateway/latest/developerguide/supported-gateway-response-types.html
  response_type = "DEFAULT_4XX"
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
    "gatewayresponse.header.X-Chisel-Info"               = "'DEFAULT_4XX from terraform'"
  }
  response_templates = {
    "application/json" = jsonencode(
      { "error" : "a non-specific 4XX error has occurred", "chisel" : "was here" }
    )
  }
  depends_on = [data.aws_api_gateway_rest_api.cors_api]
}

locals {
  gatewayresponses = {
    "ACCESS_DENIED"                  = "The gateway response for authorization failure"
    "API_CONFIGURATION_ERROR"        = "The gateway response for invalid API configuration"
    "AUTHORIZER_CONFIGURATION_ERROR" = "The gateway response when the authorizer configuration is invalid"
    "AUTHORIZER_FAILURE"             = "The gateway response when a custom authorizer failed to authenticate the caller"
    "BAD_REQUEST_PARAMETERS"         = "The gateway response when request parameters are invalid"
    "BAD_REQUEST_BODY"               = "The gateway response when request body is invalid"
    "INVALID_API_KEY"                = "INVALID_API_KEY: check you correctly configured the API key in the source code"
    "MISSING_AUTHENTICATION_TOKEN"   = "The gateway response when the incoming request does not contain an authentication token"
  }

  status_codes = {
    "ACCESS_DENIED"                  = "403"
    "API_CONFIGURATION_ERROR"        = "500"
    "AUTHORIZER_CONFIGURATION_ERROR" = "500"
    "AUTHORIZER_FAILURE"             = "500"
    "BAD_REQUEST_PARAMETERS"         = "400"
    "BAD_REQUEST_BODY"               = "400"
    "INVALID_API_KEY"                = "403"
    "MISSING_AUTHENTICATION_TOKEN"   = "403"
  }
}

resource "aws_api_gateway_gateway_response" "cors_gateway_response_for" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.cors_api.id

  for_each = local.gatewayresponses

  # status_code is the lookup of the key in the local.status_codes map
  status_code = local.status_codes[each.key]

  response_type = each.key
  response_parameters = {
    "gatewayresponse.header.Access-Control-Allow-Origin" = "'*'"
  }
  response_templates = {
    "application/json" = jsonencode(
      { "error" : each.value, "chisel" : "was here", "version" : data.external.poetry_version.result.version }
    )
  }
  depends_on = [data.aws_api_gateway_rest_api.cors_api]
}

resource "aws_api_gateway_stage" "api_stage" {
  stage_name    = terraform.workspace
  rest_api_id   = data.aws_api_gateway_rest_api.cors_api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
  variables = {
    "env"    = terraform.workspace
    "stage"  = terraform.workspace
    "lambda" = local.lambda_stage_function_name
    #"lambda_arn"      = aws_lambda_function.lambda.arn
    "lambda_function" = data.aws_lambda_function.api_render_pdf.arn
  }
}
