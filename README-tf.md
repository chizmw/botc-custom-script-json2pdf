## Requirements

| Name | Version |
|------|---------|
| <a name="requirement_terraform"></a> [terraform](#requirement\_terraform) | ~> 1.6 |
| <a name="requirement_aws"></a> [aws](#requirement\_aws) | ~> 5.6 |

## Providers

| Name | Version |
|------|---------|
| <a name="provider_aws"></a> [aws](#provider\_aws) | 5.14.0 |
| <a name="provider_aws.acm_provider"></a> [aws.acm\_provider](#provider\_aws.acm\_provider) | 5.14.0 |
| <a name="provider_external"></a> [external](#provider\_external) | 2.3.1 |
| <a name="provider_template"></a> [template](#provider\_template) | 2.2.0 |

## Modules

| Name | Source | Version |
|------|--------|---------|
| <a name="module_lambda_function_api-render_pdf"></a> [lambda\_function\_api-render\_pdf](#module\_lambda\_function\_api-render\_pdf) | terraform-aws-modules/lambda/aws | 6.0.1 |

## Resources

| Name | Type |
|------|------|
| [aws_api_gateway_deployment.arcanescripts-api-gateway-deployment](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_deployment) | resource |
| [aws_api_gateway_method_settings.all](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_method_settings) | resource |
| [aws_api_gateway_rest_api.arcanescripts-api-gateway](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_rest_api) | resource |
| [aws_api_gateway_stage.v1](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/resources/api_gateway_stage) | resource |
| [aws_acm_certificate.star_domain](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/acm_certificate) | data source |
| [aws_caller_identity.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/caller_identity) | data source |
| [aws_ecr_authorization_token.token](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/ecr_authorization_token) | data source |
| [aws_region.current](https://registry.terraform.io/providers/hashicorp/aws/latest/docs/data-sources/region) | data source |
| [external_external.useful_version_info](https://registry.terraform.io/providers/hashicorp/external/latest/docs/data-sources/external) | data source |
| [template_file.arcanescripts_api_oas3](https://registry.terraform.io/providers/hashicorp/template/latest/docs/data-sources/file) | data source |

## Inputs

| Name | Description | Type | Default | Required |
|------|-------------|------|---------|:--------:|
| <a name="input_aws_region"></a> [aws\_region](#input\_aws\_region) | The AWS region to deploy to. | `string` | `"eu-west-2"` | no |
| <a name="input_common_tags"></a> [common\_tags](#input\_common\_tags) | Common tags you want applied to all components. | `map` | <pre>{<br>  "X-Article": "https://www.alexhyett.com/terraform-s3-static-website-hosting/",<br>  "X-Foo": "botc-www"<br>}</pre> | no |
| <a name="input_domain_name"></a> [domain\_name](#input\_domain\_name) | n/a | `string` | `"arcane-scripts.net"` | no |
| <a name="input_sls_function_name"></a> [sls\_function\_name](#input\_sls\_function\_name) | The name of the serverless function. | `string` | `"render-pdf"` | no |
| <a name="input_sls_service_name"></a> [sls\_service\_name](#input\_sls\_service\_name) | The name of the serverless service. | `string` | `"botc-custom-script-json2pdf"` | no |
| <a name="input_www_bucket_name"></a> [www\_bucket\_name](#input\_www\_bucket\_name) | The name of the bucket without the www. prefix. Normally domain\_name. | `string` | `"arcane-scripts.net"` | no |
| <a name="input_www_domain_name"></a> [www\_domain\_name](#input\_www\_domain\_name) | The domain name for the website. | `string` | `"arcane-scripts.net"` | no |

## Outputs

| Name | Description |
|------|-------------|
| <a name="output_commit_version"></a> [commit\_version](#output\_commit\_version) | n/a |
| <a name="output_poetry_version"></a> [poetry\_version](#output\_poetry\_version) | n/a |
| <a name="output_project_dir"></a> [project\_dir](#output\_project\_dir) | n/a |
| <a name="output_stage_invoke_url"></a> [stage\_invoke\_url](#output\_stage\_invoke\_url) | n/a |
| <a name="output_useful_version_info"></a> [useful\_version\_info](#output\_useful\_version\_info) | n/a |
