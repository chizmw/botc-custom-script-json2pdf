
output "poetry_version" {
  value = data.external.useful_version_info.result.poetry_version
}

output "commit_version" {
  value = data.external.useful_version_info.result.commit_version
}

output "project_dir" {
  value = data.external.useful_version_info.result.project_dir
}
