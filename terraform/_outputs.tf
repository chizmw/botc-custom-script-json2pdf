
output "poetry_version" {
  value = data.external.useful_version_info.result.poetry_version
}

output "commit_version" {
  value = data.external.useful_version_info.result.head_sha
}

output "project_dir" {
  value = data.external.useful_version_info.result.project_dir
}

output "stage_function_name" {
  value = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
}

output "stage_url" {
  value = aws_api_gateway_deployment.deployment.invoke_url
}


output "www-a" {
  value = aws_route53_record.wkspc_www-a.fqdn
}
