resource "aws_api_gateway_rest_api" "arcanescripts-api-gateway" {
  name        = "arcane-scripts-api"
  description = "API for arcane-scripts.net"
  body        = data.template_file.arcanescripts_api_oas3.rendered
}

data "template_file" "arcanescripts_api_oas3" {
  template = file("../openapi/arcanescripts-oas3.yaml")

  vars = {
    get_lambda_arn  = module.lambda_function_api-status.lambda_function_invoke_arn
    post_lambda_arn = module.lambda_function_api-status.lambda_function_invoke_arn
  }
}

resource "aws_api_gateway_deployment" "arcanescripts-api-gateway-deployment" {
  rest_api_id = aws_api_gateway_rest_api.arcanescripts-api-gateway.id
  stage_name  = "dev"
}

output "url" {
  value = "${aws_api_gateway_deployment.arcanescripts-api-gateway-deployment.invoke_url}/api"
}
