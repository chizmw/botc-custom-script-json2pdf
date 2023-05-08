
# add POST method to /render
resource "aws_api_gateway_method" "api_render_post" {
  rest_api_id          = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id          = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method          = "POST"
  request_validator_id = aws_api_gateway_request_validator.api_render_validator.id
  api_key_required     = true
  authorization        = "NONE"
}

resource "aws_api_gateway_integration" "api_render_post_integration" {
  http_method             = aws_api_gateway_method.api_render_post.http_method
  resource_id             = aws_api_gateway_resource.api_botc_json2pdf_render.id
  rest_api_id             = aws_api_gateway_rest_api.api_botc_json2pdf.id
  type                    = "AWS_PROXY"
  integration_http_method = "POST"
  content_handling        = "CONVERT_TO_TEXT"
  # not idea, but it works .. make it better later
  uri = "arn:aws:apigateway:eu-west-2:lambda:path/2015-03-31/functions/arn:aws:lambda:eu-west-2:436158765452:function:$${stageVariables.lambda}/invocations"
}

locals {
  default_method_response_parameters = {
    "method.response.header.Access-Control-Allow-Origin" = true
    "method.response.header.x-api-key"                   = true
  }
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_method_response_400" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_post.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_method_response_400_forbidden" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_post.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400_forbidden.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_method_response_403" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_post.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_403.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_method_response_500" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_post.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_500.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}
