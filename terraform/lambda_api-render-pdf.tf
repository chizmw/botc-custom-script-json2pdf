module "lambda_function_api-render_pdf" {
  source  = "terraform-aws-modules/lambda/aws"
  version = "6.0.1"

  function_name = "${local.project_name}__${terraform.workspace}__render_handler"
  description   = "Manage the ${local.project_name} lambda function for /render endpoint (${terraform.workspace})"
  handler       = "botcpdf.lambda.render"
  runtime       = "python3.11"
  publish       = true
  timeout       = 30

  source_path = [
    {
      path           = "${path.module}/../lambda-src/api-render-pdf"
      poetry_install = true
    }
  ]

  layers = [
    local.secrets_layer_arn,
  ]

  attach_policy_json = true
  policy_json        = <<EOF
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Sid": "${terraform.workspace}AllowLambdaToUseSecretsLayer",
      "Effect": "Allow",
      "Action": "lambda:GetLayerVersion",
      "Resource": "*"
    },
    {
      "Effect": "Allow",
      "Action": "ssm:GetParameter",
      "Resource": [
          "arn:aws:ssm:*:*:parameter/core_infrastructure/BLAMELESS_API_KEY",
          "arn:aws:ssm:*:*:parameter/core_infrastructure/OPSLEVEL_API_KEY"
      ]
    }
  ]
}
EOF
  allowed_triggers = {
    APIGatewayAny = {
      service    = "apigateway"
      source_arn = "arn:aws:execute-api:${data.aws_region.current.name}:${data.aws_caller_identity.current.account_id}:${aws_api_gateway_rest_api.arcanescripts-api-gateway.id}/*/*/*"
    },
  }

}
