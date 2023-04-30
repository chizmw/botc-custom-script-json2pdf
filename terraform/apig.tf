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

# add POST method to /render
resource "aws_api_gateway_method" "api_render_post" {
  rest_api_id          = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id          = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method          = "POST"
  request_validator_id = aws_api_gateway_request_validator.api_render_validator.id
  api_key_required     = true
  authorization        = "NONE"
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
    "x-requested-with",
    "access-control-allow-origin",
  ]

  allow_origin = "https://${var.site_name}.${var.domain_name}"
  #allow_origin = "http://127.0.0.1:5500"

  allow_credentials = false
}

# dev stage
resource "aws_api_gateway_rest_api" "example" {
  body = jsonencode({
    openapi = "3.0.1"
    info = {
      title   = "example"
      version = "1.0"
    }
    paths = {
      "/path1" = {
        get = {
          x-amazon-apigateway-integration = {
            httpMethod           = "GET"
            payloadFormatVersion = "1.0"
            type                 = "HTTP_PROXY"
            uri                  = "https://ip-ranges.amazonaws.com/ip-ranges.json"
          }
        }
      }
    }
  })

  name = "example"
}

resource "aws_api_gateway_deployment" "example" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.api_botc_json2pdf.body))
  }

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "example" {
  deployment_id = aws_api_gateway_deployment.example.id
  rest_api_id   = aws_api_gateway_rest_api.api_botc_json2pdf.id
  stage_name    = "example"
}

resource "aws_api_gateway_method_settings" "example" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  stage_name  = aws_api_gateway_stage.example.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "INFO"
  }
}
