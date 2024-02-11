provider "docker" {
  registry_auth {
    address  = format("%v.dkr.ecr.%v.amazonaws.com", data.aws_caller_identity.current.account_id, data.aws_region.current.name)
    username = data.aws_ecr_authorization_token.token.user_name
    password = data.aws_ecr_authorization_token.token.password
  }
}
locals {
  apirender_src_dir          = "../lambda-src/api-render-pdf"
  apirender_package          = "api_render_pdf_lambda.zip"
  apirender_poetry_lock_path = "${path.module}/../lambda-src/api-render-pdf/poetry.lock"
  apirender_name             = "${local.project_name}__${terraform.workspace}__render"
}


resource "aws_lambda_function" "api-render-pdf" {
  filename      = local.apirender_package
  function_name = local.apirender_name
  role          = aws_iam_role.api-render-pdf_assume_role_policy.arn
  handler       = "botcpdf.lambda.render"
  runtime       = local.python_runtime
  #source_code_hash = filebase64sha256(local.apirender_package)
  publish     = true
  timeout     = 30
  memory_size = 512

  environment {
    variables = {
      SSM_PARAMETER_STORE = "/arcane-scripts/${terraform.workspace}/"
    }
  }

  layers = [
    local.secrets_layer_arn,
    module.lambda_layer_weasyprint.lambda_layer_arn,
  ]

  depends_on = [
    module.lambda_layer_weasyprint,
    null_resource.api-render-pdf,
  ]
}

resource "null_resource" "api-render-pdf" {
  triggers = {
    requirements = filesha1(local.apirender_poetry_lock_path)
  }

  # the command to install python and dependencies to the machine and zips
  provisioner "local-exec" {
    command = <<EOT
       set -ev
       cd ${local.apirender_src_dir}
       zip -r ${local.apirender_package} -x pycache botcpdf/ data/ templates/ README.md poetry.lock pyproject.toml
     EOT
  }
}



# module "lambda_function_api-render_pdf_x" {
#   source        = "terraform-aws-modules/lambda/aws"
#   version       = "6.0.1"
#   function_name = "${local.project_name}__${terraform.workspace}__render_handler_x"
#   description   = "Manage the ${local.project_name} lambda function for /render endpoint (${terraform.workspace})"
#   handler       = "botcpdf.lambda.render"
#   runtime       = local.python_runtime
#   publish       = true
#   timeout       = 30
#   source_path   = "${path.module}/../lambda-src/api-render-pdf/"
#   create_layer  = false # to control creation of the Lambda Layer and related resources
#   #   #create_package = false # to control build package process

#   layers = [
#     #local.secrets_layer_arn,
#     #module.lambda_layer_weasyprint.lambda_layer_arn,
#   ]

#   #   attach_policy_json = true
#   #   policy_json        = <<EOF
#   # {
#   #   "Version": "2012-10-17",
#   #   "Statement": [
#   #     {
#   #       "Sid": "${terraform.workspace}AllowLambdaToUseSecretsLayer",
#   #       "Effect": "Allow",
#   #       "Action": "lambda:GetLayerVersion",
#   #       "Resource": "*"
#   #     },
#   #     {
#   #       "Effect": "Allow",
#   #       "Action": "ssm:GetParameter",
#   #       "Resource": [
#   #           "arn:aws:ssm:*:*:parameter/core_infrastructure/BLAMELESS_API_KEY",
#   #           "arn:aws:ssm:*:*:parameter/core_infrastructure/OPSLEVEL_API_KEY"
#   #       ]
#   #     }
#   #   ]
#   # }
#   # EOF
#   #   allowed_triggers = {
#   #     APIGatewayAny = {
#   #       service    = "apigateway"
#   #       source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.arcanescripts-api-gateway.id}/*/*/*"
#   #     },
#   #   }

# }

# module "lambda_function_api-render_pdf-debug" {
#   source  = "terraform-aws-modules/lambda/aws"
#   version = "6.0.1"

#   function_name = "${local.project_name}__${terraform.workspace}__render_handler_debug"
#   description   = "Debug the ${local.project_name} lambda function for /render endpoint (${terraform.workspace})"
#   handler       = "botcpdf.debug.lambda.render"
#   runtime       = "python3.11"
#   publish       = true
#   timeout       = 30

#   source_path = "${path.module}/../lambda-src/api-render-pdf/debug"

#   layers = [
#     local.secrets_layer_arn,
#     module.lambda_layer_weasyprint.lambda_layer_arn,
#   ]

#   attach_policy_json = true
#   policy_json        = <<EOF
# {
#   "Version": "2012-10-17",
#   "Statement": [
#     {
#       "Sid": "${terraform.workspace}AllowLambdaToUseSecretsLayerDebug",
#       "Effect": "Allow",
#       "Action": "lambda:GetLayerVersion",
#       "Resource": "*"
#     },
#     {
#       "Effect": "Allow",
#       "Action": "ssm:GetParameter",
#       "Resource": [
#           "arn:aws:ssm:*:*:parameter/core_infrastructure/BLAMELESS_API_KEY",
#           "arn:aws:ssm:*:*:parameter/core_infrastructure/OPSLEVEL_API_KEY"
#       ]
#     }
#   ]
# }
# EOF
#   allowed_triggers = {
#     APIGatewayAny = {
#       service    = "apigateway"
#       source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.arcanescripts-api-gateway.id}/*/*/*"
#     },
#   }

# }

# locals {
#   api_poetry_lock_path        = "${path.module}/../lambda-src/api-render-pdf/poetry.lock"
#   api_requirements_path       = "requirements.txt"
#   api_layer_zip_path          = "api-arcance-script-deps-lambda_layer.zip"
#   api_deps_layer_name         = "${local.project_name}-${terraform.workspace}-deps-layer"
#   lambda_layer_s3_bucket_name = "${data.aws_caller_identity.current.account_id}-lambda-layer-bucket"
# }


# ####
# resource "null_resource" "api_deps_lambda_layer" {
#   triggers = {
#     requirements = filesha1(local.api_poetry_lock_path)
#   }

#   # the command to install python and dependencies to the machine and zips
#   provisioner "local-exec" {
#     command = <<EOT
#       set -ev
#       cd ../lambda-src/api-render-pdf/
#       rm -rf python
#       mkdir python
#       poetry export -f requirements.txt --without-hashes --output ${local.api_requirements_path}
#       pip3 install -r ${local.api_requirements_path} -t python/
#       zip -r ${local.api_layer_zip_path} python/
#     EOT
#   }
# }

# # define existing bucket for storing lambda layers
# resource "aws_s3_bucket" "lambda_layer_bucket" {
#   bucket = local.lambda_layer_s3_bucket_name
# }

# # # upload zip file to s3
# # resource "aws_s3_object" "lambda_layer_zip" {
# #   bucket     = aws_s3_bucket.lambda_layer_bucket.id
# #   key        = "lambda_layers/${local.api_deps_layer_name}/${local.api_layer_zip_path}"
# #   source     = local.api_layer_zip_path
# #   depends_on = [null_resource.api_deps_lambda_layer] # triggered only if the zip file is created
# # }

# # # create lambda layer from s3 object
# # resource "aws_lambda_layer_version" "my-lambda-layer" {
# #   s3_bucket           = aws_s3_bucket.lambda_layer_bucket.id
# #   s3_key              = aws_s3_object.lambda_layer_zip.key
# #   layer_name          = local.api_deps_layer_name
# #   compatible_runtimes = ["python3.11"]
# #   skip_destroy        = true
# #   depends_on          = [aws_s3_object.lambda_layer_zip] # triggered only if the zip file is uploaded to the bucket
# # }
