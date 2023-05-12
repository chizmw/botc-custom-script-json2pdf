# https://mrponath.medium.com/terraform-and-aws-api-gateway-a137ee48a8ac
# SETUP and "OPTIONS


# POST method


# a request validator is required for API Gateway to accept the request body

# we can't crteate this nicely and use a data lookup, so we'll have to assume we've created this already, and just use the ID
# resource "aws_api_gateway_request_validator" "request_validator" {
#   provider                    = aws.default
#   name                        = "json2pdf_request_validator-core"
#   rest_api_id                 = data.aws_api_gateway_rest_api.json2pdf_api.id
#   validate_request_body       = true
#   validate_request_parameters = false
# }
locals {
  request_validator_id = "bsnt9c"
}

resource "aws_api_gateway_method" "json2pdf_method" {
  provider             = aws.default
  rest_api_id          = data.aws_api_gateway_rest_api.json2pdf_api.id
  resource_id          = data.aws_api_gateway_resource.json2pdf_resource.id
  http_method          = "POST"
  authorization        = "NONE"
  api_key_required     = true
  request_validator_id = local.request_validator_id
}

resource "aws_api_gateway_method_response" "json2pdf_method_response_200" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.json2pdf_api.id
  resource_id = data.aws_api_gateway_resource.json2pdf_resource.id
  http_method = aws_api_gateway_method.json2pdf_method.http_method
  status_code = "200"
  response_parameters = {
    "method.response.header.Access-Control-Allow-Origin"  = true
    "method.response.header.Access-Control-Allow-Headers" = true
  }
  depends_on = [aws_api_gateway_method.json2pdf_method]
}



resource "aws_api_gateway_integration" "integration" {
  provider                = aws.default
  rest_api_id             = data.aws_api_gateway_rest_api.json2pdf_api.id
  resource_id             = data.aws_api_gateway_resource.json2pdf_resource.id
  http_method             = aws_api_gateway_method.json2pdf_method.http_method
  integration_http_method = "POST"
  type                    = "AWS_PROXY"
  uri                     = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:436158765452:function:$${stageVariables.lambda}/invocations"
  depends_on              = [aws_api_gateway_method.json2pdf_method, data.aws_lambda_function.api_render_pdf]
}


resource "aws_api_gateway_deployment" "deployment" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.json2pdf_api.id
  stage_name  = local.api_stage

  lifecycle {
    create_before_destroy = true
  }

  depends_on = [
    #data.aws_api_gateway_gateway_response.json2pdf_gateway_response,
    aws_api_gateway_integration.integration,
    #aws_api_gateway_integration.options_integration,
    #aws_api_gateway_integration_response.options_integration_response,
    data.external.useful_version_info,
  ]

  triggers = {
    redeployment = sha1(jsonencode([
      #data.aws_api_gateway_gateway_response.json2pdf_gateway_response.id,
      #data.aws_api_gateway_gateway_response.json2pdf_gateway_response.response_templates,
      aws_api_gateway_integration.integration.id,
      aws_api_gateway_integration.integration.uri,
      #aws_api_gateway_integration.options_integration.id,
      #aws_api_gateway_integration_response.options_integration_response.id,
      #aws_api_gateway_integration_response.options_integration_response.response_parameters,
      #aws_api_gateway_integration_response.options_integration_response.response_templates,
      #local.gatewayresponses,
      data.external.useful_version_info.result
    ]))
  }

  variables = {
    #"lambda_arn" = aws_lambda_function.lambda.arn
    "lambda" = local.lambda_stage_function_name
    "stage"  = local.api_stage
  }
}

resource "aws_api_gateway_stage" "api_stage" {
  stage_name    = local.api_stage
  rest_api_id   = data.aws_api_gateway_rest_api.json2pdf_api.id
  deployment_id = aws_api_gateway_deployment.deployment.id
  variables = {
    "env"    = local.api_stage
    "stage"  = local.api_stage
    "lambda" = local.lambda_stage_function_name
    #"lambda_arn"      = aws_lambda_function.lambda.arn
    "lambda_function" = data.aws_lambda_function.api_render_pdf.arn
  }
}

resource "aws_lambda_permission" "apigateway" {
  statement_id  = "AllowExecutionFromAPIGateway-${local.api_stage}"
  action        = "lambda:InvokeFunction"
  function_name = data.aws_lambda_function.api_render_pdf.function_name
  principal     = "apigateway.amazonaws.com"
  source_arn    = "arn:aws:lambda:eu-west-2:436158765452:function:${var.sls_service_name}-${local.api_stage}-${var.sls_function_name}"
}
