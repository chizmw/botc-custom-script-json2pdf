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



resource "aws_api_gateway_deployment" "api_botc_json2pdf_deployment" {
  rest_api_id = aws_api_gateway_rest_api.api_botc_json2pdf.id


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
