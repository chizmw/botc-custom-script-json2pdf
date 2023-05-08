# add OPTIONS method to /render
resource "aws_api_gateway_method" "api_render_option" {
  rest_api_id      = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id      = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method      = "OPTIONS"
  api_key_required = false
  authorization    = "NONE"
  # request_validator_id not required for OPTIONS
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_option_method_response_400" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_option.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_400.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}

resource "aws_api_gateway_method_response" "api_botc_json2pdf_option_method_response_403" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id
  resource_id = aws_api_gateway_resource.api_botc_json2pdf_render.id
  http_method = aws_api_gateway_method.api_render_option.http_method
  status_code = aws_api_gateway_gateway_response.api_botc_json2pdf_gateway_response_403.status_code
  response_models = {
    "application/json" = "Error"
  }
  response_parameters = local.default_method_response_parameters
}
