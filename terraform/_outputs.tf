
output "poetry_version" {
  value = data.external.poetry_version.result.version
}

output "commit_version" {
  value = data.external.commit_version.result.version
}

output "stage_function_name" {
  value = "${var.sls_service_name}-${terraform.workspace}-${var.sls_function_name}"
}

output "stage_url" {
  value = aws_api_gateway_deployment.deployment.invoke_url
}
