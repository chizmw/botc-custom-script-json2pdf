resource "aws_api_gateway_rest_api" "arcanescripts-api-gateway" {
  name        = "arcane-scripts-api-${terraform.workspace}"
  description = "API for arcane-scripts.net (${terraform.workspace})"
  body        = data.template_file.arcanescripts_api_oas3.rendered
}

data "template_file" "arcanescripts_api_oas3" {
  template = file("../openapi/arcanescripts-oas3.yaml")

  vars = {
    get_lambda_arn  = aws_lambda_function.api-render-pdf.arn
    post_lambda_arn = aws_lambda_function.api-render-pdf.arn
  }
}

resource "aws_api_gateway_deployment" "arcanescripts-api-gateway-deployment" {
  rest_api_id       = aws_api_gateway_rest_api.arcanescripts-api-gateway.id
  stage_description = "Deployed at ${timestamp()}"

  triggers = {
    redeployment = sha1(jsonencode(aws_api_gateway_rest_api.arcanescripts-api-gateway.body))
  }
  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_api_gateway_stage" "v1" {
  deployment_id = aws_api_gateway_deployment.arcanescripts-api-gateway-deployment.id
  rest_api_id   = aws_api_gateway_rest_api.arcanescripts-api-gateway.id
  stage_name    = "v1"
}

resource "aws_api_gateway_method_settings" "all" {
  rest_api_id = aws_api_gateway_rest_api.arcanescripts-api-gateway.id
  stage_name  = aws_api_gateway_stage.v1.stage_name
  method_path = "*/*"

  settings {
    metrics_enabled = true
    logging_level   = "ERROR"
  }
}

output "stage_invoke_url" {
  value = aws_api_gateway_stage.v1.invoke_url
}
