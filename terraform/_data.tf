
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
  function_name = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
}

data "aws_lambda_function" "lambda_invalidate_cache" {
  function_name = "invalidate-cache"
}

data "aws_iam_role" "iam_for_lambda" {
  name = "deploy_json2pdf"
}
