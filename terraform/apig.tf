# https://chat.openai.com/c/01aa44ef-597e-4d3e-9284-2da5d3d58646
/*
Create an API Gateway:
Navigate to the API Gateway service in the AWS Management Console.
Create a new REST API.
Create a new resource for the API, e.g., /process.
Add a POST method to the /process resource.
Integrate the POST method with your Lambda function.
*/

# create API gateway
resource "aws_api_gateway_rest_api" "api_botc_json2pdf" {
  name        = "botc-json2pdf"
  description = "API for botc-json2pdf"
}

# add /render
resource "aws_api_gateway_resource" "api_botc_json2pdf_render" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  parent_id   = aws_api_gateway_rest_api.api_botc_json2pdf.root_resource_id
  path_part   = "render"
}

resource "aws_api_gateway_request_validator" "api_render_validator" {
  name                        = "api_render_validator"
  rest_api_id                 = aws_api_gateway_rest_api.api_botc_json2pdf.id
  validate_request_body       = true
  validate_request_parameters = true
}


# CORS
module "cors" {
  source  = "squidfunk/api-gateway-enable-cors/aws"
  version = "0.3.3"

  api_id          = aws_api_gateway_rest_api.api_botc_json2pdf.id
  api_resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id

  allow_headers = [
    "Authorization",
    "Cache-Control",
    "cache-control",
    "Content-Type",
    "X-Amz-Date",
    "X-Amz-Security-Token",
    "X-Api-Key",
    "x-api-key",
    "x-requested-with",
    "access-control-allow-origin",
  ]

  #allow_origin = "https://${var.site_name}.${var.domain_name}"
  #allow_origin = "http://127.0.0.1:5500"
  allow_origin = "*"

  allow_credentials = false
}


resource "aws_api_gateway_deployment" "api_botc_json2pdf_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id

  triggers = {
    redeployment = sha1(jsonencode([
      aws_api_gateway_resource.api_botc_json2pdf_render.id,
      aws_api_gateway_method.api_render_post.id,
      aws_api_gateway_integration.api_render_post_integration.id,

      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_401.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_403.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_500.id,

      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400_forbidden.id,

      aws_api_gateway_method_response.api_botc_json2pdf_method_response_400.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_403.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_500.id,

      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400_forbidden.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_401.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_403.id,
      aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_500.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_400.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_400_forbidden.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_403.id,
      aws_api_gateway_method_response.api_botc_json2pdf_method_response_500.id,
      aws_api_gateway_method_response.api_botc_json2pdf_option_method_response_400.id,
      aws_api_gateway_method_response.api_botc_json2pdf_option_method_response_403.id,
    ]))
  }

  lifecycle {
    create_before_destroy = true
  }
}


resource "aws_api_gateway_stage" "api_botc_json2pdf_stage" {
  stage_name    = terraform.workspace
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  deployment_id = aws_api_gateway_deployment.api_botc_json2pdf_deployment.id
  variables = {
    "env"    = terraform.workspace
    "lambda" = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
  }
}

resource "aws_api_gateway_method_settings" "api_botc_json2pdf_method_settings" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  stage_name  = aws_api_gateway_stage.api_botc_json2pdf_stage.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}

# add a gateway response for a 403
resource "aws_api_gateway_gateway_response" "api_botc_json2pdf_gateway_response_403" {
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  response_type = "ACCESS_DENIED"
  status_code   = "403"
  response_templates = {
    "application/json" = <<EOF
{
    message            = "$context.error.messageString"
    resourcePath       = "$context.resourcePath"
    stage              = "$context.stage"
    "stageVariables.a" = "$stageVariables.a"
    statusCode         = "'404'"
    type               = "$context.error.responseType"
}
EOF
  }

  response_parameters = {
    "gatewayresponse.header.x-request-id" = "method.request.header.x-amzn-RequestId"
  }
}



# add a gateway response for a Missing Authentication Token
resource "aws_api_gateway_gateway_response" "api_botc_json2pdf_gateway_response_401" {
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  response_type = "AUTHORIZER_FAILURE"
  status_code   = "401"
  response_templates = {
    "application/json" = <<EOF
{
  "message": $context.error.messageString,
  "type": $context.error.responseType,
  "stage": "$context.stage",
  "resourcePath": "$context.resourcePath",
  "httpMethod": "$context.httpMethod",
  "requestId": "$context.requestId",
  "resourceId": "$context.resourceId",
  "authorizer": "$context.authorizer",
  "identity": "$context.identity"
}
EOF
  }
}

# add a generic gateway response for a 400
resource "aws_api_gateway_gateway_response" "api_botc_json2pdf_gateway_response_400" {
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  response_type = "INVALID_API_KEY"
  status_code   = "401"
  response_templates = {
    "application/json" = <<EOF
{
  "message": $context.error.messageString,
  "type": $context.error.responseType,
  "stage": "$context.stage",
  "resourcePath": "$context.resourcePath",
  "httpMethod": "$context.httpMethod",
  "requestId": "$context.requestId",
  "resourceId": "$context.resourceId",
  "authorizer": "$context.authorizer",
  "identity": "$context.identity"
}
EOF
  }

  response_parameters = {
    "gatewayresponse.header.x-chisel" = "'my-static-value'"
  }
}

resource "aws_api_gateway_gateway_response" "api_botc_json2pdf_gateway_response_400_forbidden" {
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  response_type = "UNAUTHORIZED"
  status_code   = "401"
  response_templates = {
    "application/json" = <<EOF
{
  "message": $context.error.messageString,
  "type": $context.error.responseType,
  "stage": "$context.stage",
  "resourcePath": "$context.resourcePath",
  "httpMethod": "$context.httpMethod",
  "requestId": "$context.requestId",
  "resourceId": "$context.resourceId",
  "authorizer": "$context.authorizer",
  "identity": "$context.identity"
}
EOF
  }

  response_parameters = {
    "gatewayresponse.header.x-chisel" = "'my-static-value'"
  }
}



# add a generic gateway response for a 500
resource "aws_api_gateway_gateway_response" "api_botc_json2pdf_gateway_response_500" {
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  response_type = "DEFAULT_5XX"
  status_code   = "500"
  response_templates = {
    "application/json" = <<EOF
{
  "message": $context.error.messageString,
  "type": $context.error.responseType
}
EOF
  }
}
