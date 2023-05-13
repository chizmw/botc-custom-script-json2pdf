
# the dummy file we used when working through the CORS api
# https://mrponath.medium.com/terraform-and-aws-api-gateway-a137ee48a8ac
data "archive_file" "lambda" {
  type        = "zip"
  source_file = "main.py"
  output_path = "lambda_function_payload.zip"
}

# this allows us to rely on existing information to specify the lambda function name
# supporting serverless config options and terraform workspaces
data "aws_lambda_function" "api_render_pdf" {
  provider      = aws.default
  function_name = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
}

data "aws_lambda_function" "lambda_invalidate_cache" {
  provider      = aws.default
  function_name = "invalidate-cache"
}

data "aws_iam_role" "iam_for_lambda" {
  provider = aws.default
  name     = "deploy_json2pdf"
}


data "aws_lambda_function" "invalidate_cache" {
  provider      = aws.default
  function_name = "invalidate-cache"
}

data "aws_api_gateway_rest_api" "json2pdf_api" {
  provider = aws.default
  name     = local.pdf_api_name
}

data "aws_api_gateway_resource" "json2pdf_resource" {
  provider    = aws.default
  rest_api_id = data.aws_api_gateway_rest_api.json2pdf_api.id
  path        = "/${local.pdf_render_path}"
}
