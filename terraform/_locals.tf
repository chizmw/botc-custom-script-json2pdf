locals {
  project_name = "arcane-scripts-api"

  aws_default_region = "eu-west-2"

  python_runtime = "python3.11"

  # we want a lookup of region to secrets lambda ARN
  # https://docs.aws.amazon.com/secretsmanager/latest/userguide/retrieving-secrets_lambda.html#retrieving-secrets_lambda_ARNs
  secrets_layer_arns = {
    "eu-west-1" = "arn:aws:lambda:eu-west-1:015030872274:layer:AWS-Parameters-and-Secrets-Lambda-Extension:10"
    "eu-west-2" = "arn:aws:lambda:eu-west-2:133256977650:layer:AWS-Parameters-and-Secrets-Lambda-Extension:10"
  }

  # secret_layer_arn is the lookup for the current region, or a default message of "ARN Missing For Region"
  secrets_layer_arn = lookup(local.secrets_layer_arns, data.aws_region.current.name, "ARN Missing For Region")
}




## ORIGINAL LOCALS - CLEANUP REQUIRED
locals {

  tag_defaults = {
    Owner      = "chisel"
    Product    = "botc-custom-script-json2pdf"
    InfoURL    = "https://github.com/chizmw/botc-custom-script-json2pdf"
    Version    = data.external.useful_version_info.result.poetry_version
    ShaVersion = data.external.useful_version_info.result.commit_version
  }

  # wkspc_site_name is based on the workspace name; if it's 'prod' we use 'make', if it's 'dev' we use 'preview'
  wkspc_site_name = {
    prod    = "make"
    dev     = "beta"
    default = "alpha"
  }

  # get the lookup value from the wkspc_site_name map based on the workspace name
  site_name = lookup(local.wkspc_site_name, terraform.workspace)
}

# used in "a new hope" apigateway
locals {
  pdf_api_name               = "pdf-api"
  pdf_api_description        = "JSON-to-PDF API for custom BotC scripts"
  pdf_render_path            = "render"
  api_stage                  = (terraform.workspace == "prod") ? "prod" : "dev"
  lambda_stage_function_name = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
  xray_tracingenabled        = (terraform.workspace == "prod") ? true : false
}
