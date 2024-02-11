locals {
  weasyprint_src_dir    = "../lambda-src/weasyprint-layer"
  weasyprint_package    = "${local.weasyprint_src_dir}/weasyprint_lambda_layer.zip"
  weasyprint_dockerfile = "${local.weasyprint_src_dir}/Dockerfile"
}


module "lambda_layer_weasyprint" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.1"
  runtime = local.python_runtime

  layer_name = "weasyprint-layer"

  create_package  = false # to control build package process
  create_function = false # to control creation of the Lambda Function and related resources
  create_layer    = true  # to control creation of the Lambda Layer and related resources

  local_existing_package = local.weasyprint_package

  depends_on = [
    null_resource.lambda_layer_weasyprint
  ]
}

####
resource "null_resource" "lambda_layer_weasyprint" {
  triggers = {
    requirements = filesha1(local.weasyprint_dockerfile)
  }

  # the command to install python and dependencies to the machine and zips
  provisioner "local-exec" {
    command = <<eot
      set -ev
      cd ${local.weasyprint_src_dir}
      rm -rf *.zip
      sh make-layer-zip.sh
    eot
  }
}
