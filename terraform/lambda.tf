# lambda itself should be managed by
# infra-arcane-scripts.net/terraform

# # Declare the local zip archive
# data "archive_file" "lambda_code" {
#   type        = "zip"
#   source_file = "./lambda-src/invalidate_cache.py"
#   output_path = "./tmp/invalidatecache.zip"
# }

# data "aws_iam_role" "iam_for_lambda" {
#   name = "deploy_json2pdf"
# }

# resource "aws_lambda_function" "lambda_invalidate_cache" {
#   function_name    = "invalidate-cache"
#   filename         = data.archive_file.lambda_code.output_path
#   source_code_hash = data.archive_file.lambda_code.output_base64sha256
#   role             = data.aws_iam_role.iam_for_lambda.arn
#   handler          = "invalidate_cache.lambda_handler"
#   runtime          = "python3.10"
# }
