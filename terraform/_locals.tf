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
    prod = "make"
    dev  = "beta"
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
  python_runtime             = "python3.10"
  lambda_stage_function_name = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
  xray_tracingenabled        = (terraform.workspace == "prod") ? true : false
}
